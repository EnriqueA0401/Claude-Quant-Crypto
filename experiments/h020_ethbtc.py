"""H020: reversión del ratio ETH/BTC (perps, neutral 0,5 por pata), barras diarias.

Uso: python3 experiments/h020_ethbtc.py
Variantes fijadas en HYPOTHESES.md: k ∈ {2, 2.5}; salida al cruzar z = 0 o a 30 días.
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
from src.data import load_funding, load_klines  # noqa: E402

W, SIDE = 0.5, 0.0005 + 0.0005
MAXD = 30
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def zscore(ce, cb, win=90):
    r = np.log(ce / cb)
    mu = r.shift(1).rolling(win, min_periods=win).mean()
    sd = r.shift(1).rolling(win, min_periods=win).std()
    return (r - mu) / sd


def run(oe, ob, z, fe, fb, k):
    """side = +1 largo ETH/corto BTC; decisión al close de d, ejecución en el open d+1."""
    n = len(oe)
    rows = np.zeros((n - 1, 4))      # side, pnl, cost, entry
    side, age, pending = 0, 0, None
    for t in range(n - 1):
        cost = ent = 0.0
        if pending is not None:
            if pending == 0:
                cost += 2 * W * SIDE          # salida: 2 patas × W × coste por lado
            else:
                cost += 2 * W * SIDE
                ent = 1.0
            side, age, pending = pending, 0, None
        pnl = 0.0
        if side:
            re = oe[t + 1] / oe[t] - 1
            rb = ob[t + 1] / ob[t] - 1
            pnl = W * side * (re - rb) - W * side * fe[t] + W * side * fb[t]
            age += 1
        rows[t] = (side, pnl, cost, ent)
        zt = z[t]
        if side and (np.sign(zt) == side or age >= MAXD):   # cruzó 0 o caducó
            pending = 0
        elif not side and not np.isnan(zt) and abs(zt) >= k:
            pending = -int(np.sign(zt))     # z alto (ETH caro) → corto ETH
    return rows


def main():
    e = load_klines("um", "ETHUSDT", "1d")
    b = load_klines("um", "BTCUSDT", "1d")
    idx = e.index.intersection(b.index)
    idx = idx[idx < HOLDOUT]
    e, b = e.reindex(idx), b.reindex(idx)
    z = zscore(e["close"], b["close"]).to_numpy()

    def fday(sym):
        f = load_funding(sym)
        return f.groupby((f.index - pd.Timedelta("1ns")).floor("1D")).sum().reindex(idx).fillna(0).to_numpy()

    fe, fb = fday("ETHUSDT"), fday("BTCUSDT")
    res = {}
    for k in (2.0, 2.5):
        rows = run(e["open"].to_numpy(), b["open"].to_numpy(), z, fe, fb, k)
        df = pd.DataFrame(rows, index=idx[:-1], columns=["side", "pnl", "cost", "entry"])
        df["net"] = df["pnl"] - df["cost"]
        for name, part in (("train", df[df.index < TRAIN_END]), ("oos", df[df.index >= TRAIN_END])):
            r = part["net"]
            lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=30, n_boot=5000)
            res[f"k={k}|{name}"] = {"entries": int(part["entry"].sum()), "ann": float(r.mean() * 365),
                                    "sharpe_m": metrics.sharpe_resampled(r),
                                    "max_dd": metrics.max_drawdown(r.to_numpy()),
                                    "time_in_mkt": float((part["side"] != 0).mean()),
                                    "ci95_daily": [lo, hi]}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h020.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    print(pd.DataFrame(res).T.to_string())


if __name__ == "__main__":
    main()
