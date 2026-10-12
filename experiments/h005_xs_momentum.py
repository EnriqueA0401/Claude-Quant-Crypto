"""H005 · G2: momentum/reversión cross-sectional semanal en perps USDT-M (train 2020–2022).

Uso: python3 experiments/h005_xs_momentum.py   (requiere python3 -m src.universe)
Variantes fijadas en HYPOTHESES.md: L ∈ {1, 2, 4} semanas × {mom, rev}.
Convención: señal con closes hasta el domingo; ejecución en el open del lunes 00:00 UTC;
tenencia hasta el open del lunes siguiente (o último close si el par se deslista).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import metrics  # noqa: E402
from src.data import DATA, load_funding, load_klines  # noqa: E402

PER_SIDE = 0.0005 + 0.0010
N_SIDE, W = 5, 0.5 / 5
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
VARIANTS = [(L, d) for L in (1, 2, 4) for d in ("mom", "rev")]


def panel():
    syms = sorted(p.name for p in (DATA / "futures/um/monthly/klines").iterdir()
                  if (p / "1d").exists())
    o, c, h, qv, fd = {}, {}, {}, {}, {}
    for s in syms:
        k = load_klines("um", s, "1d")
        o[s], c[s], h[s], qv[s] = k["open"], k["close"], k["high"], k["quote_volume"]
        try:
            f = load_funding(s)
            # funding con ts en (open_d, open_{d+1}] asignado al día d
            fd[s] = f.groupby((f.index - pd.Timedelta("1ns")).floor("1D")).sum()
        except FileNotFoundError:
            pass
    P = lambda d: pd.DataFrame(d).sort_index()  # noqa: E731
    return P(o), P(c), P(h), P(qv), P(fd).fillna(0.0)


def run(o, c, h, qv, fd, L, direction, end=None, score_fn=None):
    """score_fn(sun, mon, names) -> Series (mayor = largo). Por defecto, retorno de L
    semanas hasta el close del domingo (momentum)."""
    mondays = o.index[o.index.dayofweek == 0]
    if end is not None:
        mondays = mondays[mondays < end]
    first = o.apply(lambda s: s.first_valid_index())
    vol30 = qv.rolling(30, min_periods=20).sum()
    prev_w = pd.Series(0.0, index=o.columns)
    rows = []
    for i, mon in enumerate(mondays[:-1]):
        sun = mon - pd.Timedelta("1D")
        nxt = mondays[i + 1]
        if sun - pd.Timedelta(weeks=L) not in c.index or sun not in c.index:
            continue
        alive = o.loc[mon].notna() & (first <= sun - pd.Timedelta("90D"))
        liquid = vol30.loc[sun][alive].nlargest(50).index
        if score_fn is None:
            past = c.loc[sun, liquid] / c.loc[sun - pd.Timedelta(weeks=L), liquid] - 1
        else:
            past = score_fn(sun, mon, liquid)
        past = past.dropna()
        if len(past) < 2 * N_SIDE:
            continue
        ranked = past.sort_values()
        top, bot = ranked.index[-N_SIDE:], ranked.index[:N_SIDE]
        longs, shorts = (top, bot) if direction == "mom" else (bot, top)
        w = pd.Series(0.0, index=o.columns)
        w[longs], w[shorts] = W, -W
        week = o.loc[mon:nxt].index[:-1]
        ret = {}
        for s in list(longs) + list(shorts):
            seg_o = o.loc[week, s].dropna()
            p0 = seg_o.iloc[0]
            p1 = o.loc[nxt, s]
            if np.isnan(p1):                       # deslistado en la semana
                p1 = c.loc[week, s].dropna().iloc[-1]
            r = p1 / p0 - 1
            if w[s] < 0 and h.loc[week, s].max() >= 2 * p0:
                r = 1.0                             # corto 1x liquidado: pierde todo
            fsum = fd.loc[week, s].sum() if s in fd.columns else 0.0
            ret[s] = w[s] * r - w[s] * fsum         # largo paga funding positivo
        turnover = (w - prev_w).abs().sum()
        prev_w = w
        rows.append({"week": mon, "gross": sum(ret.values()),
                     "cost": turnover * PER_SIDE, "n_universe": len(past)})
    df = pd.DataFrame(rows).set_index("week")
    df["net"] = df["gross"] - df["cost"]
    return df


def main():
    o, c, h, qv, fd = panel()
    res, series = {}, {}
    for L, d in VARIANTS:
        df = run(o, c, h, qv, fd, L, d, end=TRAIN_END)
        r = df["net"]
        series[f"L={L}|{d}"] = r
        lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=8, n_boot=5000)
        res[f"L={L}|{d}"] = {"weeks": int(len(r)), "ann": float(r.mean() * 52),
                             "sharpe_m": metrics.sharpe_resampled(r),
                             "max_dd": metrics.max_drawdown(r.to_numpy()),
                             "cost_ann": float(df["cost"].mean() * 52),
                             "ci95_weekly": [lo, hi],
                             "median_universe": float(df["n_universe"].median())}
    pd.DataFrame(series).to_csv(ROOT / "reports/h005_g2_weekly.csv")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h005_g2.json").write_text(json.dumps(
        {"commit": commit, "variants": len(VARIANTS), "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.to_string())


if __name__ == "__main__":
    main()
