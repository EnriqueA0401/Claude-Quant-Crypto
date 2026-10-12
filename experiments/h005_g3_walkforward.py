"""H005 · G3: walk-forward semanal en desarrollo (holdout desde 2025-10-01 intacto).

Uso: python3 experiments/h005_g3_walkforward.py
Selección fijada antes de ver OOS: en cada fold, la variante con mayor Sharpe mensual
en las semanas de train (anteriores al test menos 1 semana de embargo).
Folds de test de 6 meses desde 2023-01.
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from h005_xs_momentum import VARIANTS, panel, run  # noqa: E402
from src import metrics  # noqa: E402

HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def main():
    o, c, h, qv, fd = panel()
    # ninguna semana de tenencia puede terminar dentro del holdout
    last_mon = o.index[(o.index.dayofweek == 0) & (o.index <= HOLDOUT)][-1]
    runs = {f"L={L}|{d}": run(o, c, h, qv, fd, L, d, end=last_mon + pd.Timedelta("1D"))
            for L, d in VARIANTS}
    edges = sorted(set(list(pd.date_range("2023-01-01", HOLDOUT, freq="6MS", tz="UTC"))
                       + [HOLDOUT]))
    oos, folds = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        score = {v: metrics.sharpe_resampled(r["net"][r.index < a - pd.Timedelta("7D")])
                 for v, r in runs.items()}
        best = max(score, key=score.get)
        r = runs[best]["net"][(runs[best].index >= a) & (runs[best].index < b)]
        oos.append(r)
        folds.append({"test": f"{a.date()}..{b.date()}", "chosen": best,
                      "weeks": int(len(r)), "ann": float(r.mean() * 52),
                      "sharpe_m": metrics.sharpe_resampled(r)})
    R = pd.concat(oos)
    lo, hi = metrics.block_bootstrap_mean_ci(R.to_numpy(), block=8, n_boot=5000)
    summ = {"oos_weeks": int(len(R)), "oos_ann": float(R.mean() * 52),
            "oos_sharpe_m": metrics.sharpe_resampled(R),
            "oos_mdd": metrics.max_drawdown(R.to_numpy()), "ci95_weekly": [lo, hi],
            "yearly": {int(y): float(v) for y, v in R.groupby(R.index.year).sum().items()}}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h005_g3.json").write_text(json.dumps(
        {"commit": commit, "folds": folds, "summary": summ}, indent=1) + "\n")
    print(pd.DataFrame(folds).to_string())
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
