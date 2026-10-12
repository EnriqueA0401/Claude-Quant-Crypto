"""Métricas y tests estadísticos (G5)."""
from __future__ import annotations

from itertools import combinations

import numpy as np
from scipy import stats

EULER_GAMMA = 0.5772156649015329


def sharpe(r: np.ndarray, periods_per_year: float | None = None) -> float:
    r = np.asarray(r, float)
    sd = r.std(ddof=1)
    if sd == 0 or not np.isfinite(sd):
        return 0.0
    sr = r.mean() / sd
    return sr * np.sqrt(periods_per_year) if periods_per_year else sr


def max_drawdown(r: np.ndarray) -> float:
    """Drawdown máximo de la curva compuesta (valor negativo)."""
    eq = np.cumprod(1.0 + np.asarray(r, float))
    peak = np.maximum.accumulate(eq)
    return float((eq / peak - 1.0).min())


def probabilistic_sharpe(r: np.ndarray, sr0: float = 0.0) -> float:
    """PSR (Bailey & López de Prado 2012). sr0 en unidades por periodo."""
    r = np.asarray(r, float)
    t = len(r)
    sr = sharpe(r)
    g3 = stats.skew(r)
    g4 = stats.kurtosis(r, fisher=False)
    den = np.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
    return float(stats.norm.cdf((sr - sr0) * np.sqrt(t - 1) / den))


def expected_max_sharpe(sr_var: float, n_trials: int) -> float:
    """E[max SR] bajo H0 entre n_trials pruebas independientes."""
    if n_trials <= 1:
        return 0.0
    z = stats.norm.ppf
    return float(np.sqrt(sr_var) * ((1 - EULER_GAMMA) * z(1 - 1 / n_trials)
                                    + EULER_GAMMA * z(1 - 1 / (n_trials * np.e))))


def deflated_sharpe(r: np.ndarray, n_trials: int, sr_var: float) -> float:
    """DSR. sr_var = varianza de los SR (por periodo) entre las pruebas realizadas."""
    return probabilistic_sharpe(r, expected_max_sharpe(sr_var, n_trials))


def block_bootstrap_mean_ci(r: np.ndarray, block: int, n_boot: int = 5000,
                            alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    """IC del retorno medio por bootstrap de bloques circulares."""
    r = np.asarray(r, float)
    n = len(r)
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(n_boot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    means = r[idx.reshape(n_boot, -1)[:, :n]].mean(axis=1)
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def pbo_cscv(m: np.ndarray, n_splits: int = 16) -> float:
    """Probability of Backtest Overfitting por CSCV (Bailey et al. 2015).

    m: matriz T x N de retornos (filas = tiempo, columnas = variantes).
    """
    m = np.asarray(m, float)
    t, n = m.shape
    if n < 2:
        raise ValueError("PBO necesita al menos 2 variantes")
    blocks = np.array_split(np.arange(t), n_splits)
    logits = []
    for is_ids in combinations(range(n_splits), n_splits // 2):
        is_rows = np.concatenate([blocks[i] for i in is_ids])
        oos_rows = np.concatenate([blocks[i] for i in range(n_splits) if i not in is_ids])
        sr_is = _col_sharpe(m[is_rows])
        sr_oos = _col_sharpe(m[oos_rows])
        best = int(np.argmax(sr_is))
        rank = stats.rankdata(sr_oos)[best]          # 1..n
        w = rank / (n + 1)
        logits.append(np.log(w / (1 - w)))
    return float(np.mean(np.array(logits) <= 0))


def _col_sharpe(x: np.ndarray) -> np.ndarray:
    sd = x.std(axis=0, ddof=1)
    sd[sd == 0] = np.inf
    return x.mean(axis=0) / sd
