"""H002 · G3: walk-forward con embargo en desarrollo (holdout de 12 meses intacto).

Uso: python3 experiments/h002_g3_walkforward.py
6 folds expandibles, train mínimo 2 años, embargo 7 días. En cada fold se elige la
variante con mejor Sharpe medio BTC+ETH en su train. Referencia: buy & hold del perp.
Se aplica también, sin rediseñar, a SOL/BNB/XRP.
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
from h002_tsmom import DPY, VARIANTS, daily, run_variant  # noqa: E402
from src import backtest, metrics  # noqa: E402
from src.costs import PERP  # noqa: E402
from src.validation import holdout_split, walk_forward  # noqa: E402

DESIGN = ["BTCUSDT", "ETHUSDT"]
OTHERS = ["SOLUSDT", "BNBUSDT", "XRPUSDT"]


def dev_data(sym):
    d, fund = daily(sym)
    dev, _ = holdout_split(d.index, 12)
    d = d[dev]
    return d, fund[fund.index <= d.index[-1] + pd.Timedelta("1D")]


def all_runs(sym, cost_mult=1.0):
    d, fund = dev_data(sym)
    runs = {v: run_variant(d, fund, *v, cost_mult=cost_mult)[0] for v in VARIANTS}
    bh = backtest.run(d["open"], pd.Series(1.0, index=d.index), PERP, spot=False,
                      funding=fund)
    return runs, bh


def main():
    des = {s: all_runs(s) for s in DESIGN}
    des2 = {s: all_runs(s, 2.0)[0] for s in DESIGN}
    oth = {s: all_runs(s) for s in OTHERS}
    idx = des["BTCUSDT"][0][VARIANTS[0]].index.intersection(des["ETHUSDT"][0][VARIANTS[0]].index)
    folds = walk_forward(len(idx), n_folds=6, min_train=365 * 2, horizon=1, embargo=7)
    oos, oos2, bh, rep, oth_oos = [], [], [], [], {s: [] for s in OTHERS}
    for tr, te in folds:
        tri, tei = idx[tr], idx[te]
        score = {v: np.mean([metrics.sharpe_resampled(des[s][0][v]["net"].loc[tri])
                             for s in DESIGN]) for v in VARIANTS}
        best = max(score, key=score.get)
        r = pd.concat([des[s][0][best]["net"].loc[tei] for s in DESIGN], axis=1).mean(axis=1)
        r2 = pd.concat([des2[s][best]["net"].loc[tei] for s in DESIGN], axis=1).mean(axis=1)
        b = pd.concat([des[s][1]["net"].loc[tei] for s in DESIGN], axis=1).mean(axis=1)
        trades = sum(backtest.n_trades(des[s][0][best]["pos"].loc[tei]) for s in DESIGN)
        oos.append(r), oos2.append(r2), bh.append(b)
        rec = {"test": f"{tei[0].date()}..{tei[-1].date()}", "chosen": f"L={best[0]},{best[1]}",
               "ann": float(r.mean() * DPY), "bh_ann": float(b.mean() * DPY), "trades": trades}
        for s in OTHERS:
            ro = oth[s][0][best]["net"].reindex(tei).dropna()
            oth_oos[s].append(ro)
        rep.append(rec)
    R, R2, B = pd.concat(oos), pd.concat(oos2), pd.concat(bh)
    lo, hi = metrics.block_bootstrap_mean_ci(R.to_numpy(), block=60, n_boot=5000)
    summ = {
        "oos_ann": float(R.mean() * DPY), "oos_sharpe": metrics.sharpe_resampled(R),
        "oos_mdd": metrics.max_drawdown(R.to_numpy()), "oos_trades": int(sum(x["trades"] for x in rep)),
        "oos_ann_cost2x": float(R2.mean() * DPY), "oos_sharpe_cost2x": metrics.sharpe_resampled(R2),
        "bh_ann": float(B.mean() * DPY), "bh_sharpe": metrics.sharpe_resampled(B),
        "bh_mdd": metrics.max_drawdown(B.to_numpy()),
        "ci95_mean_daily": [lo, hi],
        "yearly": {int(k): float(v) for k, v in R.groupby(R.index.year).sum().items()},
        "yearly_bh": {int(k): float(v) for k, v in B.groupby(B.index.year).sum().items()},
        "others_ann": {s: float(pd.concat(v).mean() * DPY) for s, v in oth_oos.items()},
        "others_sharpe": {s: metrics.sharpe_resampled(pd.concat(v)) for s, v in oth_oos.items()},
    }
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h002_g3.json").write_text(json.dumps(
        {"commit": commit, "folds": rep, "summary": summ}, indent=1) + "\n")
    print(pd.DataFrame(rep).round(3).to_string())
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
