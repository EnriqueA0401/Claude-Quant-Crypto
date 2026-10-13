"""H033: carry COIN-M siempre cubierto; la moneda se mantiene y solo se rota el futuro.

Uso: python3 experiments/h033_always_hedged.py [holdout]
Sin argumento: periodo informativo 2021 → 2025-09 (2023–2025 contaminado, ver HYPOTHESES).
Con 'holdout': evalúa 2025-10-01 → 2026-09-30 UNA sola vez (registrar en STATE.md).
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h012_quarterly_basis as h12  # noqa: E402
from src import metrics  # noqa: E402

h12.W, h12.MMR = 1.0, -1e9
h12.CS, h12.CF = 0.0, 0.0010          # el spot no se rota en cada ciclo
SPOT_ONCE = 2 * 0.0015                # compra inicial y venta final del spot
CASH = 0.045


def run(start, end):
    nets = []
    for b in ("BTCUSD", "ETHUSD"):
        spot, futs = h12.load(b, market="cm")
        futs = {c: f for c, f in futs.items() if len(f) and f.index[-1] < end}
        o = h12.run(spot, futs, -1.0, "expiry", end=end)     # θ = −100 %: siempre cubierto
        nets.append(o["net"][o.index >= start].rename(b))
    R = pd.concat(nets, axis=1).fillna(0.0).mean(axis=1)
    R.iloc[0] -= SPOT_ONCE / 2
    R.iloc[-1] -= SPOT_ONCE / 2
    lo, hi = metrics.block_bootstrap_mean_ci(R.to_numpy(), block=24 * 30, n_boot=2000)
    years = (R.index[-1] - R.index[0]).days / 365
    return {"period": f"{R.index[0].date()}..{R.index[-1].date()}",
            "ann": float(R.mean() * 8760), "sharpe_m": metrics.sharpe_resampled(R),
            "max_dd": metrics.max_drawdown(R.to_numpy()), "ci95_hourly": [lo, hi],
            "excess_vs_cash": float(R.mean() * 8760 - CASH), "years": years,
            "yearly": {int(y): float(v) for y, v in R.groupby(R.index.year).sum().items()}}


def main(holdout=False):
    if holdout:
        res = {"holdout": run(pd.Timestamp("2025-10-01", tz="UTC"), pd.Timestamp("2026-10-01", tz="UTC"))}
        out = "reports/h033_holdout.json"
    else:
        res = {"train_2021_2022": run(pd.Timestamp("2021-01-01", tz="UTC"), pd.Timestamp("2023-01-01", tz="UTC")),
               "informativo_2023_2025": run(pd.Timestamp("2023-01-01", tz="UTC"), h12.HOLDOUT)}
        out = "reports/h033.json"
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / out).write_text(json.dumps({"commit": commit, "cash": CASH, "results": res}, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(holdout=len(sys.argv) > 1 and sys.argv[1] == "holdout")
