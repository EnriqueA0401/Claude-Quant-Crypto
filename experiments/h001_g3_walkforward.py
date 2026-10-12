"""H001 · G3: walk-forward con purga/embargo en el periodo de desarrollo.

Uso: python3 experiments/h001_g3_walkforward.py
- Desarrollo = todo menos los últimos 12 meses (holdout, NO se toca aquí).
- 6 folds expandibles, train mínimo 2 años, embargo 1 semana.
- En cada fold se elige la variante con mejor Sharpe medio (BTC+ETH) en su train y se
  evalúa solo en el bloque de test. Mismas 6 variantes de G2 (no se añaden pruebas).
- También se aplica la variante elegida, sin rediseñar, a SOL/BNB/XRP (preliminar G4).
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
from h001_carry import HPY, VARIANTS, load  # noqa: E402
from src import metrics  # noqa: E402
from src.carry import carry_signal, run_carry  # noqa: E402
from src.costs import PERP, SPOT  # noqa: E402
from src.validation import holdout_split, walk_forward  # noqa: E402

DESIGN = ["BTCUSDT", "ETHUSDT"]
OTHERS = ["SOLUSDT", "BNBUSDT", "XRPUSDT"]
EMBARGO = 24 * 7


def full_runs(sym, cost_mult=1.0):
    perp, spot, trad, fund = load(sym)
    dev, _ = holdout_split(perp.index, 12)
    perp, spot, trad = perp[dev], spot[dev], trad[dev]
    fund = fund[fund.index <= perp.index[-1]]
    runs = {}
    for v in VARIANTS:
        sig = carry_signal(fund, perp.index, v[1], v[0])
        runs[v] = run_carry(spot, perp, fund, sig, SPOT.scaled(cost_mult),
                            PERP.scaled(cost_mult), tradable=trad,
                            liq_high=perp["mark_high"])["net"]
    return runs


def main():
    design = {s: full_runs(s) for s in DESIGN}
    design2x = {s: full_runs(s, 2.0) for s in DESIGN}
    others = {s: full_runs(s) for s in OTHERS}
    idx = design["BTCUSDT"][VARIANTS[0]].index
    for s in DESIGN:
        assert design[s][VARIANTS[0]].index.equals(idx)
    folds = walk_forward(len(idx), n_folds=6, min_train=24 * 365 * 2, horizon=1,
                         embargo=EMBARGO)
    oos, oos2x, oos_oth, fold_rep = [], [], {s: [] for s in OTHERS}, []
    for tr, te in folds:
        score = {v: np.mean([metrics.sharpe(design[s][v].iloc[tr].to_numpy()) for s in DESIGN])
                 for v in VARIANTS}
        best = max(score, key=score.get)
        t0, t1 = idx[te[0]], idx[te[-1]]
        r = pd.concat([design[s][best].iloc[te] for s in DESIGN], axis=1).mean(axis=1)
        r2 = pd.concat([design2x[s][best].iloc[te] for s in DESIGN], axis=1).mean(axis=1)
        oos.append(r)
        oos2x.append(r2)
        rec = {"test": f"{t0.date()}..{t1.date()}", "chosen": f"theta={best[0]},k={best[1]}",
               "ann_ret": float(r.mean() * HPY), "sharpe": metrics.sharpe_resampled(r)}
        for s in OTHERS:
            ro = others[s][best].loc[t0:t1]
            oos_oth[s].append(ro)
            rec[f"{s}_ann"] = float(ro.mean() * HPY) if len(ro) else None
        fold_rep.append(rec)
    r = pd.concat(oos).to_numpy()
    r2 = pd.concat(oos2x).to_numpy()
    lo, hi = metrics.block_bootstrap_mean_ci(r, block=24 * 60, n_boot=5000)
    yearly = pd.concat(oos).groupby(lambda t: t.year).sum()
    summary = {
        "portfolio": "media BTC/ETH, cada pata 50% del capital de su par",
        "oos_ann_return": float(r.mean() * HPY), "oos_sharpe": metrics.sharpe_resampled(pd.concat(oos)),
        "oos_max_dd": metrics.max_drawdown(r), "oos_ann_return_cost2x": float(r2.mean() * HPY),
        "oos_sharpe_cost2x": metrics.sharpe_resampled(pd.concat(oos2x)),
        "ci95_mean_hourly": [lo, hi], "yearly_sum": {int(k): float(v) for k, v in yearly.items()},
        "others_oos_ann": {s: float(pd.concat(v).mean() * HPY) for s, v in oos_oth.items()},
        "others_oos_sharpe": {s: metrics.sharpe_resampled(pd.concat(v))
                              for s, v in oos_oth.items()},
    }
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h001_g3.json").write_text(json.dumps(
        {"commit": commit, "folds": fold_rep, "summary": summary}, indent=1) + "\n")
    print(pd.DataFrame(fold_rep).round(4).to_string())
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
