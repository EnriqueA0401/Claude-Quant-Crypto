"""H027: largo spot BTC/ETH salvo cuando el MVRV supera su percentil p de 730 días.

Uso: python3 experiments/h027_mvrv.py
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
from src.data import load_klines  # noqa: E402
from src.external import fetch_coinmetrics  # noqa: E402

COST = 0.0015
START = pd.Timestamp("2020-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def mvrv_signal(mvrv: pd.Series, p: float) -> pd.Series:
    """1 = largo; 0 si MVRV_d > percentil p de los 730 días previos (estricto, solo pasado)."""
    thr = mvrv.shift(1).rolling(730, min_periods=365).quantile(p)
    return (~(mvrv > thr)).astype(float).where(thr.notna(), 1.0)


def asset(sym, cm_asset, p):
    mv = fetch_coinmetrics(cm_asset, ["CapMVRVCur"])["CapMVRVCur"]
    k = load_klines("spot", sym, "1d")
    k = k[(k.index >= START) & (k.index < HOLDOUT)]
    sig = mvrv_signal(mv, p).reindex(k.index).fillna(1.0)
    pos = sig.shift(1).fillna(0.0)
    ret = k["open"].shift(-1) / k["open"] - 1
    net = pos * ret - pos.diff().abs().fillna(pos.iloc[0]) * COST
    return net.iloc[:-1], ret.iloc[:-1], pos.iloc[:-1]


def main():
    res = {}
    for p in (0.8, 0.9):
        parts = [asset("BTCUSDT", "btc", p), asset("ETHUSDT", "eth", p)]
        net = pd.concat([x[0] for x in parts], axis=1).mean(axis=1)
        bh = pd.concat([x[1] for x in parts], axis=1).mean(axis=1)
        pos = pd.concat([x[2] for x in parts], axis=1).mean(axis=1)
        tr, te = net.index < TRAIN_END, net.index >= TRAIN_END
        res[f"p={p}"] = {"train": stats(net[tr], bh[tr]), "oos": stats(net[te], bh[te]),
                         "exposure_oos": float(pos[te].mean()),
                         "switches_oos": int((pos[te].diff().abs() > 0).sum())}
    res["chosen_on_train"] = max(("p=0.8", "p=0.9"), key=lambda x: res[x]["train"]["sharpe_m"])
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h027.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for k in ("p=0.8", "p=0.9"):
        for part in ("train", "oos"):
            v = res[k][part]
            print(k, part, "ann", round(v["ann"], 3), "SR", round(v["sharpe_m"], 2), "MDD",
                  round(v["max_dd"], 2), "| B&H", round(v["bh_ann"], 3), round(v["bh_sharpe_m"], 2),
                  round(v["bh_max_dd"], 2), "| alfa", round(v["alpha_ann"], 3), "beta",
                  round(v["beta"], 2), [round(x, 5) for x in v["alpha_ci95_daily"]])
    print("elegida:", res["chosen_on_train"], "exposición/cambios OOS:",
          round(res[res["chosen_on_train"]]["exposure_oos"], 2), res[res["chosen_on_train"]]["switches_oos"])


if __name__ == "__main__":
    main()
