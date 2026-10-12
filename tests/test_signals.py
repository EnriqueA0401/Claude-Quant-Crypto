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


from src.signals import liquidation_rebound_long  # noqa: E402


def _bars(n=3000, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-01", periods=n, freq="1h", tz="UTC")
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.005, n)))
    oi = 1e5 * np.exp(np.cumsum(rng.normal(0, 0.003, n)))
    return pd.DataFrame({"close": close, "oi": oi}, index=idx)


def test_rebound_trigger_and_hold():
    df = _bars()
    df.iloc[2000:, 0] *= 0.9          # caída del 10 % en el bar 2000
    df.iloc[2000:, 1] *= 0.8          # OI cae 20 %
    s = liquidation_rebound_long(df, k=4, hold=6)
    assert 2000 in s.attrs["starts"]
    assert (s.iloc[2000:2006] == 1).all() and s.iloc[2006] == 0


def test_rebound_no_lookahead():
    df = _bars(seed=3)
    base = liquidation_rebound_long(df, 3, 24)
    for t in [800, 1500, 2500]:
        alt = df.copy()
        alt.iloc[t + 1:] *= np.random.default_rng(t).lognormal(0, 0.2, (len(df) - t - 1, 2))
        got = liquidation_rebound_long(alt, 3, 24)
        pd.testing.assert_series_equal(base.iloc[:t + 1], got.iloc[:t + 1])


def test_h009_basis_signal_timing_and_lookahead():
    import sys as _s
    from pathlib import Path as _P
    _s.path.insert(0, str(_P(__file__).resolve().parents[1] / "experiments"))
    import h009_basis as h9
    rng = np.random.default_rng(0)
    idx = pd.date_range("2022-01-01", periods=2000, freq="1h", tz="UTC")
    b = pd.Series(rng.normal(0, 1e-4, 2000), index=idx)
    b.iloc[1500] = 0.01                                  # pico extremo
    s = h9.basis_signal(b, 0.99, 8)
    assert s.iloc[1500] == 1 and s.iloc[1499] == 0       # decide al close del pico
    assert s.iloc[1500:1520].sum() <= 9                  # sale por H o mediana
    alt = b.copy()
    alt.iloc[1501:] = 0.05
    s2 = h9.basis_signal(alt, 0.99, 8)
    pd.testing.assert_series_equal(s.iloc[:1501], s2.iloc[:1501])
