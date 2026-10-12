"""H003 · G2: corto tras funding extremo (train 2020–2022, BTC y ETH, perps 1h).

Uso: python3 experiments/h003_funding_extreme.py
Variantes fijadas antes de ver resultados (4): p ∈ {0.90, 0.95} × H ∈ {24, 72} h.
Nulo: los mismos números de operaciones y duración en momentos aleatorios (500 sims).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import backtest, metrics  # noqa: E402
from src.costs import PERP  # noqa: E402
from src.data import load_funding, load_klines  # noqa: E402
from src.signals import funding_extreme_short  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
VARIANTS = [(p, h) for p in (0.90, 0.95) for h in (24, 72)]


def load(sym, end=None):
    k = load_klines("um", sym)
    k["liq_high"] = load_klines("um", sym, kind="markPriceKlines")["high"].reindex(k.index)
    k["liq_high"] = k["liq_high"].fillna(k["high"])
    f = load_funding(sym)
    if end is not None:
        k, f = k[k.index < end], f[f.index < end]
    return k, f


def trade_returns(out, starts, hold):
    net = out["net"].to_numpy()
    return np.array([net[t + 1:t + 1 + hold].sum() for t in starts if t + hold < len(net)])


def worst_rise(k, starts, hold):
    o, h = k["open"].to_numpy(), k["liq_high"].to_numpy()
    return max((h[t + 1:t + 1 + hold].max() / o[t + 1] for t in starts
                if t + hold < len(o)), default=0.0)


def null_trades(k, f, n, hold, sims=500, seed=0):
    """Media por operación de cortos aleatorios (sin solapamiento aproximado)."""
    rng = np.random.default_rng(seed)
    o = k["open"].to_numpy()
    fb = backtest.run(k["open"], pd.Series(-1.0, index=k.index), PERP, spot=False,
                      funding=f)["funding"].to_numpy()   # funding pagado por el corto (pos·f)
    cost = 2 * PERP.per_side
    means = []
    for _ in range(sims):
        ts = rng.integers(1, len(o) - hold - 1, size=n)
        r = [-(o[t + hold] / o[t] - 1) - fb[t:t + hold].sum() - cost for t in ts]
        means.append(np.mean(r))
    return np.array(means)


def main():
    res = {}
    for sym in ["BTCUSDT", "ETHUSDT"]:
        k, f = load(sym, TRAIN_END)
        for p, hold in VARIANTS:
            sig = funding_extreme_short(f, k.index, p, hold)
            starts = sig.attrs["starts"]
            out = backtest.run(k["open"], sig, PERP, spot=False, funding=f)
            tr = trade_returns(out, starts, hold)
            wr = worst_rise(k, starts, hold)
            assert wr < 1.9, f"posible liquidación {sym} {p} {hold}: {wr}"
            nul = null_trades(k, f, len(tr), hold)
            res[f"{sym}|p={p}|H={hold}"] = {
                "trades": int(len(tr)), "mean_trade": float(tr.mean()),
                "hit_rate": float((tr > 0).mean()),
                "t_stat": float(tr.mean() / (tr.std(ddof=1) / np.sqrt(len(tr)))),
                "null_mean": float(nul.mean()),
                "p_vs_null": float((nul >= tr.mean()).mean()),
                "ann_return": float(out["net"].mean() * 24 * 365),
                "sharpe_m": metrics.sharpe_resampled(out["net"]),
                "max_dd": metrics.max_drawdown(out["net"].to_numpy()),
                "worst_rise": wr}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h003_g2.json").write_text(json.dumps(
        {"commit": commit, "period": "2020-01-01..2022-12-31", "variants": len(VARIANTS),
         "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.astype(float).round(4).to_string())


if __name__ == "__main__":
    main()
