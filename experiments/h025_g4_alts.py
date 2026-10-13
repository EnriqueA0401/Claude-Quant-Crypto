"""H025 · G4: señal VRP de BTC (sin cambios) aplicada a SOL, BNB y XRP (perps), 2023–2025.

Uso: python3 experiments/h025_g4_alts.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from h024_vol_managed import HOLDOUT, TRAIN, stats  # noqa: E402
from src.data import load_funding, load_klines  # noqa: E402
from src.external import fetch_dvol  # noqa: E402

COST = 0.0015


def btc_signal():
    k = load_klines("um", "BTCUSDT", "1d")
    k = k[(k.index >= pd.Timestamp("2021-03-24", tz="UTC")) & (k.index < HOLDOUT)]
    lr = np.log(k["close"]).diff()
    vrp = (fetch_dvol("BTC").reindex(k.index).ffill() / 100) ** 2 - lr.rolling(7, min_periods=6).var() * 365
    wk = vrp[pd.Series(k.index.dayofweek == 6, index=k.index)]
    med = wk.shift(1).rolling(52, min_periods=26).median()
    sig = (wk > med).astype(float).where(med.notna(), 1.0)
    return sig.reindex(k.index).ffill().fillna(1.0)


def main():
    sig = btc_signal()
    nets, bhs, out = [], [], {}
    for sym in ("SOLUSDT", "BNBUSDT", "XRPUSDT"):
        k = load_klines("um", sym, "1d").reindex(sig.index)
        pos = sig.shift(1).fillna(0.0)
        ret = k["open"].shift(-1) / k["open"] - 1
        f = load_funding(sym)
        fday = f.groupby((f.index - pd.Timedelta("1ns")).floor("1D")).sum().reindex(k.index).fillna(0.0)
        net = (pos * ret - pos * fday - pos.diff().abs().fillna(0.0) * COST).iloc[:-1]
        bh = (ret - fday).iloc[:-1]
        te = net.index >= TRAIN[1]
        out[sym] = stats(net[te].fillna(0), bh[te].fillna(0))
        nets.append(net[te].fillna(0))
        bhs.append(bh[te].fillna(0))
    port = stats(pd.concat(nets, axis=1).mean(axis=1), pd.concat(bhs, axis=1).mean(axis=1))
    (ROOT / "reports/h025_g4_alts.json").write_text(json.dumps({"portfolio": port, "per_asset": out},
                                                                indent=1) + "\n")
    for k, v in list(out.items()) + [("CARTERA", port)]:
        print(k, "ann", round(v["ann"], 3), "SR", round(v["sharpe_m"], 2), "| B&H", round(v["bh_ann"], 3),
              round(v["bh_sharpe_m"], 2), "| alfa", round(v["alpha_ann"], 3), "beta", round(v["beta"], 2),
              [round(x, 5) for x in v["alpha_ci95_daily"]])


if __name__ == "__main__":
    main()
