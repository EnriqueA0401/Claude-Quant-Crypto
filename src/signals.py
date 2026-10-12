"""Señales. Cada función usa solo datos hasta el close del bar t."""
from __future__ import annotations

import numpy as np
import pandas as pd


def ts_momentum(df: pd.DataFrame, lookback: int) -> pd.Series:
    """Signo del retorno close-to-close de los últimos `lookback` bars."""
    r = df["close"] / df["close"].shift(lookback) - 1.0
    return np.sign(r).fillna(0.0)
