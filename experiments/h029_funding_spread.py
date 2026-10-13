"""H029: diferencial de funding BTC vs ETH, posición neutral semanal.

Uso: python3 experiments/h029_funding_spread.py
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

W, SIDE = 0.5, 0.0010
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def main():
    k = {s: load_klines("um", s, "1d") for s in ("BTCUSDT", "ETHUSDT")}
    f = {s: load_funding(s) for s in k}
    idx = k["BTCUSDT"].index.intersection(k["ETHUSDT"].index)
    idx = idx[idx < HOLDOUT]
    mons = idx[idx.dayofweek == 0]
    res = {}
    for d in (0.5e-4, 1e-4):
        rows, prev = [], (0.0, 0.0)
        for i, mon in enumerate(mons[:-1]):
            nxt = mons[i + 1]
            m = {s: f[s][(f[s].index >= mon - pd.Timedelta("7D")) & (f[s].index < mon)].sum() / 21
                 for s in k}
            diff = m["ETHUSDT"] - m["BTCUSDT"]
            if abs(diff) > d:
                w = (W, -W) if diff < 0 else (-W, W)      # (ETH, BTC): corto el caro
            else:
                w = (0.0, 0.0)
            pnl = 0.0
            for wi, s in zip(w, ("ETHUSDT", "BTCUSDT")):
                if wi:
                    r = k[s].loc[nxt, "open"] / k[s].loc[mon, "open"] - 1
                    fs = f[s][(f[s].index > mon) & (f[s].index <= nxt)].sum()
                    pnl += wi * r - wi * fs
            cost = (abs(w[0] - prev[0]) + abs(w[1] - prev[1])) * SIDE
            rows.append({"week": mon, "net": pnl - cost, "active": w != (0.0, 0.0)})
            prev = w
        df = pd.DataFrame(rows).set_index("week")
        for part, sel in (("train", df.index < TRAIN_END), ("oos", df.index >= TRAIN_END)):
            r = df.loc[sel, "net"]
            lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=8, n_boot=5000)
            res[f"d={d}|{part}"] = {"ann": float(r.mean() * 52), "sharpe_m": metrics.sharpe_resampled(r),
                                    "max_dd": metrics.max_drawdown(r.to_numpy()),
                                    "active": float(df.loc[sel, "active"].mean()), "ci95_weekly": [lo, hi]}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h029.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for kk, v in res.items():
        print(kk, round(v["ann"], 4), round(v["sharpe_m"], 2), round(v["max_dd"], 3),
              "activa", round(v["active"], 2), [round(x, 5) for x in v["ci95_weekly"]])


if __name__ == "__main__":
    main()
