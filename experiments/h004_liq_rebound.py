"""H004 · G2: largo tras cascadas de liquidación (caída fuerte + OI cae), BTC/ETH 1h.

Uso: python3 experiments/h004_liq_rebound.py
Variantes fijadas en HYPOTHESES.md: k ∈ {3, 4} × H ∈ {4, 24}. Train 2020-09 → 2022-12.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import backtest  # noqa: E402
from src.costs import PERP  # noqa: E402
from src.data import load_funding, load_klines, load_oi_hourly  # noqa: E402
from src.signals import liquidation_rebound_long  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
VARIANTS = [(k, h) for k in (3, 4) for h in (4, 24)]


def load(sym, end=None):
    k = load_klines("um", sym)[["open", "close"]]
    k["oi"] = load_oi_hourly(sym).reindex(k.index)
    k = k[k["oi"].first_valid_index():]
    k["oi"] = k["oi"].ffill()
    f = load_funding(sym)
    if end is not None:
        k, f = k[k.index < end], f[f.index < end]
    return k, f


def trade_returns(out, starts, hold):
    net = out["net"].to_numpy()
    return np.array([net[t + 1:t + 1 + hold].sum() for t in starts if t + hold < len(net)])


def null_means(k, f, n, hold, sims=500, seed=0):
    rng = np.random.default_rng(seed)
    o = k["open"].to_numpy()
    fpay = backtest.run(k["open"], pd.Series(1.0, index=k.index), PERP, spot=False,
                        funding=f)["funding"].to_numpy()
    cost = 2 * PERP.per_side
    return np.array([np.mean([o[t + hold] / o[t] - 1 - fpay[t:t + hold].sum() - cost
                              for t in rng.integers(1, len(o) - hold - 1, n)])
                     for _ in range(sims)])


def evaluate(sym, end):
    k, f = load(sym, end)
    res = {}
    for kk, hold in VARIANTS:
        sig = liquidation_rebound_long(k, kk, hold)
        out = backtest.run(k["open"], sig, PERP, spot=False, funding=f)
        tr = trade_returns(out, sig.attrs["starts"], hold)
        if len(tr) < 2:
            res[f"{sym}|k={kk}|H={hold}"] = {"trades": int(len(tr))}
            continue
        nul = null_means(k, f, len(tr), hold)
        res[f"{sym}|k={kk}|H={hold}"] = {
            "trades": int(len(tr)), "mean_trade": float(tr.mean()),
            "median_trade": float(np.median(tr)), "hit": float((tr > 0).mean()),
            "t": float(tr.mean() / (tr.std(ddof=1) / np.sqrt(len(tr)))),
            "null_mean": float(nul.mean()), "p_vs_null": float((nul >= tr.mean()).mean())}
    return res


def main():
    res = {}
    for sym in ["BTCUSDT", "ETHUSDT"]:
        res.update(evaluate(sym, TRAIN_END))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h004_g2.json").write_text(json.dumps(
        {"commit": commit, "period": "2020-09..2022-12", "variants": len(VARIANTS),
         "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.round(4).to_string())


if __name__ == "__main__":
    main()
