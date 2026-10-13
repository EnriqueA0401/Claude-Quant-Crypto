"""H043 · G5: DSR (contador global), PBO-CSCV, White RC y bootstrap del retorno OOS.

Uso: python3 experiments/h043_g5.py
Familia: continuación con ventanas 3/7/14 días y reversión 7 días (todas probadas).
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
from h022_g5 import white_rc  # noqa: E402
from h043_g4 import score_w  # noqa: E402
from h043_taker_flow import HOLDOUT, make_score, taker_panel  # noqa: E402
from src import metrics  # noqa: E402

GLOBAL_TRIALS = 146
START = pd.Timestamp("2023-01-01", tz="UTC")


def main():
    o, c, h, qv, fd = h5.panel()
    tb = taker_panel(o.columns).reindex(o.index)
    end = o.index[(o.index.dayofweek == 0) & (o.index <= HOLDOUT)][-1] + pd.Timedelta("1D")
    fams = {"cont_7d": score_w(tb, qv, 7), "cont_3d": score_w(tb, qv, 3),
            "cont_14d": score_w(tb, qv, 14), "rev_7d": make_score(tb, qv, -1.0)}
    R = pd.DataFrame({k: h5.run(o, c, h, qv, fd, 1, "mom", end=end, score_fn=f)["net"]
                      for k, f in fams.items()}).dropna()
    oos = R[R.index >= START]
    srs = oos.apply(lambda col: metrics.sharpe(col.to_numpy()))
    res = {"global_trials": GLOBAL_TRIALS,
           "psr_oos": metrics.probabilistic_sharpe(oos["cont_7d"].to_numpy()),
           "dsr_oos": metrics.deflated_sharpe(oos["cont_7d"].to_numpy(), GLOBAL_TRIALS,
                                              float(srs.var(ddof=1))),
           "pbo_cscv_full": metrics.pbo_cscv(R.to_numpy(), n_splits=10),
           "white_rc_p_oos": white_rc(oos.to_numpy(), block=8),
           "bootstrap_ci95_weekly_oos": list(metrics.block_bootstrap_mean_ci(
               oos["cont_7d"].to_numpy(), block=8, n_boot=5000)),
           "weekly_sharpe_oos": {k: float(v) for k, v in srs.items()}}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h043_g5.json").write_text(json.dumps({"commit": commit, "results": res},
                                                          indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
