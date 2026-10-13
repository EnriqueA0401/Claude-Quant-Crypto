"""H043 · G4: costes ×2, ventanas vecinas (3 y 14 d), pares 51–100 y control de momentum.

Uso: python3 experiments/h043_g4.py
Todo en 2023-01 → 2025-09 (periodo OOS de G3), variante de continuación.
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
import h005_xs_momentum as h5  # noqa: E402
from h043_taker_flow import HOLDOUT, stats, taker_panel  # noqa: E402
from src import metrics  # noqa: E402

START = pd.Timestamp("2023-01-01", tz="UTC")


def score_w(tb, qv, days):
    def score(sun, mon, names):
        a = tb.loc[sun - pd.Timedelta(days=days - 1):sun, names].sum(min_count=max(2, days - 2))
        b = qv.loc[sun - pd.Timedelta(days=days - 1):sun, names].sum(min_count=max(2, days - 2))
        return a / b
    return score


def main():
    o, c, h, qv, fd = h5.panel()
    tb = taker_panel(o.columns).reindex(o.index)
    end = o.index[(o.index.dayofweek == 0) & (o.index <= HOLDOUT)][-1] + pd.Timedelta("1D")
    cfg = {"base_7d": dict(score_fn=score_w(tb, qv, 7)),
           "cost2x": dict(score_fn=score_w(tb, qv, 7), per_side=0.003),
           "window_3d": dict(score_fn=score_w(tb, qv, 3)),
           "window_14d": dict(score_fn=score_w(tb, qv, 14)),
           "pairs_51_100": dict(score_fn=score_w(tb, qv, 7), skip=50)}
    runs = {k: h5.run(o, c, h, qv, fd, 1, "mom", end=end, **v) for k, v in cfg.items()}
    mom = h5.run(o, c, h, qv, fd, 1, "mom", end=end)["net"]
    res = {k: stats(r["net"][r.index >= START]) for k, r in runs.items()}
    y = runs["base_7d"]["net"][runs["base_7d"].index >= START]
    x = mom.reindex(y.index).fillna(0.0)
    X = np.c_[np.ones(len(x)), x.to_numpy()]
    beta = np.linalg.lstsq(X, y.to_numpy(), rcond=None)[0]
    resid = y.to_numpy() - X @ beta
    lo, hi = metrics.block_bootstrap_mean_ci(resid + beta[0], block=8, n_boot=5000)
    res["vs_momentum"] = {"alpha_ann": float(beta[0] * 52), "beta_mom": float(beta[1]),
                          "corr": float(np.corrcoef(x, y)[0, 1]), "alpha_ci95_weekly": [lo, hi],
                          "momentum_ann_oos": float(x.mean() * 52)}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h043_g4.json").write_text(json.dumps({"commit": commit, "results": res},
                                                          indent=1) + "\n")
    for k, v in res.items():
        if k == "vs_momentum":
            print(k, {a: (round(b, 4) if isinstance(b, float) else [round(z, 4) for z in b]) for a, b in v.items()})
        else:
            print(k, round(v["ann"], 3), round(v["sharpe_m"], 2), round(v["max_dd"], 2),
                  [round(z, 4) for z in v["ci95_weekly"]], {a: round(b, 2) for a, b in v["yearly"].items()})


if __name__ == "__main__":
    main()
