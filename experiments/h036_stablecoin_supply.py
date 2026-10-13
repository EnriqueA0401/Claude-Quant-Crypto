"""H036: largo BTC/ETH (perp) solo si la oferta de stablecoins USD creció en D días.

Uso: python3 experiments/h036_stablecoin_supply.py
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from h024_vol_managed import stats  # noqa: E402
from src.data import load_funding, load_klines  # noqa: E402
from src.external import fetch_stablecoin_supply  # noqa: E402

COST = 0.0010
START = pd.Timestamp("2020-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def asset(sym, supply, d):
    k = load_klines("um", sym, "1d")
    k = k[(k.index >= START) & (k.index < HOLDOUT)]
    sup = supply.reindex(k.index).ffill()
    sig = (sup / sup.shift(d) - 1 > 0).astype(float)          # conocido al close de d
    pos = sig.shift(1).fillna(0.0)
    ret = k["open"].shift(-1) / k["open"] - 1
    f = load_funding(sym)
    fday = f.groupby((f.index - pd.Timedelta("1ns")).floor("1D")).sum().reindex(k.index).fillna(0.0)
    net = pos * ret - pos * fday - pos.diff().abs().fillna(0.0) * COST
    return net.iloc[:-1], (ret - fday).iloc[:-1], pos.iloc[:-1]


def main():
    supply = fetch_stablecoin_supply()
    res = {}
    for d in (7, 30):
        parts = [asset("BTCUSDT", supply, d), asset("ETHUSDT", supply, d)]
        net = pd.concat([p[0] for p in parts], axis=1).mean(axis=1)
        bh = pd.concat([p[1] for p in parts], axis=1).mean(axis=1)
        pos = pd.concat([p[2] for p in parts], axis=1).mean(axis=1)
        tr, te = net.index < TRAIN_END, net.index >= TRAIN_END
        res[f"D={d}"] = {"train": stats(net[tr], bh[tr]), "oos": stats(net[te], bh[te]),
                         "exposure_oos": float(pos[te].mean())}
    res["chosen_on_train"] = max(("D=7", "D=30"), key=lambda x: res[x]["train"]["sharpe_m"])
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h036.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for k in ("D=7", "D=30"):
        for p in ("train", "oos"):
            v = res[k][p]
            print(k, p, "ann", round(v["ann"], 3), "SR", round(v["sharpe_m"], 2), "MDD",
                  round(v["max_dd"], 2), "| B&H", round(v["bh_ann"], 3), round(v["bh_sharpe_m"], 2),
                  "| alfa", round(v["alpha_ann"], 3), "beta", round(v["beta"], 2),
                  [round(x, 5) for x in v["alpha_ci95_daily"]])
    print("elegida:", res["chosen_on_train"], "exposición OOS:", round(res[res["chosen_on_train"]]["exposure_oos"], 2))


if __name__ == "__main__":
    main()
