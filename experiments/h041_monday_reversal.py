"""H041: reversión del lunes tras el movimiento del fin de semana (BTC/ETH perps).

Uso: python3 experiments/h041_monday_reversal.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import load_klines  # noqa: E402

COST = 2 * 0.0010
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def main():
    res = {}
    for m in (0.0, 0.05):
        rows = []
        for sym in ("BTCUSDT", "ETHUSDT"):
            k = load_klines("um", sym, "1d")
            k = k[k.index < HOLDOUT]
            for mon in k.index[k.index.dayofweek == 0]:
                sat = mon - pd.Timedelta("2D")
                if sat not in k.index:
                    continue
                wk = k.loc[mon, "open"] / k.loc[sat, "open"] - 1     # conocido en el open del lunes
                if abs(wk) <= m or wk == 0:
                    continue
                r = k.loc[mon, "close"] / k.loc[mon, "open"] - 1
                rows.append({"mon": mon, "gross": -np.sign(wk) * r})
        d = pd.DataFrame(rows).set_index("mon")
        d["net"] = d["gross"] - COST
        for name, x in (("train", d[d.index < TRAIN_END]), ("oos", d[d.index >= TRAIN_END])):
            res[f"m={m}|{name}"] = {"n": int(len(x)), "mean_gross": float(x["gross"].mean()),
                                    "t_gross": float(x["gross"].mean() / (x["gross"].std(ddof=1) / np.sqrt(len(x)))),
                                    "mean_net": float(x["net"].mean())}
    (ROOT / "reports/h041.json").write_text(json.dumps(res, indent=1) + "\n")
    print(pd.DataFrame(res).T.round(5).to_string())


if __name__ == "__main__":
    main()
