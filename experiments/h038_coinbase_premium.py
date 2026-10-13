"""H038: largo BTC (perp Binance) solo si la prima de Coinbase supera su media de W días.

Uso: python3 experiments/h038_coinbase_premium.py
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
from src.external import fetch_coinbase_daily  # noqa: E402

COST = 0.0010
START = pd.Timestamp("2020-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def main():
    cb = fetch_coinbase_daily()
    k = load_klines("um", "BTCUSDT", "1d")
    k = k[(k.index >= START - pd.Timedelta("40D")) & (k.index < HOLDOUT)]
    spot = load_klines("spot", "BTCUSDT", "1d")["close"].reindex(k.index)
    prem = cb.reindex(k.index) / spot - 1
    f = load_funding("BTCUSDT")
    fday = f.groupby((f.index - pd.Timedelta("1ns")).floor("1D")).sum().reindex(k.index).fillna(0.0)
    ret = k["open"].shift(-1) / k["open"] - 1
    res = {}
    for w in (7, 30):
        sig = (prem > prem.shift(1).rolling(w, min_periods=w // 2).mean()).astype(float)
        pos = sig.shift(1).fillna(0.0)
        net = (pos * ret - pos * fday - pos.diff().abs().fillna(0.0) * COST).iloc[:-1]
        bh = (ret - fday).iloc[:-1]
        keep = net.index >= START
        net, bh = net[keep], bh[keep]
        tr, te = net.index < TRAIN_END, net.index >= TRAIN_END
        res[f"W={w}"] = {"train": stats(net[tr], bh[tr]), "oos": stats(net[te], bh[te]),
                         "exposure_oos": float(pos[pos.index >= TRAIN_END].mean())}
    res["chosen_on_train"] = max(("W=7", "W=30"), key=lambda x: res[x]["train"]["sharpe_m"])
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h038.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for kk in ("W=7", "W=30"):
        for p in ("train", "oos"):
            v = res[kk][p]
            print(kk, p, "ann", round(v["ann"], 3), "SR", round(v["sharpe_m"], 2), "MDD",
                  round(v["max_dd"], 2), "| B&H", round(v["bh_ann"], 3), round(v["bh_sharpe_m"], 2),
                  "| alfa", round(v["alpha_ann"], 3), "beta", round(v["beta"], 2),
                  [round(x, 5) for x in v["alpha_ci95_daily"]])
    print("elegida:", res["chosen_on_train"])


if __name__ == "__main__":
    main()
