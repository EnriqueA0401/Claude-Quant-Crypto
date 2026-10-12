"""H012 · G2/G3: basis de futuros trimestrales fijado a la entrada (BTC, ETH).

Uso: python3 experiments/h012_quarterly_basis.py [g3]
Variantes fijadas en HYPOTHESES.md: θ ∈ {0.05, 0.10} × salida ∈ {vencimiento, θ/4}.
Convenciones: barras 1h por open time; decisión al close del bar t, ejecución en el open
de t+1. La posición mantiene unidades fijas desde la entrada (o el último rebalanceo): el bar t
gana W·(ΔS/S_ref − ΔF/F_ref) entre open[t] y open[t+1]; en la última barra del contrato se
usa su close como precio de liquidación (≈ índice).
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
from src.data import DATA, load_klines  # noqa: E402

CS = 0.0010 + 0.0005
CF = 0.0005 + 0.0005
W, BAND, MMR, MIN_DAYS = 0.5, 0.25, 0.005, 14
VARIANTS = [(th, ex) for th in (0.05, 0.10) for ex in ("expiry", "early")]
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")
HPY = 24 * 365


def load(base):
    spot = load_klines("spot", base)[["open", "close"]]
    futs = {}
    for d in sorted((DATA / "futures/um/monthly/klines").glob(f"{base}_*")):
        k = load_klines("um", d.name)[["open", "high", "close"]]
        futs[d.name] = k
    return spot, futs


def run(spot, futs, theta, exit_rule, end=None):
    idx = spot.index if end is None else spot.index[spot.index < end]
    so, sc = spot["open"].reindex(idx).ffill().to_numpy(), spot["close"].reindex(idx).ffill().to_numpy()
    last = {c: f.index[-1] for c, f in futs.items()}
    al = {c: f.reindex(idx) for c, f in futs.items()}
    n = len(idx)
    rows = np.zeros((n, 6))   # pos, basis_pnl, cost, rebalance, liquidated, entry
    cur, ref, s_ref, pos = None, np.nan, np.nan, 0.0
    pending = None            # contrato a abrir en el open del bar siguiente
    exit_next = False
    for t in range(n - 1):
        cost = reb = liq = ent = 0.0
        if pending is not None:                       # entrada en open[t]
            cur, pos, ent = pending, 1.0, 1.0
            ref = al[cur]["open"].iloc[t]
            s_ref = so[t]                           # unidades fijas desde la entrada
            cost += W * (CS + CF)
            pending = None
        if exit_next and pos:                         # salida anticipada en open[t]
            cost += W * (CS + CF)
            pos, cur, exit_next = 0.0, None, False
        pnl = 0.0
        if pos:
            f = al[cur]
            fo, fh = f["open"].iloc[t], f["high"].iloc[t]
            is_last = idx[t] == last[cur]
            f1 = f["close"].iloc[t] if is_last else f["open"].iloc[t + 1]
            if np.isnan(f1):                         # hueco en el futuro: sin cambio
                f1 = fo
            if fh >= ref * (2 - MMR):
                # corto liquidado: se pierde el margen; el spot se vende al mismo nivel
                # (+100 % sobre la referencia como mucho)
                gain_s = min(so[t + 1] - so[t], 2 * s_ref - so[t]) / s_ref
                liq, pnl = 1.0, W * (gain_s - (ref * 2 - fo) / ref)
                pos, cur = 0.0, None
            else:
                # PnL con unidades fijas (W/s_ref unidades de spot, W/ref de futuro)
                pnl = W * ((so[t + 1] - so[t]) / s_ref - (f1 - fo) / ref)
                mv = abs(f1 / ref - 1)
                if mv > BAND:
                    reb, ref, s_ref = W * mv * (CS + CF), f1, so[t + 1]
                if is_last:                           # vencimiento: cierre de ambas patas
                    cost += W * (CS + CF)
                    pos, cur = 0.0, None
        rows[t] = (pos if (pos or liq or ent) else 0.0, pnl, cost, reb, liq, ent)
        # decisiones al close de t (para el open de t+1)
        if pos and exit_rule == "early":
            f = al[cur]
            days = (last[cur] - idx[t]) / pd.Timedelta("1D")
            if days > 0 and (f["close"].iloc[t] / sc[t] - 1) * 365 / days < theta / 4:
                exit_next = True
        if not pos and pending is None:
            best = None
            for c in sorted(futs):
                days = (last[c] - idx[t]) / pd.Timedelta("1D")
                if days >= MIN_DAYS and not np.isnan(al[c]["close"].iloc[t]):
                    best = (c, days)
                    break
            if best:
                c, days = best
                if (al[c]["close"].iloc[t] / sc[t] - 1) * 365 / days > theta:
                    pending = c
    out = pd.DataFrame(rows[:-1], index=idx[:-1],
                       columns=["pos", "basis", "cost", "rebalance", "liquidated", "entry"])
    out["net"] = out["basis"] - out["cost"] - out["rebalance"]
    return out


def summarize(o):
    r = o["net"]
    lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=24 * 60, n_boot=2000)
    tim = float((o["pos"] > 0).mean())
    return {"ann": float(r.mean() * HPY), "sharpe_m": metrics.sharpe_resampled(r),
            "max_dd": metrics.max_drawdown(r.to_numpy()), "entries": int(o["entry"].sum()),
            "time_in_mkt": tim, "ann_on_deployed": float(r.mean() * HPY / max(tim, 1e-9)),
            "liquidations": int(o["liquidated"].sum()), "ci95_hourly": [lo, hi],
            "yearly": {int(y): float(v) for y, v in r.groupby(r.index.year).sum().items()}}


def main(g3=False):
    end = HOLDOUT if g3 else TRAIN_END
    res = {}
    for base in ("BTCUSDT", "ETHUSDT"):
        spot, futs = load(base)
        futs = {c: f for c, f in futs.items() if f.index[-1] < end}   # vencidos antes del corte
        for th, ex in VARIANTS:
            res[f"{base}|theta={th}|{ex}"] = summarize(run(spot, futs, th, ex, end=end))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    name = "h012_dev.json" if g3 else "h012_g2.json"
    (ROOT / "reports" / name).write_text(json.dumps(
        {"commit": commit, "end": str(end), "variants": len(VARIANTS), "results": res},
        indent=1) + "\n")
    print(pd.DataFrame(res).T.drop(columns=["ci95_hourly", "yearly"]).to_string())


if __name__ == "__main__":
    main(g3=len(sys.argv) > 1 and sys.argv[1] == "g3")
