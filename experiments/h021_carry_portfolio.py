"""H021: cartera carry BTC/ETH = H012 (trimestral) + H001 (perp) cuando H012 está fuera.

Uso: python3 experiments/h021_carry_portfolio.py
Diseño fijado en HYPOTHESES.md (1 variante). Juzgar 2023-01 → 2025-09 contra 5 %/año.
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
from h001_carry import load as load_perp  # noqa: E402
from src import metrics  # noqa: E402
from src.carry import carry_signal, run_carry  # noqa: E402
from src.costs import PERP, SPOT  # noqa: E402

START = pd.Timestamp("2023-01-01", tz="UTC")
BENCH = 0.05


def one(base):
    spot, futs = h12.load(base)
    futs = {c: f for c, f in futs.items() if f.index[-1] < h12.HOLDOUT}
    q = h12.run(spot, futs, 0.05, "early", end=h12.HOLDOUT)
    perp, sp, trad, fund = load_perp(base)
    m = perp.index < h12.HOLDOUT
    perp, sp, trad, fund = perp[m], sp[m], trad[m], fund[fund.index < h12.HOLDOUT]
    sig = carry_signal(fund, perp.index, 3, 1e-4)
    busy = (q["pos"] > 0).reindex(perp.index).fillna(False)
    # sin solapamiento: fuera del perp una hora antes, durante y una hora después de H012
    block = busy | busy.shift(-1, fill_value=False) | busy.shift(1, fill_value=False)
    sig = sig.where(~block, 0.0)
    p = run_carry(sp, perp, fund, sig, SPOT, PERP, tradable=trad, liq_high=perp["mark_high"])
    net = q["net"].reindex(p.index).fillna(0.0) + p["net"]
    return net, q, p


def main():
    nets, info = [], {}
    for base in ("BTCUSDT", "ETHUSDT"):
        net, q, p = one(base)
        nets.append(net.rename(base))
        o = slice(START, None)
        info[base] = {"ann_q": float(q["net"].loc[o].mean() * 8760),
                      "ann_perp": float(p["net"].loc[o].mean() * 8760),
                      "time_q": float((q["pos"].loc[o] > 0).mean()),
                      "time_perp": float((p["pos"].loc[o] > 0).mean())}
    R = pd.concat(nets, axis=1).fillna(0.0).mean(axis=1)
    R = R[R.index >= START]
    lo, hi = metrics.block_bootstrap_mean_ci(R.to_numpy(), block=24 * 60, n_boot=2000)
    res = {"oos_ann": float(R.mean() * 8760), "sharpe_m": metrics.sharpe_resampled(R),
           "max_dd": metrics.max_drawdown(R.to_numpy()), "ci95_hourly": [lo, hi],
           "bench_usdt": BENCH, "beats_bench": bool(R.mean() * 8760 > BENCH),
           "yearly": {int(y): float(v) for y, v in R.groupby(R.index.year).sum().items()},
           "per_asset": info}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h021.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
