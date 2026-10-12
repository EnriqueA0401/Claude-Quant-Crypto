"""H008 · G3: walk-forward del carry cross-sectional de funding (holdout desde 2025-10).

Uso: python3 experiments/h008_g3_walkforward.py
Selección fijada antes de ver OOS: variante D con mayor Sharpe mensual en las semanas
de train (anteriores al test menos 1 semana). Folds de 6 meses desde 2023-01.
Incluye costes ×2 y descomposición funding / precio.
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h005_xs_momentum as h5  # noqa: E402
from h008_funding_xs import DAYS, funding_events, make_score  # noqa: E402
from src import metrics  # noqa: E402

HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def main():
    o, c, h, qv, fd = h5.panel()
    ev = funding_events(o.columns)
    last_mon = o.index[(o.index.dayofweek == 0) & (o.index <= HOLDOUT)][-1]
    end = last_mon + pd.Timedelta("1D")
    runs = {d: h5.run(o, c, h, qv, fd, 1, "mom", end=end, score_fn=make_score(ev, d))
            for d in DAYS}
    edges = sorted(set(list(pd.date_range(pd.Timestamp("2023-01-01", tz="UTC"), HOLDOUT,
                                          freq="6MS")) + [HOLDOUT]))
    oos, folds = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        score = {d: metrics.sharpe_resampled(r["net"][r.index < a - pd.Timedelta("7D")])
                 for d, r in runs.items()}
        best = max(score, key=score.get)
        seg = runs[best][(runs[best].index >= a) & (runs[best].index < b)]
        oos.append(seg)
        folds.append({"test": f"{a.date()}..{b.date()}", "chosen": f"D={best}",
                      "weeks": int(len(seg)), "ann": float(seg["net"].mean() * 52),
                      "funding_ann": float(seg["funding"].mean() * 52),
                      "sharpe_m": metrics.sharpe_resampled(seg["net"])})
    O = pd.concat(oos)
    R = O["net"]
    R2 = O["gross"] - 2 * O["cost"]
    lo, hi = metrics.block_bootstrap_mean_ci(R.to_numpy(), block=8, n_boot=5000)
    summ = {"oos_weeks": int(len(R)), "oos_ann": float(R.mean() * 52),
            "oos_sharpe_m": metrics.sharpe_resampled(R),
            "oos_mdd": metrics.max_drawdown(R.to_numpy()), "ci95_weekly": [lo, hi],
            "oos_ann_cost2x": float(R2.mean() * 52),
            "oos_sharpe_cost2x": metrics.sharpe_resampled(R2),
            "funding_ann": float(O["funding"].mean() * 52),
            "price_ann": float((O["gross"] - O["funding"]).mean() * 52),
            "cost_ann": float(O["cost"].mean() * 52),
            "yearly": {int(y): float(v) for y, v in R.groupby(R.index.year).sum().items()},
            "train_full_sample": {f"D={d}": {"ann": float(r["net"][r.index < pd.Timestamp("2023-01-01", tz="UTC")].mean() * 52),
                                            "funding_ann": float(r["funding"][r.index < pd.Timestamp("2023-01-01", tz="UTC")].mean() * 52)}
                                  for d, r in runs.items()}}
    for d, r in runs.items():
        r.to_csv(ROOT / f"reports/h008_dev_D{d}.csv")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h008_g3.json").write_text(json.dumps(
        {"commit": commit, "folds": folds, "summary": summ}, indent=1) + "\n")
    print(pd.DataFrame(folds).to_string())
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
