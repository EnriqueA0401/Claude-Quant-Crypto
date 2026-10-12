"""H002 · G5 (preliminar): DSR con el contador global, PBO-CSCV y alfa frente a buy&hold.

Uso: python3 experiments/h002_g5_stats.py   (requiere haber corrido h002_g3_walkforward)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from h002_g3_walkforward import DESIGN, all_runs  # noqa: E402
from h002_tsmom import VARIANTS  # noqa: E402
from src import metrics  # noqa: E402

GLOBAL_TRIALS = 14   # contador global en STATE.md al ejecutar


def main():
    runs = {s: all_runs(s) for s in DESIGN}
    mat = pd.concat({v: pd.concat([runs[s][0][v]["net"] for s in DESIGN], axis=1).mean(axis=1)
                     for v in VARIANTS}, axis=1).dropna()
    bh = pd.concat([runs[s][1]["net"] for s in DESIGN], axis=1).mean(axis=1).reindex(mat.index)
    # Sharpe por periodo semanal para DSR (menos autocorrelación que diario)
    wk = mat.resample("W").sum()
    srs = wk.apply(lambda c: metrics.sharpe(c.to_numpy()))
    best = srs.idxmax()
    dsr = metrics.deflated_sharpe(wk[best].to_numpy(), GLOBAL_TRIALS, float(srs.var(ddof=1)))
    pbo = metrics.pbo_cscv(wk.to_numpy(), n_splits=10)
    # alfa: regresión semanal de la estrategia sobre buy & hold (OLS, errores HAC simples)
    y, x = wk[best].to_numpy(), bh.resample("W").sum().to_numpy()
    X = np.c_[np.ones_like(x), x]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    lo, hi = metrics.block_bootstrap_mean_ci(resid + beta[0], block=8, n_boot=5000)
    res = {"best_variant": f"L={int(best[0])},{best[1]}", "weekly_sr_best": float(srs[best]),
           "dsr": dsr, "pbo": pbo, "alpha_weekly": float(beta[0]), "beta": float(beta[1]),
           "alpha_ann": float(beta[0] * 52), "alpha_ci95_weekly": [lo, hi],
           "global_trials": GLOBAL_TRIALS}
    (ROOT / "reports/h002_g5.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
