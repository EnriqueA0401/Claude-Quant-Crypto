"""Particiones para G2/G3: holdout final y walk-forward con purga y embargo."""
from __future__ import annotations

import numpy as np
import pandas as pd


def holdout_split(index: pd.DatetimeIndex, months: int = 12) -> tuple[np.ndarray, np.ndarray]:
    """Máscaras (desarrollo, holdout). El holdout son los últimos `months` meses."""
    cut = index.max() - pd.DateOffset(months=months)
    hold = np.asarray(index > cut)
    return ~hold, hold


def walk_forward(n: int, n_folds: int, min_train: int, horizon: int = 1,
                 embargo: int = 0, expanding: bool = True) -> list[tuple[np.ndarray, np.ndarray]]:
    """Folds (train, test) en posiciones 0..n-1 del periodo de DESARROLLO.

    - Los bloques de test son contiguos y cubren [min_train, n).
    - Purga: se quitan del train las últimas `horizon` observaciones (sus etiquetas
      miran hasta `horizon` bars hacia delante y solaparían con el test).
    - Embargo: hueco adicional de `embargo` bars entre train y test.
    - expanding=False usa una ventana de train de longitud fija `min_train`.
    """
    if min_train + n_folds > n:
        raise ValueError("no hay datos suficientes para los folds pedidos")
    bounds = np.linspace(min_train, n, n_folds + 1).astype(int)
    folds = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        end = a - horizon - embargo
        start = 0 if expanding else max(0, a - min_train)
        if end <= start:
            raise ValueError("purga + embargo dejan el train vacío")
        folds.append((np.arange(start, end), np.arange(a, b)))
    return folds
