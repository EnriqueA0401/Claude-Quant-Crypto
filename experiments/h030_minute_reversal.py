"""H030: cota bruta de la reversión tras minutos extremos (BTC/ETH perp, 2022).

Uso: python3 experiments/h030_minute_reversal.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import load_klines  # noqa: E402

MAKER_RT = 0.0004


def main():
    res = {}
    for sym in ("BTCUSDT", "ETHUSDT"):
        k = load_klines("um", sym, "1m")
        k = k[(k.index >= "2022-01-01") & (k.index < "2023-01-01")]
        r = k["close"] / k["open"] - 1                      # retorno del minuto t
        sd = r.shift(1).rolling(1440, min_periods=720).std()
        o = k["open"].to_numpy()
        for kk in (4, 6):
            ev = np.flatnonzero((r.abs() > kk * sd).to_numpy())
            for hmin in (5, 30):
                ev2 = ev[ev + 1 + hmin < len(o)]
                fwd = o[ev2 + 1 + hmin] / o[ev2 + 1] - 1     # desde el open del minuto t+1
                contra = -np.sign(r.to_numpy()[ev2]) * fwd
                t = contra.mean() / (contra.std(ddof=1) / np.sqrt(len(contra)))
                res[f"{sym}|k={kk}|H={hmin}"] = {"events": int(len(contra)),
                                                 "mean_gross": float(contra.mean()),
                                                 "t": float(t),
                                                 "beats_maker_rt": bool(contra.mean() > MAKER_RT and t > 3)}
    (ROOT / "reports/h030.json").write_text(json.dumps(res, indent=1) + "\n")
    print(pd.DataFrame(res).T.to_string())


if __name__ == "__main__":
    main()
