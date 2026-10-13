"""H022 · G4: costes ×2, vecinos θ ∈ {3 %, 7 %} (BTC/ETH OOS) y 12 altcoins COIN-M (W = 1).

Uso: python3 experiments/h022_g4.py
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
from h012_g4_robustness import COINS  # noqa: E402
from src import metrics  # noqa: E402

h12.W, h12.MMR = 1.0, -1e9
START = pd.Timestamp("2023-01-01", tz="UTC")


def port(bases, th, mult=1.0):
    h12.CS, h12.CF = 0.0015 * mult, 0.0010 * mult
    nets, ent = [], 0
    for b in bases:
        spot, futs = h12.load(b, market="cm")
        futs = {c: f for c, f in futs.items() if len(f) and f.index[-1] < h12.HOLDOUT}
        if not futs:
            continue
        o = h12.run(spot, futs, th, "early", end=h12.HOLDOUT)
        nets.append(o["net"].rename(b))
        ent += int(o["entry"][o.index >= START].sum())
    h12.CS, h12.CF = 0.0015, 0.0010
    R = pd.concat(nets, axis=1).fillna(0.0).mean(axis=1)
    R = R[R.index >= START]
    lo, hi = metrics.block_bootstrap_mean_ci(R.to_numpy(), block=24 * 60, n_boot=2000)
    return {"oos_ann": float(R.mean() * 8760), "sharpe_m": metrics.sharpe_resampled(R),
            "max_dd": metrics.max_drawdown(R.to_numpy()), "entries_oos": ent,
            "ci95_hourly": [lo, hi],
            "yearly": {int(y): float(v) for y, v in R.groupby(R.index.year).sum().items()}}


def main():
    bb = ["BTCUSD", "ETHUSD"]
    res = {"cost2x": port(bb, 0.05, 2.0), "theta3": port(bb, 0.03), "theta7": port(bb, 0.07),
           "alts_12": port([f"{c}USD" for c in COINS], 0.05)}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h022_g4.json").write_text(json.dumps({"commit": commit, "results": res},
                                                          indent=1) + "\n")
    for k, v in res.items():
        print(k, round(v["oos_ann"], 4), round(v["sharpe_m"], 2), round(v["max_dd"], 3),
              v["entries_oos"], {y: round(z, 3) for y, z in v["yearly"].items()})


if __name__ == "__main__":
    main()
