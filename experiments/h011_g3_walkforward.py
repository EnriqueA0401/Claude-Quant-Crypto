"""H011 · G3: walk-forward del carry en altcoins (holdout desde 2025-10 intacto).

Uso: python3 experiments/h011_g3_walkforward.py
Selección fijada antes de ver OOS: la variante con mayor Sharpe mensual en las semanas de
train (anteriores al test menos 1 semana). Folds de 6 meses desde 2023-01.
Criterio económico de G0: ≥ 5 %/año sobre capital y ≥ 100 entradas OOS.
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h011_alt_carry as h11  # noqa: E402
from src import metrics  # noqa: E402

HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def main():
    P = h11.panels()
    po = P[0]
    last_mon = po.index[(po.index.dayofweek == 0) & (po.index <= HOLDOUT)][-1]
    end = last_mon + pd.Timedelta("1D")
    runs = {f"D={d}|theta={th}": h11.run(*P, d, th, end=end) for d, th in h11.VARIANTS}
    for k, r in runs.items():
        r.to_csv(ROOT / f"reports/h011_dev_{k.replace('|', '_')}.csv")
    edges = sorted(set(list(pd.date_range(pd.Timestamp("2023-01-01", tz="UTC"), HOLDOUT,
                                          freq="6MS")) + [HOLDOUT]))
    oos, folds = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        score = {k: metrics.sharpe_resampled(r["net"][r.index < a - pd.Timedelta("7D")])
                 for k, r in runs.items()}
        best = max(score, key=score.get)
        seg = runs[best][(runs[best].index >= a) & (runs[best].index < b)]
        oos.append(seg)
        folds.append({"test": f"{a.date()}..{b.date()}", "chosen": best, "weeks": int(len(seg)),
                      "ann": float(seg["net"].mean() * 52),
                      "funding_ann": float(seg["funding"].mean() * 52),
                      "entries": int(seg["changes"].sum() // 2),
                      "avg_pairs": float(seg["n"].mean())})
    O = pd.concat(oos)
    R = O["net"]
    R2 = O["basis"] + O["funding"] - 2 * O["cost"]
    lo, hi = metrics.block_bootstrap_mean_ci(R.to_numpy(), block=8, n_boot=5000)
    summ = {"oos_weeks": int(len(R)), "oos_ann": float(R.mean() * 52),
            "oos_sharpe_m": metrics.sharpe_resampled(R),
            "oos_mdd": metrics.max_drawdown(R.to_numpy()), "ci95_weekly": [lo, hi],
            "oos_ann_cost2x": float(R2.mean() * 52),
            "funding_ann": float(O["funding"].mean() * 52),
            "basis_ann": float(O["basis"].mean() * 52), "cost_ann": float(O["cost"].mean() * 52),
            "entries_approx": int(O["changes"].sum() // 2), "liquidations": int(O["liquidations"].sum()),
            "avg_pairs": float(O["n"].mean()),
            "yearly": {int(y): float(v) for y, v in R.groupby(R.index.year).sum().items()}}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h011_g3.json").write_text(json.dumps(
        {"commit": commit, "folds": folds, "summary": summ}, indent=1) + "\n")
    print(pd.DataFrame(folds).to_string())
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
