"""H024: exposición semanal a BTC/ETH (perps) ∝ c/σ² (realizada 30 d o DVOL).

Uso: python3 experiments/h024_vol_managed.py
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
from src.external import fetch_dvol  # noqa: E402

COST, WMAX = 0.0010, 1.5
TRAIN = (pd.Timestamp("2021-04-01", tz="UTC"), pd.Timestamp("2023-01-01", tz="UTC"))
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def asset(sym, cur, kind):
    k = load_klines("um", sym, "1d")
    k = k[(k.index >= TRAIN[0] - pd.Timedelta("60D")) & (k.index < HOLDOUT)]
    lr = np.log(k["close"]).diff()
    if kind == "rv":
        var = lr.rolling(30, min_periods=25).var()
    else:
        var = (fetch_dvol(cur).reindex(k.index).ffill() / 100) ** 2 / 365
    inv = 1 / var                                        # conocido al close del día
    sunday = k.index.dayofweek == 6
    raw = inv.where(pd.Series(sunday, index=k.index)).ffill()
    c = 1 / raw[(raw.index >= TRAIN[0]) & (raw.index < TRAIN[1])].mean()   # media w = 1 en train
    w = (c * raw).clip(upper=WMAX).fillna(0.0)
    pos = w.shift(1).fillna(0.0)                         # lunes: ejecuta en el open
    ret = k["open"].shift(-1) / k["open"] - 1
    f = load_funding(sym)
    fday = f.groupby((f.index - pd.Timedelta("1ns")).floor("1D")).sum().reindex(k.index).fillna(0.0)
    net = pos * ret - pos * fday - pos.diff().abs().fillna(0.0) * COST
    bh = ret - fday                                      # perp 1x permanente (paga funding)
    keep = k.index >= TRAIN[0]
    return net[keep].iloc[:-1], bh[keep].iloc[:-1], pos[keep].iloc[:-1]


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
    res = {}
    for kind in ("rv", "dvol"):
        parts = [asset("BTCUSDT", "BTC", kind), asset("ETHUSDT", "ETH", kind)]
        net = pd.concat([p[0] for p in parts], axis=1).mean(axis=1)
        bh = pd.concat([p[1] for p in parts], axis=1).mean(axis=1)
        pos = pd.concat([p[2] for p in parts], axis=1).mean(axis=1)
        tr, te = net.index < TRAIN[1], net.index >= TRAIN[1]
        res[kind] = {"train": stats(net[tr], bh[tr]), "oos": stats(net[te], bh[te]),
                     "avg_w_oos": float(pos[te].mean())}
    res["chosen_on_train"] = max(("rv", "dvol"), key=lambda k: res[k]["train"]["sharpe_m"])
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h024.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for k in ("rv", "dvol"):
        for p in ("train", "oos"):
            v = res[k][p]
            print(k, p, "ann", round(v["ann"], 3), "SR", round(v["sharpe_m"], 2), "MDD",
                  round(v["max_dd"], 2), "| B&H", round(v["bh_ann"], 3), round(v["bh_sharpe_m"], 2),
                  round(v["bh_max_dd"], 2), "| alfa", round(v["alpha_ann"], 3), "beta",
                  round(v["beta"], 2), [round(x, 5) for x in v["alpha_ci95_daily"]])
    print("elegida:", res["chosen_on_train"], "w media OOS:", round(res[res["chosen_on_train"]]["avg_w_oos"], 2))


if __name__ == "__main__":
    main()
