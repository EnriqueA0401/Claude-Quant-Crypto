"""H022 · G5: DSR (contador global), PBO-CSCV, White Reality Check y bootstrap por bloques.

Uso: python3 experiments/h022_g5.py
Familia de variantes: θ ∈ {3, 5, 7 %} × salida ∈ {anticipada, vencimiento} (COIN-M, W=1),
cartera 50/50 BTC/ETH, retornos semanales 2021–2025-09. Retorno en exceso de caja: 5 %/año.
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
import h012_quarterly_basis as h12  # noqa: E402
from src import metrics  # noqa: E402

h12.W, h12.MMR = 1.0, -1e9
GLOBAL_TRIALS = 103          # contador global al ejecutar (101 + esta familia ya contada)
CASH = 0.05
START = pd.Timestamp("2023-01-01", tz="UTC")


def white_rc(excess: np.ndarray, block: int, n_boot: int = 5000, seed: int = 0) -> float:
    """p-valor del White Reality Check: H0 = ninguna variante tiene media > 0."""
    rng = np.random.default_rng(seed)
    t, k = excess.shape
    stat = np.sqrt(t) * excess.mean(axis=0).max()
    centered = excess - excess.mean(axis=0)
    nb = int(np.ceil(t / block))
    cnt = 0
    for _ in range(n_boot):
        idx = (rng.integers(0, t, nb)[:, None] + np.arange(block)[None, :]).ravel()[:t] % t
        cnt += np.sqrt(t) * centered[idx].mean(axis=0).max() >= stat
    return cnt / n_boot


def main():
    data = {b: h12.load(b, market="cm") for b in ("BTCUSD", "ETHUSD")}
    series = {}
    for th in (0.03, 0.05, 0.07):
        for ex in ("early", "expiry"):
            nets = []
            for b, (spot, futs) in data.items():
                futs = {c: f for c, f in futs.items() if len(f) and f.index[-1] < h12.HOLDOUT}
                nets.append(h12.run(spot, futs, th, ex, end=h12.HOLDOUT)["net"])
            series[f"theta={th}|{ex}"] = pd.concat(nets, axis=1).fillna(0).mean(axis=1)
    hourly = pd.DataFrame(series)
    weekly = hourly.resample("W").sum()
    excess = weekly - CASH / 52
    main_v = "theta=0.05|early"
    oos = excess[excess.index >= START]
    srs = excess.apply(lambda c: metrics.sharpe(c.to_numpy()))
    dsr_full = metrics.deflated_sharpe(excess[main_v].to_numpy(), GLOBAL_TRIALS, float(srs.var(ddof=1)))
    dsr_oos = metrics.deflated_sharpe(oos[main_v].to_numpy(), GLOBAL_TRIALS,
                                      float(oos.apply(lambda c: metrics.sharpe(c.to_numpy())).var(ddof=1)))
    psr_oos = metrics.probabilistic_sharpe(oos[main_v].to_numpy())
    pbo = metrics.pbo_cscv(excess.to_numpy(), n_splits=10)
    wrc = white_rc(oos.to_numpy(), block=13)
    lo, hi = metrics.block_bootstrap_mean_ci(oos[main_v].to_numpy(), block=13, n_boot=5000)
    lo_raw, hi_raw = metrics.block_bootstrap_mean_ci(weekly[main_v][weekly.index >= START].to_numpy(),
                                                     block=13, n_boot=5000)
    raw_oos = weekly[weekly.index >= START]
    dsr_raw = metrics.deflated_sharpe(raw_oos[main_v].to_numpy(), GLOBAL_TRIALS,
                                      float(raw_oos.apply(lambda c: metrics.sharpe(c.to_numpy())).var(ddof=1)))
    wrc_raw = white_rc(raw_oos.to_numpy(), block=13)
    res = {"variants": list(series), "dsr_oos_raw": dsr_raw, "white_rc_pvalue_oos_raw": wrc_raw,
           "psr_oos_raw": metrics.probabilistic_sharpe(raw_oos[main_v].to_numpy()), "global_trials": GLOBAL_TRIALS, "cash_hurdle": CASH,
           "oos_weekly_sharpe_excess": float(metrics.sharpe(oos[main_v].to_numpy())),
           "psr_oos_excess": psr_oos, "dsr_oos_excess": dsr_oos, "dsr_full_excess": dsr_full,
           "pbo_cscv": pbo, "white_rc_pvalue_oos_excess": wrc,
           "bootstrap_ci95_weekly_excess_oos": [lo, hi],
           "bootstrap_ci95_weekly_raw_oos": [lo_raw, hi_raw],
           "oos_ann_excess": float(oos[main_v].mean() * 52)}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h022_g5.json").write_text(json.dumps({"commit": commit, "results": res},
                                                          indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
