"""H026: fuera del mercado 7 días tras una entrada neta anómala a exchanges (BTC/ETH).

Uso: python3 experiments/h026_exchange_flows.py
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
from h024_vol_managed import stats  # noqa: E402
from src.data import load_funding, load_klines  # noqa: E402
from src.external import fetch_coinmetrics  # noqa: E402

COST, OFF_DAYS = 0.0010, 7
START_TRAIN = pd.Timestamp("2020-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def flow_signal(net: pd.Series, k: float) -> pd.Series:
    """1 = largo. z_d con los 90 días previos; z_d > k → 0 en d..d+6 (posición d+1..d+7)."""
    z = (net - net.shift(1).rolling(90, min_periods=60).mean()) / net.shift(1).rolling(90, min_periods=60).std()
    trig = (z > k).to_numpy()
    sig = np.ones(len(net))
    for i in np.flatnonzero(trig):
        sig[i:i + OFF_DAYS] = 0.0
    return pd.Series(sig, index=net.index)


def asset(sym, cm_asset, k):
    cm = fetch_coinmetrics(cm_asset, ["FlowInExNtv", "FlowOutExNtv", "SplyExNtv"])
    net = (cm["FlowInExNtv"] - cm["FlowOutExNtv"]) / cm["SplyExNtv"]
    kl = load_klines("um", sym, "1d")
    kl = kl[(kl.index >= START_TRAIN) & (kl.index < HOLDOUT)]
    sig = flow_signal(net, k).reindex(kl.index).fillna(1.0)
    pos = sig.shift(1).fillna(0.0)
    ret = kl["open"].shift(-1) / kl["open"] - 1
    f = load_funding(sym)
    fday = f.groupby((f.index - pd.Timedelta("1ns")).floor("1D")).sum().reindex(kl.index).fillna(0.0)
    netr = pos * ret - pos * fday - pos.diff().abs().fillna(0.0) * COST
    return netr.iloc[:-1], (ret - fday).iloc[:-1], pos.iloc[:-1]


def main():
    res = {}
    for k in (1.5, 2.0):
        parts = [asset("BTCUSDT", "btc", k), asset("ETHUSDT", "eth", k)]
        net = pd.concat([p[0] for p in parts], axis=1).mean(axis=1)
        bh = pd.concat([p[1] for p in parts], axis=1).mean(axis=1)
        pos = pd.concat([p[2] for p in parts], axis=1).mean(axis=1)
        tr, te = net.index < TRAIN_END, net.index >= TRAIN_END
        res[f"k={k}"] = {"train": stats(net[tr], bh[tr]), "oos": stats(net[te], bh[te]),
                         "exposure_oos": float(pos[te].mean())}
    res["chosen_on_train"] = max(("k=1.5", "k=2.0"), key=lambda x: res[x]["train"]["sharpe_m"])
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h026.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for k in ("k=1.5", "k=2.0"):
        for p in ("train", "oos"):
            v = res[k][p]
            print(k, p, "ann", round(v["ann"], 3), "SR", round(v["sharpe_m"], 2), "MDD",
                  round(v["max_dd"], 2), "| B&H", round(v["bh_ann"], 3), round(v["bh_sharpe_m"], 2),
                  "| alfa", round(v["alpha_ann"], 3), "beta", round(v["beta"], 2),
                  [round(x, 5) for x in v["alpha_ci95_daily"]])
    print("elegida:", res["chosen_on_train"])


if __name__ == "__main__":
    main()
