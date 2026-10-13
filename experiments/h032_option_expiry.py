"""H032: retorno de BTC/ETH en las 48 h antes / después del vencimiento mensual de Deribit.

Uso: python3 experiments/h032_option_expiry.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import load_funding, load_klines  # noqa: E402

COST = 2 * 0.0010
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def expiries():
    out = []
    for m in pd.period_range("2020-01", "2025-09", freq="M"):
        last = pd.Timestamp(m.end_time.date(), tz="UTC")
        while last.dayofweek != 4:
            last -= pd.Timedelta("1D")
        out.append(last + pd.Timedelta("8h"))
    return out


def window_returns(sym, before):
    k = load_klines("um", sym)["open"]
    f = load_funding(sym)
    rows = []
    for e in expiries():
        a, b = (e - pd.Timedelta("48h"), e) if before else (e, e + pd.Timedelta("48h"))
        if a in k.index and b in k.index:
            fs = f[(f.index > a) & (f.index <= b)].sum()
            rows.append({"exp": e, "ret": k[b] / k[a] - 1, "fund": fs})
    return pd.DataFrame(rows).set_index("exp")


def main():
    res = {}
    for name, before in (("pre48h", True), ("post48h", False)):
        d = pd.concat([window_returns(s, before) for s in ("BTCUSDT", "ETHUSDT")])
        tr, te = d[d.index < TRAIN_END], d[(d.index >= TRAIN_END) & (d.index < HOLDOUT)]
        side = float(np.sign(tr["ret"].mean()))
        for part, x in (("train", tr), ("oos", te)):
            net = side * x["ret"] - side * x["fund"] - COST
            res[f"{name}|{part}"] = {"n": int(len(x)), "side": side,
                                     "mean_gross": float(x["ret"].mean()),
                                     "t_gross": float(x["ret"].mean() / (x["ret"].std(ddof=1) / np.sqrt(len(x)))),
                                     "mean_net_trade": float(net.mean()),
                                     "t_net": float(net.mean() / (net.std(ddof=1) / np.sqrt(len(net))))}
    (ROOT / "reports/h032.json").write_text(json.dumps(res, indent=1) + "\n")
    print(pd.DataFrame(res).T.round(4).to_string())


if __name__ == "__main__":
    main()
