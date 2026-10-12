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


def liquidation_rebound_long(df: pd.DataFrame, k: float, hold: int,
                             window: int = 720, oi_q: float = 0.05) -> pd.Series:
    """H004: +1 durante `hold` barras tras una caída ≤ −k·σ con caída fuerte de OI.

    df: barras 1h con 'close' y 'oi' (OI al final de la hora, solo snapshots < close).
    σ y el percentil de ΔOI se calculan con las `window` barras ANTERIORES a t.
    El evento del bar t (conocido en su close) activa sig[t..t+hold-1]; sin solapamiento.
    """
    r = df["close"].pct_change()
    doi = df["oi"].pct_change()
    sigma = r.rolling(window, min_periods=window // 2).std().shift(1)
    q = doi.rolling(window, min_periods=window // 2).quantile(oi_q).shift(1)
    trig = ((r <= -k * sigma) & (doi <= q)).to_numpy()
    sig = np.zeros(len(df))
    starts, busy_until = [], -1
    for t in np.flatnonzero(trig):
        if t <= busy_until:
            continue
        sig[t:t + hold] = 1.0
        starts.append(int(t))
        busy_until = t + hold - 1
    out = pd.Series(sig, index=df.index)
    out.attrs["starts"] = starts
    return out
