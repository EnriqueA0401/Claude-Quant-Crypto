"""H043: ratio de compras agresivas (taker buy) semanal como señal cross-sectional.

Uso: python3 experiments/h043_taker_flow.py
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
from src.data import DATA, load_klines  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def taker_panel(cols):
    tb = {}
    for s in cols:
        k = load_klines("um", s, "1d")
        tb[s] = k["taker_buy_quote"].where(k["quote_volume"] > 0)
    return pd.DataFrame(tb).sort_index()


def make_score(tb, qv, sign):
    def score(sun, mon, names):
        a = tb.loc[sun - pd.Timedelta("6D"):sun, names].sum(min_count=5)
        b = qv.loc[sun - pd.Timedelta("6D"):sun, names].sum(min_count=5)
        return sign * (a / b)
    return score


def stats(r):
    lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=8, n_boot=5000)
    return {"weeks": int(len(r)), "ann": float(r.mean() * 52), "sharpe_m": metrics.sharpe_resampled(r),
            "max_dd": metrics.max_drawdown(r.to_numpy()), "ci95_weekly": [lo, hi],
            "yearly": {int(y): float(v) for y, v in r.groupby(r.index.year).sum().items()}}


def main():
    o, c, h, qv, fd = h5.panel()
    tb = taker_panel(o.columns).reindex(o.index)
    end = o.index[(o.index.dayofweek == 0) & (o.index <= HOLDOUT)][-1] + pd.Timedelta("1D")
    runs = {name: h5.run(o, c, h, qv, fd, 1, "mom", end=end, score_fn=make_score(tb, qv, sg))
            for name, sg in (("cont", 1.0), ("rev", -1.0))}
    g2 = {k: stats(r["net"][r.index < TRAIN_END]) for k, r in runs.items()}
    edges = sorted(set(list(pd.date_range(pd.Timestamp("2023-01-01", tz="UTC"), HOLDOUT, freq="6MS")) + [HOLDOUT]))
    oos, folds = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        sc = {k: metrics.sharpe_resampled(r["net"][r.index < a - pd.Timedelta("7D")]) for k, r in runs.items()}
        best = max(sc, key=sc.get)
        seg = runs[best]["net"][(runs[best].index >= a) & (runs[best].index < b)]
        oos.append(seg)
        folds.append({"test": f"{a.date()}..{b.date()}", "chosen": best, "ann": float(seg.mean() * 52)})
    g3 = {"folds": folds, "summary": stats(pd.concat(oos))}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h043.json").write_text(json.dumps({"commit": commit, "g2": g2, "g3": g3},
                                                       indent=1) + "\n")
    for k, v in g2.items():
        print("G2", k, round(v["ann"], 3), round(v["sharpe_m"], 2), round(v["max_dd"], 2),
              [round(x, 4) for x in v["ci95_weekly"]])
    s = g3["summary"]
    print("G3", [f["chosen"] for f in folds], round(s["ann"], 3), round(s["sharpe_m"], 2),
          round(s["max_dd"], 2), [round(x, 4) for x in s["ci95_weekly"]],
          {y: round(z, 2) for y, z in s["yearly"].items()})


if __name__ == "__main__":
    main()
