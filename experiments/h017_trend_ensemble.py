"""H017: tendencia multi-moneda largo/plano (ensemble Donchian, tamaño por volatilidad).

Uso: python3 experiments/h017_trend_ensemble.py
Diseño fijado en HYPOTHESES.md. Variantes: rebalanceo diario / semanal.
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

LOOKBACKS = (10, 20, 40, 80, 160)
TOP, VOL_TGT, COST = 20, 0.008, 0.0015
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def donchian_state(close: pd.Series, L: int) -> pd.Series:
    """1 tras romper el máximo de los L closes previos; 0 tras perder el mínimo de L/2."""
    hi = close.shift(1).rolling(L, min_periods=L).max()
    lo = close.shift(1).rolling(L // 2, min_periods=L // 2).min()
    st = np.zeros(len(close))
    cur = 0.0
    for i, (x, a, b) in enumerate(zip(close.to_numpy(), hi.to_numpy(), lo.to_numpy())):
        if np.isnan(x):
            cur = 0.0
        elif not np.isnan(a) and x > a:
            cur = 1.0
        elif not np.isnan(b) and x < b:
            cur = 0.0
        st[i] = cur
    return pd.Series(st, index=close.index)


def target_weights(c, qv):
    """Pesos objetivo decididos al close del día d (solo datos hasta d)."""
    vol30 = qv.rolling(30, min_periods=20).sum()
    inuni = vol30.rank(axis=1, ascending=False) <= TOP
    sig = pd.DataFrame({s: np.mean([donchian_state(c[s], L) for L in LOOKBACKS], axis=0)
                        for s in c.columns}, index=c.index)
    sd = np.log(c).diff().rolling(60, min_periods=40).std()
    scale = (VOL_TGT / sd).clip(upper=1.0)
    return (sig * scale * inuni / TOP).fillna(0.0)


def backtest(o, c, fd, w_target, weekly):
    w = w_target.copy()
    if weekly:   # solo se actualiza al close del domingo (ejecución el lunes)
        keep = w.index.dayofweek == 6
        w = w.where(pd.Series(keep, index=w.index), np.nan).ffill().fillna(0.0)
    pos = w.shift(1).fillna(0.0)                        # ejecutado en el open del día
    ret = (o.shift(-1) / o - 1)
    dead = ret.isna() & (pos > 0)                       # deslistado/suspendido: sale al último precio
    pos = pos.where(~dead, 0.0)
    gross = (pos * ret.fillna(0.0)).sum(axis=1)
    fund = (pos * fd.reindex(pos.index).reindex(columns=pos.columns).fillna(0.0)).sum(axis=1)
    cost = pos.diff().abs().sum(axis=1) * COST
    net = (gross - fund - cost).iloc[:-1]
    return pd.DataFrame({"net": net, "gross": gross.iloc[:-1], "funding": fund.iloc[:-1],
                         "cost": cost.iloc[:-1], "exposure": pos.sum(axis=1).iloc[:-1]})


def stats(r, bh):
    lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=30, n_boot=5000)
    X = np.c_[np.ones(len(r)), bh.reindex(r.index).fillna(0).to_numpy()]
    beta = np.linalg.lstsq(X, r.to_numpy(), rcond=None)[0]
    resid = r.to_numpy() - X @ beta
    alo, ahi = metrics.block_bootstrap_mean_ci(resid + beta[0], block=30, n_boot=5000)
    return {"ann": float(r.mean() * 365), "sharpe_m": metrics.sharpe_resampled(r),
            "max_dd": metrics.max_drawdown(r.to_numpy()), "ci95_daily": [lo, hi],
            "alpha_ann": float(beta[0] * 365), "beta_btc": float(beta[1]),
            "alpha_ci95_daily": [alo, ahi],
            "yearly": {int(y): float(v) for y, v in r.groupby(r.index.year).sum().items()}}


def main():
    o, c, h, qv, fd = h5.panel()
    o, c, qv = (x[x.index < HOLDOUT] for x in (o, c, qv))
    wt = target_weights(c, qv)
    bh = (o["BTCUSDT"].shift(-1) / o["BTCUSDT"] - 1)
    res = {}
    for name, weekly in (("daily", False), ("weekly", True)):
        bt = backtest(o, c, fd, wt, weekly)
        res[name] = {"train": stats(bt["net"][bt.index < TRAIN_END], bh),
                     "oos": stats(bt["net"][bt.index >= TRAIN_END], bh),
                     "avg_exposure": float(bt["exposure"].mean()),
                     "cost_ann": float(bt["cost"].mean() * 365)}
    best = max(res, key=lambda k: res[k]["train"]["sharpe_m"])
    res["chosen_on_train"] = best
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h017.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for k in ("daily", "weekly"):
        for part in ("train", "oos"):
            v = res[k][part]
            print(k, part, round(v["ann"], 3), round(v["sharpe_m"], 2), round(v["max_dd"], 2),
                  "alpha", round(v["alpha_ann"], 3), "beta", round(v["beta_btc"], 2),
                  [round(x, 5) for x in v["alpha_ci95_daily"]], {y: round(z, 2) for y, z in v["yearly"].items()})
    print("elegida en train:", best)


if __name__ == "__main__":
    main()
