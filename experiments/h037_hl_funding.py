"""H037: divergencia de funding Hyperliquid − Binance como señal contraria (BTC/ETH).

Uso: python3 experiments/h037_hl_funding.py
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
from src.external import fetch_hyperliquid_funding  # noqa: E402

COST = 0.0010
TRAIN = (pd.Timestamp("2023-05-15", tz="UTC"), pd.Timestamp("2024-07-01", tz="UTC"))
OOS_END = pd.Timestamp("2025-10-01", tz="UTC")


def asset(sym, coin, k):
    kl = load_klines("um", sym, "1d")
    kl = kl[(kl.index >= TRAIN[0] - pd.Timedelta("120D")) & (kl.index < OOS_END)]
    hl = fetch_hyperliquid_funding(coin)
    hl_d = hl.groupby(hl.index.floor("1D")).mean().reindex(kl.index) * 8
    bf = load_funding(sym)
    bf_d = (bf.groupby((bf.index - pd.Timedelta("1ns")).floor("1D")).sum() / 3).reindex(kl.index)
    diff = hl_d - bf_d
    z = (diff - diff.shift(1).rolling(90, min_periods=60).mean()) / diff.shift(1).rolling(90, min_periods=60).std()
    sig = (-np.sign(z) * (z.abs() > k)).fillna(0.0)
    pos = sig.shift(1).fillna(0.0)
    ret = kl["open"].shift(-1) / kl["open"] - 1
    fday = bf.groupby((bf.index - pd.Timedelta("1ns")).floor("1D")).sum().reindex(kl.index).fillna(0.0)
    net = pos * ret - pos * fday - pos.diff().abs().fillna(0.0) * COST
    keep = kl.index >= TRAIN[0]
    return net[keep].iloc[:-1], pos[keep].iloc[:-1]


def main():
    res = {}
    for k in (1.5, 2.0):
        parts = [asset("BTCUSDT", "BTC", k), asset("ETHUSDT", "ETH", k)]
        net = pd.concat([p[0] for p in parts], axis=1).mean(axis=1)
        pos = pd.concat([p[1] for p in parts], axis=1)
        for name, sel in (("train", net.index < TRAIN[1]), ("oos", net.index >= TRAIN[1])):
            r = net[sel]
            lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=20, n_boot=5000)
            res[f"k={k}|{name}"] = {"ann": float(r.mean() * 365), "sharpe_m": metrics.sharpe_resampled(r),
                                    "max_dd": metrics.max_drawdown(r.to_numpy()),
                                    "active": float((pos[sel] != 0).mean().mean()),
                                    "ci95_daily": [lo, hi]}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h037.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for kk, v in res.items():
        print(kk, round(v["ann"], 4), round(v["sharpe_m"], 2), round(v["max_dd"], 3),
              "activa", round(v["active"], 2), [round(x, 5) for x in v["ci95_daily"]])


if __name__ == "__main__":
    main()
