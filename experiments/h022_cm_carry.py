"""H022: carry trimestral COIN-M BTC/ETH con la moneda como margen (capital completo).

Uso: python3 experiments/h022_cm_carry.py
Regla fija (H012-G3): θ = 5 %, salida anticipada. W = 1 por pata, sin liquidación.
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

h12.W = 1.0          # todo el capital en la cobertura (la moneda es el margen)
h12.MMR = -1e9       # el corto coin-margined cubierto no se liquida
START = pd.Timestamp("2023-01-01", tz="UTC")
BENCH = 0.05


def main():
    nets, info = [], {}
    for base in ("BTCUSD", "ETHUSD"):
        spot, futs = h12.load(base, market="cm")
        futs = {c: f for c, f in futs.items() if len(f) and f.index[-1] < h12.HOLDOUT}
        o = h12.run(spot, futs, 0.05, "early", end=h12.HOLDOUT)
        nets.append(o["net"].rename(base))
        oo = o[o.index >= START]
        info[base] = {"ann_oos": float(oo["net"].mean() * 8760),
                      "ann_train": float(o["net"][o.index < START].mean() * 8760),
                      "entries_oos": int(oo["entry"].sum()),
                      "time_in_mkt_oos": float((oo["pos"] > 0).mean()),
                      "cost_ann_oos": float((oo["cost"] + oo["rebalance"]).mean() * 8760),
                      "contracts": len(futs)}
    R = pd.concat(nets, axis=1).fillna(0.0).mean(axis=1)
    Ro = R[R.index >= START]
    lo, hi = metrics.block_bootstrap_mean_ci(Ro.to_numpy(), block=24 * 60, n_boot=2000)
    res = {"oos_ann": float(Ro.mean() * 8760), "sharpe_m": metrics.sharpe_resampled(Ro),
           "max_dd": metrics.max_drawdown(Ro.to_numpy()), "ci95_hourly": [lo, hi],
           "train_ann": float(R[R.index < START].mean() * 8760),
           "bench_usdt": BENCH, "beats_bench": bool(Ro.mean() * 8760 > BENCH),
           "yearly": {int(y): float(v) for y, v in Ro.groupby(Ro.index.year).sum().items()},
           "per_asset": info}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h022.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
