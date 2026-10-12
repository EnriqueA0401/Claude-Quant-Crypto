"""H012 · G4: robustez del basis trimestral en activos no usados en el diseño.

Uso: python3 experiments/h012_g4_robustness.py
Variante fija (elegida en G3): θ = 5 %, salida anticipada. Activos: trimestrales COIN-M
de 12 monedas (precio USD por moneda; aproximación lineal del contrato inverso) con su
spot XXXUSDT. Pruebas: costes ×1 y ×2, vecinos θ ∈ {3 %, 7 %}, por año y por activo.
Solo contratos que vencen antes del holdout (2025-10-01).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h012_quarterly_basis as h12  # noqa: E402
from src import metrics  # noqa: E402
from src.data import DATA, load_klines  # noqa: E402

COINS = ["ADA", "BCH", "BNB", "DOT", "EOS", "ETC", "FIL", "LINK", "LTC", "SOL", "TRX", "XRP"]


def load_cm(coin):
    spot = load_klines("spot", f"{coin}USDT")[["open", "close"]]
    futs = {}
    for d in sorted((DATA / "futures/cm/monthly/klines").glob(f"{coin}USD_*")):
        if (d / "1h").exists():
            f = load_klines("cm", d.name)[["open", "high", "close"]]
            if f.index[-1] < h12.HOLDOUT:
                futs[d.name] = f
    return spot, futs


def with_costs(mult):
    h12.CS, h12.CF = (0.0010 + 0.0005) * mult, (0.0005 + 0.0005) * mult


def main():
    res, per_asset = {}, {}
    for label, th, mult in [("base", 0.05, 1), ("cost2x", 0.05, 2),
                            ("theta3", 0.03, 1), ("theta7", 0.07, 1)]:
        with_costs(mult)
        series, ent = [], 0
        for coin in COINS:
            spot, futs = load_cm(coin)
            if not futs:
                continue
            o = h12.run(spot, futs, th, "early", end=h12.HOLDOUT)
            series.append(o["net"].rename(coin))
            ent += int(o["entry"].sum())
            if label == "base":
                per_asset[coin] = {"ann": float(o["net"].mean() * h12.HPY),
                                   "entries": int(o["entry"].sum()),
                                   "liq": int(o["liquidated"].sum()),
                                   "first": str(o.index[0].date())}
        P = pd.concat(series, axis=1).fillna(0.0)
        R = P.mean(axis=1)                      # capital repartido entre las 12 monedas
        lo, hi = metrics.block_bootstrap_mean_ci(R.to_numpy(), block=24 * 60, n_boot=2000)
        R23 = R[R.index >= pd.Timestamp("2023-01-01", tz="UTC")]
        res[label] = {"ann": float(R.mean() * h12.HPY), "sharpe_m": metrics.sharpe_resampled(R),
                      "max_dd": metrics.max_drawdown(R.to_numpy()), "entries": ent,
                      "ci95_hourly": [lo, hi], "ann_2023_2025": float(R23.mean() * h12.HPY),
                      "yearly": {int(y): float(v) for y, v in R.groupby(R.index.year).sum().items()}}
    with_costs(1)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h012_g4.json").write_text(json.dumps(
        {"commit": commit, "results": res, "per_asset": per_asset}, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    print(pd.DataFrame(per_asset).T.to_string())


if __name__ == "__main__":
    main()
