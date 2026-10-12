"""H011 · G2: cash-and-carry en altcoins (largo spot + corto perp), cartera semanal.

Uso: python3 experiments/h011_alt_carry.py   (requiere klines spot 1d: src.universe)
Variantes fijadas en HYPOTHESES.md: D ∈ {3, 7} × θ ∈ {None, 3e-4}. Train 2020–2022.
Convención: selección con funding de [lunes − D, lunes); ejecución en el open del lunes
(ambas patas); salida en el open del lunes siguiente.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from src import metrics  # noqa: E402
from src.data import DATA, load_funding, load_klines  # noqa: E402

SPOT_SIDE = 0.0010 + 0.0010
PERP_SIDE = 0.0005 + 0.0010
N, W = 5, 0.1
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
VARIANTS = [(d, th) for d in (3, 7) for th in (None, 3e-4)]


def panels():
    perp_syms = sorted(p.name for p in (DATA / "futures/um/monthly/klines").iterdir()
                       if (p / "1d").exists())
    spot_dir = DATA / "spot/monthly/klines"
    po, pc, ph, qv, so, sc, ev = {}, {}, {}, {}, {}, {}, {}
    for s in perp_syms:
        if not (spot_dir / s / "1d").exists():
            continue
        k = load_klines("um", s, "1d")
        sp = load_klines("spot", s, "1d")
        # volumen 0 = suspendido/deslistado con precio plano: no operable
        k.loc[k["quote_volume"] <= 0, ["open", "close", "high"]] = np.nan
        sp.loc[sp["quote_volume"] <= 0, ["open", "close"]] = np.nan
        po[s], pc[s], ph[s], qv[s] = k["open"], k["close"], k["high"], k["quote_volume"]
        so[s], sc[s] = sp["open"], sp["close"]
        try:
            ev[s] = load_funding(s)
        except FileNotFoundError:
            pass
    P = lambda d: pd.DataFrame(d).sort_index()  # noqa: E731
    return P(po), P(pc), P(ph), P(qv), P(so), P(sc), ev


def _exit_price(o, c, week, nxt, s):
    p1 = o.loc[nxt, s] if nxt in o.index else np.nan
    if np.isnan(p1):
        seg = c.loc[week, s].dropna()
        p1 = seg.iloc[-1] if len(seg) else np.nan
    return p1


def run(po, pc, ph, qv, so, sc, ev, D, theta, end=None):
    mondays = po.index[po.index.dayofweek == 0]
    if end is not None:
        mondays = mondays[mondays < end]
    first_p = po.apply(lambda x: x.first_valid_index())
    first_s = so.apply(lambda x: x.first_valid_index())
    vol30 = qv.rolling(30, min_periods=20).sum()
    held, rows = set(), []
    for i, mon in enumerate(mondays[:-1]):
        sun, nxt = mon - pd.Timedelta("1D"), mondays[i + 1]
        if sun not in vol30.index:
            continue
        ok = (po.loc[mon].notna() & so.reindex(columns=po.columns).loc[mon].notna()
              & (first_p <= sun - pd.Timedelta("90D"))
              & (first_s.reindex(po.columns) <= sun - pd.Timedelta("90D")))
        liquid = vol30.loc[sun][ok].nlargest(50).index
        score = {}
        for s in liquid:
            f = ev.get(s)
            if f is None:
                continue
            w = f[(f.index >= mon - pd.Timedelta(days=D)) & (f.index < mon)]
            if len(w):
                score[s] = w.sum() / (D * 3)   # equivalente 8 h (pares con funding 4 h/1 h)
        sc_ = pd.Series(score, dtype=float)
        key = pd.DataFrame({"v": -sc_.round(10).to_numpy(), "n": sc_.index}, index=sc_.index)
        sc_ = sc_.loc[key.sort_values(["v", "n"], kind="mergesort").index]  # empates por nombre
        if theta is not None:
            sc_ = sc_[sc_ > theta]
        new = set(sc_.index[:N])
        changes = len(new ^ held)
        cost = changes * W * (SPOT_SIDE + PERP_SIDE)
        week = po.loc[mon:nxt].index[:-1]
        pnl_basis = pnl_fund = 0.0
        liq = 0
        for s in new:
            p0, s0 = po.loc[mon, s], so.loc[mon, s]
            p1 = _exit_price(po, pc, week, nxt, s)
            s1 = _exit_price(so, sc, week, nxt, s)
            rs = s1 / s0 - 1 if not np.isnan(s1) else 0.0
            if ph.loc[week, s].max() >= 2 * p0:
                rp_short, liq = -1.0, liq + 1
            else:
                rp_short = -(p1 / p0 - 1)
            f = ev.get(s)
            fs = 0.0
            if f is not None:
                fs = f[(f.index > mon) & (f.index <= week[-1] + pd.Timedelta("1D"))].sum()
            pnl_basis += W * (rs + rp_short)
            pnl_fund += W * fs
        rows.append({"week": mon, "n": len(new), "basis": pnl_basis, "funding": pnl_fund,
                     "cost": cost, "changes": changes, "liquidations": liq})
        held = new
    df = pd.DataFrame(rows).set_index("week")
    df["net"] = df["basis"] + df["funding"] - df["cost"]
    return df


def main():
    P = panels()
    res, series = {}, {}
    for d, th in VARIANTS:
        df = run(*P, d, th, end=TRAIN_END)
        key = f"D={d}|theta={th}"
        r = df["net"]
        series[key] = r
        lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=8, n_boot=5000)
        res[key] = {"weeks": int(len(r)), "ann": float(r.mean() * 52),
                    "funding_ann": float(df["funding"].mean() * 52),
                    "basis_ann": float(df["basis"].mean() * 52),
                    "cost_ann": float(df["cost"].mean() * 52),
                    "sharpe_m": metrics.sharpe_resampled(r),
                    "max_dd": metrics.max_drawdown(r.to_numpy()),
                    "entries": int(df["changes"].sum() // 2 + df["n"].iloc[-1] // 2),
                    "avg_pairs": float(df["n"].mean()),
                    "liquidations": int(df["liquidations"].sum()), "ci95_weekly": [lo, hi]}
    pd.DataFrame(series).to_csv(ROOT / "reports/h011_g2_weekly.csv")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h011_g2.json").write_text(json.dumps(
        {"commit": commit, "variants": len(VARIANTS), "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.to_string())


if __name__ == "__main__":
    main()
