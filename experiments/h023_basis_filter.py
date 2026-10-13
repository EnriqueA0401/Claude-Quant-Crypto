"""H023: largo spot BTC/ETH solo cuando el basis trimestral anualizado < b.

Uso: python3 experiments/h023_basis_filter.py
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
import h012_quarterly_basis as h12  # noqa: E402
from src import metrics  # noqa: E402
from src.data import load_klines  # noqa: E402

COST = 0.0015
START = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def daily_basis(base):
    spot, futs = h12.load(base)
    days = pd.date_range(pd.Timestamp("2021-01-01", tz="UTC"), HOLDOUT - pd.Timedelta("1D"),
                         freq="1D")
    sc = spot["close"]
    out = pd.Series(np.nan, index=days)
    for d in days:
        t = d + pd.Timedelta("23h")                      # último bar 1h del día
        for c in sorted(futs):
            f = futs[c]
            left = (f.index[-1] - t) / pd.Timedelta("1D")
            if left >= 14 and t in f.index and not np.isnan(f.loc[t, "close"]) and t in sc.index:
                out[d] = (f.loc[t, "close"] / sc.loc[t] - 1) * 365 / left
                break
    return out


def backtest(base, basis, b):
    k = load_klines("spot", base, "1d").reindex(basis.index)
    sig = (basis < b).astype(float).where(basis.notna(), 0.0)
    pos = sig.shift(1).fillna(0.0)                       # decide al close, opera en el open
    ret = k["open"].shift(-1) / k["open"] - 1
    net = pos * ret - pos.diff().abs().fillna(pos.iloc[0]) * COST
    return net.iloc[:-1], ret.iloc[:-1], pos.iloc[:-1]


def stats(r, bh):
    X = np.c_[np.ones(len(r)), bh.to_numpy()]
    beta = np.linalg.lstsq(X, r.to_numpy(), rcond=None)[0]
    resid = r.to_numpy() - X @ beta
    lo, hi = metrics.block_bootstrap_mean_ci(resid + beta[0], block=30, n_boot=5000)
    return {"ann": float(r.mean() * 365), "sharpe_m": metrics.sharpe_resampled(r),
            "max_dd": metrics.max_drawdown(r.to_numpy()), "alpha_ann": float(beta[0] * 365),
            "beta": float(beta[1]), "alpha_ci95_daily": [lo, hi],
            "bh_ann": float(bh.mean() * 365), "bh_sharpe_m": metrics.sharpe_resampled(bh),
            "bh_max_dd": metrics.max_drawdown(bh.to_numpy())}


def main():
    bases = {b: daily_basis(b) for b in ("BTCUSDT", "ETHUSDT")}
    res = {}
    for thr in (0.10, 0.15):
        parts = [backtest(b, s, thr) for b, s in bases.items()]
        net = pd.concat([p[0] for p in parts], axis=1).mean(axis=1)
        bh = pd.concat([p[1] for p in parts], axis=1).mean(axis=1)
        expo = pd.concat([p[2] for p in parts], axis=1).mean(axis=1)
        res[f"b={thr}"] = {"train": stats(net[net.index < START], bh[bh.index < START]),
                           "oos": stats(net[net.index >= START], bh[bh.index >= START]),
                           "exposure_oos": float(expo[expo.index >= START].mean())}
    best = max(res, key=lambda k: res[k]["train"]["sharpe_m"])
    res["chosen_on_train"] = best
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h023.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1, default=float) + "\n")
    for k in ("b=0.1", "b=0.15"):
        for p in ("train", "oos"):
            v = res[k][p]
            print(k, p, "ann", round(v["ann"], 3), "SR", round(v["sharpe_m"], 2), "MDD",
                  round(v["max_dd"], 2), "| B&H", round(v["bh_ann"], 3), round(v["bh_sharpe_m"], 2),
                  round(v["bh_max_dd"], 2), "| alfa", round(v["alpha_ann"], 3), "beta",
                  round(v["beta"], 2), [round(x, 5) for x in v["alpha_ci95_daily"]])
    print("elegida:", best, "exposición OOS:", round(res[best]["exposure_oos"], 2))


if __name__ == "__main__":
    main()
