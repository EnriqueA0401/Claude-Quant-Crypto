"""H015 (efecto MAX) y H016 (baja volatilidad / BAB): cartera cross-sectional mensual.

Uso: python3 experiments/h015_h016_lowrisk.py
Motor de H005 con rebalanceo cada 4 semanas. Largo = menor riesgo/MAX, corto = mayor.
Variantes fijadas en HYPOTHESES.md: H015 {MAX30, MAX5}; H016 {vol30, beta60}.
G2 = train 2020–2022; G3 = walk-forward (folds de 6 meses desde 2023) por hipótesis.
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
from src import metrics  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def scores(c):
    r = c.pct_change(fill_method=None)
    lr = np.log(c).diff()
    btc = lr["BTCUSDT"]

    def max30(sun, mon, names):
        return -r.loc[sun - pd.Timedelta("29D"):sun, names].max(min_count=20)

    def max5(sun, mon, names):
        w = r.loc[sun - pd.Timedelta("29D"):sun, names]
        return -w.apply(lambda x: x.dropna().nlargest(5).mean() if x.notna().sum() >= 20 else np.nan)

    def vol30(sun, mon, names):
        w = lr.loc[sun - pd.Timedelta("29D"):sun, names]
        return -w.std().where(w.notna().sum() >= 20)

    def beta60(sun, mon, names):
        w = lr.loc[sun - pd.Timedelta("59D"):sun, names]
        b = btc.loc[w.index]
        cov = w.apply(lambda x: x.cov(b))
        return -(cov / b.var()).where(w.notna().sum() >= 40)

    return {"H015|MAX30": max30, "H015|MAX5": max5, "H016|vol30": vol30, "H016|beta60": beta60}


def stats(r):
    lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=8, n_boot=5000)
    return {"weeks": int(len(r)), "ann": float(r.mean() * 52), "sharpe_m": metrics.sharpe_resampled(r),
            "max_dd": metrics.max_drawdown(r.to_numpy()), "ci95_weekly": [lo, hi],
            "yearly": {int(y): float(v) for y, v in r.groupby(r.index.year).sum().items()}}


def main():
    o, c, h, qv, fd = h5.panel()
    end = o.index[(o.index.dayofweek == 0) & (o.index <= HOLDOUT)][-1] + pd.Timedelta("1D")
    runs = {k: h5.run(o, c, h, qv, fd, 1, "mom", end=end, score_fn=f, every=4)
            for k, f in scores(c).items()}
    g2 = {k: stats(r["net"][r.index < TRAIN_END]) for k, r in runs.items()}
    edges = sorted(set(list(pd.date_range(pd.Timestamp("2023-01-01", tz="UTC"), HOLDOUT,
                                          freq="6MS")) + [HOLDOUT]))
    g3 = {}
    for hyp in ("H015", "H016"):
        cand = {k: r for k, r in runs.items() if k.startswith(hyp)}
        oos, folds = [], []
        for a, b in zip(edges[:-1], edges[1:]):
            sc = {k: metrics.sharpe_resampled(r["net"][r.index < a - pd.Timedelta("7D")])
                  for k, r in cand.items()}
            best = max(sc, key=sc.get)
            seg = cand[best]["net"][(cand[best].index >= a) & (cand[best].index < b)]
            oos.append(seg)
            folds.append({"test": f"{a.date()}..{b.date()}", "chosen": best,
                          "ann": float(seg.mean() * 52)})
        g3[hyp] = {"folds": folds, "summary": stats(pd.concat(oos))}
    for k, r in runs.items():
        r.to_csv(ROOT / f"reports/{k.replace('|', '_')}_dev.csv")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h015_h016.json").write_text(json.dumps(
        {"commit": commit, "g2": g2, "g3": g3}, indent=1) + "\n")
    for k, v in g2.items():
        print("G2", k, round(v["ann"], 3), round(v["sharpe_m"], 2), round(v["max_dd"], 2),
              [round(x, 4) for x in v["ci95_weekly"]])
    for k, v in g3.items():
        s = v["summary"]
        print("G3", k, [f["chosen"] for f in v["folds"]], round(s["ann"], 3), round(s["sharpe_m"], 2),
              round(s["max_dd"], 2), [round(x, 4) for x in s["ci95_weekly"]],
              {y: round(z, 2) for y, z in s["yearly"].items()})


if __name__ == "__main__":
    main()
