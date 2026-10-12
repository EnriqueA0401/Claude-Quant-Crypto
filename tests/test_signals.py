import numpy as np
import pandas as pd

from src.signals import funding_extreme_short


def _fund(n=400, seed=0):
    rng = np.random.default_rng(seed)
    ev = pd.date_range("2023-01-01", periods=n, freq="8h", tz="UTC")
    return pd.Series(rng.normal(1e-4, 1e-4, n), index=ev)


def test_trigger_timing_and_hold():
    f = pd.Series(1e-4, index=_fund().index)   # constante: los empates no disparan
    f.iloc[300] = 0.01                        # extremo claro
    idx = pd.date_range("2023-01-01", periods=400 * 8, freq="1h", tz="UTC")
    s = funding_extreme_short(f, idx, 0.99, hold=5, window=300, min_events=100)
    t = idx.get_loc(f.index[300] - pd.Timedelta("1h"))   # bar cuyo close = evento
    assert (s.iloc[t:t + 5] == -1).all() and s.iloc[t + 5] == 0
    assert s.iloc[t - 1] == 0


def test_no_lookahead():
    f = _fund(seed=1)
    idx = pd.date_range("2023-01-01", periods=400 * 8, freq="1h", tz="UTC")
    base = funding_extreme_short(f, idx, 0.9, 24, window=300, min_events=100)
    for k in [150, 250, 350]:
        alt = f.copy()
        alt.iloc[k + 1:] = np.random.default_rng(k).normal(0.01, 0.01, len(f) - k - 1)
        got = funding_extreme_short(alt, idx, 0.9, 24, window=300, min_events=100)
        cut = idx + pd.Timedelta("1h") < f.index[k + 1]   # bars que cierran antes del evento k+1
        pd.testing.assert_series_equal(base[cut], got[cut])


def test_no_overlap():
    f = pd.Series(np.r_[np.full(200, 1e-4), np.full(10, 0.01)],
                  index=pd.date_range("2023-01-01", periods=210, freq="8h", tz="UTC"))
    idx = pd.date_range("2023-01-01", periods=210 * 8, freq="1h", tz="UTC")
    s = funding_extreme_short(f, idx, 0.9, hold=72, window=200, min_events=100)
    # eventos extremos 200..209 (cada 8 h). Entrada en el bar 1599 (close = evento 200)
    # durante 72 h → ocupado hasta 1670; los eventos 201..208 se ignoran; el 209
    # (bar 1671) abre otra hasta el final de la serie (1680 bars) → 72 + 9.
    assert (s == -1).sum() == 72 + 9
    assert s.iloc[1598] == 0 and (s.iloc[1599:] == -1).all()
