"""H039: arbitraje estadístico por pares cointegrados (perps USDT-M, diario).

Uso: python3 experiments/h039_pairs.py
"""
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h005_xs_momentum as h5  # noqa: E402
from src import metrics  # noqa: E402

COST, FORM, TRADE, NPAIRS, TOPN = 0.0015, 90, 30, 5, 20
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def adf_t(s: np.ndarray) -> float:
    """t del coeficiente de s_{t−1} en Δs_t = a + b·s_{t−1} (ADF sin retardos)."""
    ds, lag = np.diff(s), s[:-1]
    X = np.c_[np.ones_like(lag), lag]
    beta, res, *_ = np.linalg.lstsq(X, ds, rcond=None)
    resid = ds - X @ beta
    sigma2 = resid @ resid / (len(ds) - 2)
    se = np.sqrt(sigma2 * np.linalg.inv(X.T @ X)[1, 1])
    return float(beta[1] / se)


def select_pairs(lc: pd.DataFrame, names) -> list:
    out = []
    r = lc[names].diff()
    corr = r.corr()
    for a, b in combinations(names, 2):
        x = lc[[a, b]].dropna()
        if len(x) < FORM - 5 or corr.loc[a, b] < 0.7:
            continue
        beta = np.polyfit(x[b], x[a], 1)[0]
        sp = x[a] - beta * x[b]
        out.append((adf_t(sp.to_numpy()), a, b, beta, sp.mean(), sp.std()))
    return sorted(out)[:NPAIRS]


def run(o, c, qv, fd, e, end):
    lc = np.log(c)
    vol30 = qv.rolling(30, min_periods=20).sum()
    days = o.index[(o.index >= pd.Timestamp("2020-04-01", tz="UTC")) & (o.index < end)]
    pnl = pd.Series(0.0, index=days)
    starts = days[::TRADE]
    for t0 in starts:
        i0 = o.index.get_loc(t0)
        form = lc.iloc[i0 - FORM:i0]
        alive = o.loc[t0].notna() & vol30.iloc[i0 - 1].notna()
        names = list(vol30.iloc[i0 - 1][alive].nlargest(TOPN).index)
        for _, a, b, beta, mu, sd in select_pairs(form, names):
            wa, wb = 0.1 / (1 + abs(beta)), 0.1 * abs(beta) / (1 + abs(beta))
            side = 0
            for k in range(TRADE):
                i = i0 + k
                if i + 1 >= len(o.index) or o.index[i] >= end:
                    break
                # posición del día i decidida al close de i−1
                if side:
                    ra = o[a].iloc[i + 1] / o[a].iloc[i] - 1
                    rb = o[b].iloc[i + 1] / o[b].iloc[i] - 1
                    if np.isnan(ra) or np.isnan(rb):
                        pnl.iloc[pnl.index.get_loc(o.index[i])] -= (wa + wb) * COST
                        side = 0
                        break
                    fa = fd[a].iloc[i] if a in fd else 0.0
                    fb = fd[b].iloc[i] if b in fd else 0.0
                    p = side * (wa * ra - np.sign(beta) * wb * rb) - side * (wa * fa - np.sign(beta) * wb * fb)
                    pnl.iloc[pnl.index.get_loc(o.index[i])] += p
                z = (lc[a].iloc[i] - beta * lc[b].iloc[i] - mu) / sd   # close del día i
                new = side
                if side == 0 and abs(z) > e:
                    new = -int(np.sign(z))                     # z alto: A caro → corto A
                elif side != 0 and (np.sign(z) == side or np.isnan(z)):
                    new = 0
                if k == TRADE - 1:
                    new = 0
                if new != side and i + 1 < len(o.index) and o.index[i + 1] in pnl.index:
                    pnl.iloc[pnl.index.get_loc(o.index[i + 1])] -= abs(new - side) * (wa + wb) * COST
                side = new
    return pnl


def main():
    o, c, h, qv, fd = h5.panel()
    res = {}
    for e in (2.0, 2.5):
        r = run(o, c, qv, fd, e, HOLDOUT)
        for name, sel in (("train", r.index < TRAIN_END), ("oos", r.index >= TRAIN_END)):
            x = r[sel]
            lo, hi = metrics.block_bootstrap_mean_ci(x.to_numpy(), block=30, n_boot=5000)
            res[f"e={e}|{name}"] = {"ann": float(x.mean() * 365), "sharpe_m": metrics.sharpe_resampled(x),
                                    "max_dd": metrics.max_drawdown(x.to_numpy()), "ci95_daily": [lo, hi],
                                    "yearly": {int(y): float(v) for y, v in x.groupby(x.index.year).sum().items()}}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h039.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for k, v in res.items():
        print(k, round(v["ann"], 4), round(v["sharpe_m"], 2), round(v["max_dd"], 3),
              [round(x, 5) for x in v["ci95_daily"]], {y: round(z, 3) for y, z in v["yearly"].items()})


if __name__ == "__main__":
    main()
