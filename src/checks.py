"""Comprobaciones reutilizables del protocolo de revisión (pasos 2 y 3)."""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd


def assert_no_lookahead(signal_fn: Callable[[pd.DataFrame], pd.Series],
                        df: pd.DataFrame, cut_points, seed: int = 0) -> None:
    """Altera los datos posteriores a cada t y exige señales idénticas hasta t."""
    rng = np.random.default_rng(seed)
    base = signal_fn(df)
    for t in cut_points:
        alt = df.copy()
        num = alt.select_dtypes("number").columns
        noise = rng.lognormal(0, 0.5, size=(len(alt) - t - 1, len(num)))
        alt.iloc[t + 1:, [alt.columns.get_loc(c) for c in num]] *= noise
        got = signal_fn(alt)
        pd.testing.assert_series_equal(base.iloc[:t + 1], got.iloc[:t + 1],
                                       check_names=False)
