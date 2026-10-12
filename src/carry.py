"""H001 · cash-and-carry: largo spot + corto perp de igual nocional.

Convenciones (mismas que src/backtest.py):
- Barras 1h indexadas por open time. La decisión del bar t usa datos hasta su close
  (= open[t+1]) y se ejecuta en open[t+1]; pos[t] = decisión[t-1].
- Funding del bar t: eventos con timestamp en (open[t], open[t+1]]. Un corto cobra
  funding positivo.
- Retornos sobre el capital total. w = fracción del capital en nocional de cada pata
  (apalancamiento 1x en el perp: w = 0,5, la otra mitad es margen del corto).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .costs import Costs


def _bar_close(index: pd.DatetimeIndex) -> np.ndarray:
    step = index[1] - index[0]
    return pd.DatetimeIndex(index + step).as_unit("ns").asi8


def carry_signal(funding: pd.Series, index: pd.DatetimeIndex, k: int,
                 theta: float) -> pd.Series:
    """1 = mantener la cobertura. Entrada si media de las últimas k tasas > theta,
    salida si < theta/2 (histéresis). Solo usa eventos con ts <= close del bar."""
    m = funding.rolling(k).mean().to_numpy()
    state = np.zeros(len(m))
    s = 0.0
    for i, v in enumerate(m):
        if np.isnan(v):
            s = 0.0
        elif v > theta:
            s = 1.0
        elif v < theta / 2:
            s = 0.0
        state[i] = s
    ev = pd.DatetimeIndex(funding.index).as_unit("ns").asi8
    j = np.searchsorted(ev, _bar_close(index), side="right") - 1
    out = np.where(j >= 0, state[np.clip(j, 0, None)], 0.0)
    return pd.Series(out, index=index)


def funding_per_bar(funding: pd.Series, index: pd.DatetimeIndex) -> np.ndarray:
    edges = pd.DatetimeIndex(index).as_unit("ns").asi8
    ts = pd.DatetimeIndex(funding.index).as_unit("ns").asi8
    idx = np.searchsorted(edges, ts, side="left") - 1
    ok = (idx >= 0) & (idx < len(edges))
    out = np.zeros(len(edges))
    np.add.at(out, idx[ok], funding.to_numpy()[ok])
    return out


def run_carry(spot_open: pd.Series, perp: pd.DataFrame, funding: pd.Series,
              signal: pd.Series, spot_costs: Costs, perp_costs: Costs, *,
              w: float = 0.5, band: float = 0.25, mmr: float = 0.005,
              tradable: pd.Series | None = None,
              liq_high: pd.Series | None = None) -> pd.DataFrame:
    """perp: DataFrame con 'open' y 'high'. spot_open alineado al mismo índice.
    liq_high: high del mark price (Binance liquida por mark price). Donde falte se usa
    el high del último precio (más pesimista).

    - tradable[t] = False congela la posición en el bar t (huecos de spot).
    - Rebalanceo: si el perp se aleja más de `band` del precio de referencia, se
      mueve band/2 del nocional en cada pata (coste w·band·(cs+cp)) y se resetea la
      referencia.
    - Liquidación: el corto 1x se liquida si el high del bar alcanza
      ref·(1 + 1/1 - mmr); se pierde todo el margen (w) y la posición se cierra.
    """
    idx = perp.index
    if not (spot_open.index.equals(idx) and signal.index.equals(idx)):
        raise ValueError("índices desalineados")
    n = len(idx)
    po, so = perp["open"].to_numpy(), spot_open.to_numpy()
    ph = perp["high"] if liq_high is None else liq_high.reindex(idx).fillna(perp["high"])
    ph = ph.to_numpy()
    fund = funding_per_bar(funding, idx)
    sig = signal.to_numpy()
    trad = np.ones(n, bool) if tradable is None else tradable.to_numpy()
    cs, cp = spot_costs.per_side, perp_costs.per_side
    rows = np.zeros((n - 1, 6))  # pos, basis, funding, cost, rebalance, liquidated
    pos, ref = 0.0, np.nan
    for t in range(n - 1):
        want = sig[t - 1] if t > 0 else 0.0
        new = want if trad[t] else pos
        cost = abs(new - pos) * w * (cs + cp)
        if new > 0 and pos == 0:
            ref = po[t]
        pos = new
        basis = fund_pnl = reb = liq = 0.0
        if pos > 0:
            if ph[t] >= ref * (2.0 - mmr):
                liq = 1.0
                basis = -w          # se pierde el margen del corto
                pos, ref = 0.0, np.nan
            else:
                rs = so[t + 1] / so[t] - 1.0
                rp = po[t + 1] / po[t] - 1.0
                basis = w * (rs - rp)
                fund_pnl = w * fund[t]
                if abs(po[t + 1] / ref - 1.0) > band:
                    reb = w * band * (cs + cp)
                    ref = po[t + 1]
        rows[t] = (pos, basis, fund_pnl, cost, reb, liq)
    out = pd.DataFrame(rows, index=idx[:-1],
                       columns=["pos", "basis", "funding", "cost", "rebalance", "liquidated"])
    out["net"] = out["basis"] + out["funding"] - out["cost"] - out["rebalance"]
    return out
