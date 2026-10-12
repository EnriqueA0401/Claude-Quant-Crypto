"""Backtester vectorizado de una sola serie.

Convención de tiempos (barras indexadas por open time):
- La señal de la barra t se calcula con datos hasta el CLOSE de t.
- La posición resultante se ejecuta en el OPEN de t+1 y se mantiene hasta el OPEN de t+2.
- Retorno del bar t (open-to-open): r_t = open[t+1] / open[t] - 1.
- pos[t] = señal[t-1]; pnl[t] = pos[t] * r_t - coste * |pos[t] - pos[t-1]|.
- Funding (perps): pnl[t] -= pos[t] * sum(funding con timestamp en (open[t], open[t+1]]).
  Un largo paga funding positivo; un corto lo cobra.
Las posiciones son fracciones del capital (sin apalancamiento salvo |pos| > 1).
El último bar no tiene retorno (no hay open[t+1]) y se descarta.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .costs import Costs


def run(open_: pd.Series, signal: pd.Series, costs: Costs, *,
        spot: bool = True, funding: pd.Series | None = None) -> pd.DataFrame:
    if not open_.index.equals(signal.index):
        raise ValueError("open_ y signal deben compartir índice")
    if open_.isna().any() or (open_ <= 0).any():
        raise ValueError("open_ contiene NaN o precios no positivos")
    sig = signal.astype(float).fillna(0.0)
    if spot:
        sig = sig.clip(lower=0.0)  # sin cortos en spot
    pos = sig.shift(1).fillna(0.0)
    ret = open_.shift(-1) / open_ - 1.0
    turnover = pos.diff().abs()
    turnover.iloc[0] = abs(pos.iloc[0])
    cost = turnover * costs.per_side
    fund = pd.Series(0.0, index=open_.index)
    if funding is not None and len(funding):
        if spot:
            raise ValueError("funding solo aplica a perps")
        # asigna cada evento de funding al bar t con open[t] < ts <= open[t+1]
        edges = pd.DatetimeIndex(open_.index).as_unit("ns").asi8
        ts = pd.DatetimeIndex(funding.index).as_unit("ns").asi8
        idx = np.searchsorted(edges, ts, side="left") - 1
        ok = (idx >= 0) & (idx < len(edges) - 1)
        agg = pd.Series(funding.values[ok]).groupby(idx[ok]).sum()
        fund.iloc[agg.index.values] = agg.values
    gross = pos * ret
    net = gross - cost - pos * fund
    out = pd.DataFrame({"pos": pos, "ret": ret, "gross": gross, "cost": cost,
                        "funding": pos * fund, "net": net, "turnover": turnover})
    return out.iloc[:-1]


def n_trades(pos: pd.Series) -> int:
    """Número de cambios de posición (entradas, salidas, giros)."""
    return int((pos.diff().fillna(pos.iloc[0]) != 0).sum())
