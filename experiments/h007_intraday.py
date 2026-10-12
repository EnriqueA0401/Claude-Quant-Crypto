"""H007 · G2: estacionalidad por bloques de 4 h UTC (train 2020–2022, BTC+ETH perps).

Uso: python3 experiments/h007_intraday.py
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.costs import PERP  # noqa: E402
from src.data import load_funding, load_klines  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
BLOCKS = [(h, h + 4) for h in range(0, 24, 4)]


def block_returns(sym):
    k = load_klines("um", sym)["open"]
    k = k[k.index < TRAIN_END + pd.Timedelta("4h")]
    f = load_funding(sym)
    rows = {}
    for a, b in BLOCKS:
        st = k[k.index.hour == a]
        en = k.reindex(st.index + pd.Timedelta(hours=b - a))
        r = (en.to_numpy() / st.to_numpy() - 1)
        # funding con ts en (inicio, fin] del bloque: un largo lo paga
        fs = np.array([f[(f.index > t) & (f.index <= t + pd.Timedelta(hours=b - a))].sum()
                       for t in st.index])
        s = pd.Series(r, index=st.index).where(st.index < TRAIN_END).dropna()
        rows[f"{a:02d}-{b:02d}"] = (s, pd.Series(fs, index=st.index).reindex(s.index))
    return rows


def main():
    res = {}
    data = {s: block_returns(s) for s in ["BTCUSDT", "ETHUSDT"]}
    for name in data["BTCUSDT"]:
        r = pd.concat([data[s][name][0] for s in data], axis=1).mean(axis=1).dropna()
        fu = pd.concat([data[s][name][1] for s in data], axis=1).mean(axis=1).reindex(r.index)
        sign = np.sign(r.mean())
        net = sign * r - sign * fu - 2 * PERP.per_side
        # t de la media bruta con días como observación (bloques no solapan entre días)
        t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
        res[name] = {"days": int(len(r)), "mean_gross": float(r.mean()), "t_gross": float(t),
                     "p_gross": float(2 * stats.norm.sf(abs(t))),
                     "mean_net_trade": float(net.mean()),
                     "cost_roundtrip": 2 * PERP.per_side}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h007_g2.json").write_text(json.dumps(
        {"commit": commit, "variants": len(BLOCKS), "bonferroni_alpha": 0.05 / len(BLOCKS),
         "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.astype(float).round(5).to_string())


if __name__ == "__main__":
    main()
