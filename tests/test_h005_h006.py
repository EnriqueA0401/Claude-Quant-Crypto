"""Protocolo pasos 1–3 para experiments/h005_xs_momentum.py y h006_listing.py."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import h005_xs_momentum as h5  # noqa: E402
import h006_listing as h6  # noqa: E402


def _panel(n_days=400, n_sym=12, seed=0, drift=None):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2021-01-04", periods=n_days, freq="1D", tz="UTC")  # lunes
    cols = [f"S{i}" for i in range(n_sym)]
    lr = rng.normal(0, 0.03, (n_days, n_sym))
    if drift is not None:
        lr += drift
    close = 100 * np.exp(np.cumsum(lr, axis=0))
    c = pd.DataFrame(close, index=idx, columns=cols)
    o = c.shift(1).fillna(100.0)          # open del día = close del día anterior
    h = np.maximum(o, c)
    qv = pd.DataFrame(1e6, index=idx, columns=cols)
    fd = pd.DataFrame(0.0, index=idx, columns=cols)
    return o, c, h, qv, fd


def test_h005_hand_pnl_known_ranking():
    # retornos deterministas: S_i sube i*0.1 % al día → ranking estable y PnL calculable
    n_days, n_sym = 200, 12
    idx = pd.date_range("2021-01-04", periods=n_days, freq="1D", tz="UTC")
    g = np.array([1 + 0.001 * i for i in range(n_sym)])
    c = pd.DataFrame(100 * g[None, :] ** np.arange(1, n_days + 1)[:, None], index=idx,
                     columns=[f"S{i}" for i in range(n_sym)])
    o = c.shift(1).fillna(100.0)
    h = np.maximum(o, c)
    qv = pd.DataFrame(1e6, index=idx, columns=c.columns)
    fd = pd.DataFrame(0.0, index=idx, columns=c.columns)
    df = h5.run(o, c, h, qv, fd, 1, "mom")
    wk = df.iloc[1]                                    # semana sin cambio de cartera
    exp = 0.1 * sum(g[i] ** 7 - 1 for i in range(7, 12)) - 0.1 * sum(g[i] ** 7 - 1 for i in range(5))
    assert wk["gross"] == pytest.approx(exp, rel=1e-12)
    assert wk["cost"] == 0
    assert df["cost"].iloc[0] == pytest.approx(1.0 * h5.PER_SIDE)   # entrada: 10 × 0,1


def test_h005_no_lookahead():
    o, c, h, qv, fd = _panel(seed=1)
    base = h5.run(o, c, h, qv, fd, 2, "mom")
    cut = base.index[10]
    # alterar todo lo posterior al domingo previo a `cut` (close) no cambia la cartera
    # elegida en `cut`; comparamos el coste (depende solo de los pesos hasta `cut`)
    alt = [x.copy() for x in (o, c, h, qv, fd)]
    rng = np.random.default_rng(5)
    for x in alt[:3]:
        x.loc[cut:] *= rng.lognormal(0, 0.3, x.loc[cut:].shape)
    got = h5.run(*alt, 2, "mom")
    pd.testing.assert_series_equal(base["cost"].loc[:cut], got["cost"].loc[:cut])
    pd.testing.assert_series_equal(base["gross"].loc[:cut - pd.Timedelta("8D")],
                                   got["gross"].loc[:cut - pd.Timedelta("8D")])


def test_h005_null_loses_costs():
    o, c, h, qv, fd = _panel(n_days=1500, seed=2)
    df = h5.run(o, c, h, qv, fd, 1, "mom")
    se = df["gross"].std() / np.sqrt(len(df))
    assert abs(df["gross"].mean()) < 4 * se
    assert df["net"].mean() < df["gross"].mean()


def test_h006_event_return_hand():
    idx = pd.date_range("2021-03-01", periods=10, freq="1D", tz="UTC")
    k = pd.DataFrame({"open": [10, 10, 9, 8, 8, 8, 8, 8, 8, 8.0],
                      "close": [10, 9, 8, 8, 8, 8, 8, 8, 8, 8.0],
                      "high": [10, 10, 10, 9, 8, 8, 8, 8, 8, 8.0]}, index=idx)
    f = pd.Series([0.001, 0.002], index=[idx[1] + pd.Timedelta("8h"), idx[5]])
    r = h6.event_return(k, f, start=1, n=3)       # open día 1 (10) → open día 4 (8)
    assert r["gross"] == pytest.approx(0.2)
    assert r["funding"] == pytest.approx(0.001)   # el de idx[5] cae fuera (t1 = idx[4])
    assert r["net"] == pytest.approx(0.2 + 0.001 - 2 * (h6.FEE + h6.SLIP))


def test_h006_liquidation_and_delisting():
    idx = pd.date_range("2021-03-01", periods=4, freq="1D", tz="UTC")
    k = pd.DataFrame({"open": [10, 10, 12, 12.0], "close": [10, 12, 12, 13.0],
                      "high": [10, 20, 12, 13.0]}, index=idx)
    assert h6.event_return(k, None, 1, 2)["net"] == -1.0
    k2 = k.assign(high=k[["open", "close"]].max(axis=1))
    r = h6.event_return(k2, None, 2, 30)          # se deslista: sale al último close
    assert r["gross"] == pytest.approx(-(13 / 12 - 1))


def test_h006_stop_fill_gap_and_level():
    idx = pd.date_range("2021-03-01", periods=5, freq="1D", tz="UTC")
    k = pd.DataFrame({"open": [10, 10, 11, 15, 15.0], "close": [10, 11, 15, 15, 15.0],
                      "high": [10, 12, 12, 16, 15.0]}, index=idx)
    r = h6.event_return(k, None, 1, 4, stop=0.3)   # nivel 13: se toca el día 3 con gap (open 15)
    assert r["gross"] == pytest.approx(-(15 * (1 + h6.SLIP) / 10 - 1))
    r2 = h6.event_return(k, None, 1, 4, stop=0.15)  # nivel 11.5: día 1 (high 12, open 10)
    assert r2["gross"] == pytest.approx(-(11.5 * (1 + h6.SLIP) / 10 - 1))
