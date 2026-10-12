"""H010 · G2/G3: prima de alto volumen cross-sectional semanal (perps USDT-M).

Uso: python3 experiments/h010_volume.py [g3]
Variantes fijadas en HYPOTHESES.md: B ∈ {4, 12} semanas de base.
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
from src import metrics  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")
BASES = (4, 12)


def make_score(qv, base):
    def score(sun, mon, names):
        last = qv.loc[sun - pd.Timedelta("6D"):sun, names].sum(min_count=7)
        prev = qv.loc[sun - pd.Timedelta(days=7 * (base + 1) - 1):sun - pd.Timedelta("7D"),
                      names]
        base_mean = prev.sum(min_count=7 * base) / base
        return (last / base_mean).replace([float("inf")], float("nan"))
    return score


def summarize(r):
    lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=8, n_boot=5000)
    return {"weeks": int(len(r)), "ann": float(r.mean() * 52),
            "sharpe_m": metrics.sharpe_resampled(r), "max_dd": metrics.max_drawdown(r.to_numpy()),
            "ci95_weekly": [lo, hi],
            "yearly": {int(y): float(v) for y, v in r.groupby(r.index.year).sum().items()}}


def main(g3=False):
    o, c, h, qv, fd = h5.panel()
    end = TRAIN_END
    if g3:
        end = o.index[(o.index.dayofweek == 0) & (o.index <= HOLDOUT)][-1] + pd.Timedelta("1D")
    runs = {b: h5.run(o, c, h, qv, fd, 1, "mom", end=end, score_fn=make_score(qv, b))
            for b in BASES}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    if not g3:
        res = {f"B={b}": summarize(r["net"]) for b, r in runs.items()}
        (ROOT / "reports/h010_g2.json").write_text(json.dumps(
            {"commit": commit, "variants": len(BASES), "results": res}, indent=1) + "\n")
        print(json.dumps(res, indent=1))
        return
    edges = sorted(set(list(pd.date_range(pd.Timestamp("2023-01-01", tz="UTC"), HOLDOUT,
                                          freq="6MS")) + [HOLDOUT]))
    oos, folds = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        sc = {k: metrics.sharpe_resampled(r["net"][r.index < a - pd.Timedelta("7D")])
              for k, r in runs.items()}
        best = max(sc, key=sc.get)
        seg = runs[best]["net"][(runs[best].index >= a) & (runs[best].index < b)]
        oos.append(seg)
        folds.append({"test": f"{a.date()}..{b.date()}", "chosen": f"B={best}",
                      "ann": float(seg.mean() * 52)})
    summ = summarize(pd.concat(oos))
    (ROOT / "reports/h010_g3.json").write_text(json.dumps(
        {"commit": commit, "folds": folds, "summary": summ}, indent=1) + "\n")
    print(json.dumps({"folds": folds, "summary": summ}, indent=1))


if __name__ == "__main__":
    main(g3=len(sys.argv) > 1 and sys.argv[1] == "g3")
