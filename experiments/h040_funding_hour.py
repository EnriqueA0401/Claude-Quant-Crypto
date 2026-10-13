"""H040: cota bruta de la deriva en la hora previa a la liquidación de funding (8 h).

Uso: python3 experiments/h040_funding_hour.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import load_funding, load_klines  # noqa: E402

END = pd.Timestamp("2023-01-01", tz="UTC")


def main():
    res = {}
    for u in (0.0, 0.0003):
        vals = []
        for sym in ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"):
            k = load_klines("um", sym)
            k = k[k.index < END]
            f = load_funding(sym)
            bars = k[k.index.hour.isin([7, 15, 23])]          # hora previa a 08/16/00 UTC
            last_f = f.reindex(bars.index, method="ffill")     # último funding liquidado (≤ inicio)
            r = bars["close"] / bars["open"] - 1
            m = last_f.abs() >= u
            vals.append((-np.sign(last_f) * r)[m & (last_f != 0)].dropna())
        x = pd.concat(vals)
        res[f"u={u}"] = {"n": int(len(x)), "mean_gross": float(x.mean()),
                         "t": float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))),
                         "beats_maker_rt": bool(x.mean() > 0.0004 and
                                                x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) > 3)}
    (ROOT / "reports/h040.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
