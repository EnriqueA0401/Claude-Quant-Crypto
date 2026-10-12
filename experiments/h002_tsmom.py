"""H002 · G2: momentum de series temporales en perps BTC/ETH (train 2020–2022).

Uso: python3 experiments/h002_tsmom.py
Variantes fijadas antes de ver resultados (8): L ∈ {7, 14, 28, 56} días ×
modo ∈ {largo/corto, largo/plano}. Barras diarias UTC desde klines 1h; señal al close
del día d, ejecución en el open del día d+1; funding real incluido; posición 1x.
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
from src.signals import ts_momentum  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
VARIANTS = [(L, mode) for L in (7, 14, 28, 56) for mode in ("ls", "lf")]
DPY = 365


def daily(sym):
    h = load_klines("um", sym)
    mark = load_klines("um", sym, kind="markPriceKlines")["high"].reindex(h.index)
    h["liq_high"] = mark.fillna(h["high"])
    d = h.resample("1D").agg({"open": "first", "high": "max", "close": "last",
                              "liq_high": "max", "volume": "sum"})
    full_days = h["open"].resample("1D").count() == 24
    return d[full_days], load_funding(sym)


def run_variant(d, fund, L, mode, cost_mult=1.0):
    sig = ts_momentum(d, L)
    if mode == "lf":
        sig = sig.clip(lower=0)
    out = backtest.run(d["open"], sig, PERP.scaled(cost_mult), spot=False, funding=fund)
    # liquidación de un corto 1x: el high del día tendría que casi duplicar el open
    shorts = out["pos"] < 0
    worst = (d["liq_high"] / d["open"]).reindex(out.index)[shorts].max() if shorts.any() else 0
    return out, float(worst)


def summarize(out):
    r = out["net"].to_numpy()
    return {"ann_return": float(r.mean() * DPY), "sharpe_ann": metrics.sharpe_resampled(out["net"]),
            "max_dd": metrics.max_drawdown(r), "trades": backtest.n_trades(out["pos"]),
            "funding_ann": float(-out["funding"].mean() * DPY),
            "cost_ann": float(out["cost"].mean() * DPY)}


def main():
    res = {}
    for sym in ["BTCUSDT", "ETHUSDT"]:
        d, fund = daily(sym)
        d = d[d.index < TRAIN_END]
        fund = fund[fund.index < TRAIN_END]
        for L, mode in VARIANTS:
            out, worst = run_variant(d, fund, L, mode)
            assert worst < 1.9, f"posible liquidación {sym} {L} {mode}: {worst}"
            res[f"{sym}|L={L}|{mode}"] = summarize(out)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h002_g2.json").write_text(json.dumps(
        {"commit": commit, "period": "2020-01-01..2022-12-31", "variants": len(VARIANTS),
         "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.astype(float).round(3).to_string())


if __name__ == "__main__":
    main()
