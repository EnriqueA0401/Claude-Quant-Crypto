"""Señales. Cada función usa solo datos hasta el close del bar t."""
from __future__ import annotations

import numpy as np
import pandas as pd


def ts_momentum(df: pd.DataFrame, lookback: int) -> pd.Series:
    """Signo del retorno close-to-close de los últimos `lookback` bars."""
    r = df["close"] / df["close"].shift(lookback) - 1.0
    return np.sign(r).fillna(0.0)


def funding_extreme_short(funding: pd.Series, index: pd.DatetimeIndex, pct: float,
                          hold: int, window: int = 1095, min_events: int = 270,
                          bar: pd.Timedelta = pd.Timedelta("1h")) -> pd.Series:
    """H003: -1 durante `hold` barras tras un funding en su percentil >= pct.

    El percentil del evento i = fracción de los eventos [i-window+1, i] estrictamente
    menores que él (solo pasado y el propio evento, conocido en su timestamp). Con
    empates (funding fijo en 0,01 %) el percentil no sube, así que no dispara. El evento con ts = close del bar t
    activa sig[t..t+hold-1]; con la convención pos[t] = sig[t-1] la posición se mantiene
    exactamente `hold` barras. No se solapan operaciones.
    """
    v = funding.to_numpy()
    rank = pd.Series(v).rolling(window, min_periods=min_events).apply(
        lambda x: (x < x[-1]).mean(), raw=True).to_numpy()   # estricto: empates no disparan
    trig = (rank >= pct) & (v > 0)
    closes = pd.DatetimeIndex(index + bar).as_unit("ns").asi8
    ev = pd.DatetimeIndex(funding.index).as_unit("ns").asi8
    sig = np.zeros(len(index))
    starts = []
    busy_until = -1
    for i in np.flatnonzero(trig):
        t = int(np.searchsorted(closes, ev[i], side="left"))   # primer bar con close >= ts
        if t >= len(index) or t <= busy_until:
            continue
        sig[t:t + hold] = -1.0
        starts.append(t)
        busy_until = t + hold - 1
    out = pd.Series(sig, index=index)
    out.attrs["starts"] = starts   # bar de decisión de cada operación (pos desde t+1)
    return out
