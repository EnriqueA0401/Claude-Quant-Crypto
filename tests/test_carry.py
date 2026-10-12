"""Protocolo pasos 1–3 para src/carry.py."""
import numpy as np
import pandas as pd
import pytest

from src.carry import carry_signal, funding_per_bar, run_carry
from src.costs import Costs

IDX = pd.date_range("2024-01-01", periods=6, freq="1h", tz="UTC")
CS = Costs(0.001, 0.0005)   # 0,15% por lado
CP = Costs(0.0005, 0.0005)  # 0,10% por lado


def _perp(opens, highs=None):
    o = pd.Series(opens, index=IDX, dtype=float)
    return pd.DataFrame({"open": o, "high": o if highs is None else pd.Series(highs, index=IDX)})


def test_hand_pnl_flat_prices():
    perp = _perp([100] * 6)
    spot = pd.Series(100.0, index=IDX)
    fund = pd.Series([0.001], index=[IDX[2] + pd.Timedelta("30min")])
    sig = pd.Series([1, 1, 1, 0, 0, 0], index=IDX, dtype=float)
    out = run_carry(spot, perp, fund, sig, CS, CP, w=0.5)
    # pos=[0,1,1,1,0]; entrada t1 y salida t4 cuestan 0.5*0.0025; funding en t2
    assert out["pos"].tolist() == [0, 1, 1, 1, 0]
    assert out["net"].tolist() == pytest.approx([0, -0.00125, 0.0005, 0, -0.00125], abs=1e-15)


def test_hand_pnl_basis():
    perp = _perp([100, 100, 110, 110, 110, 110])
    spot = pd.Series([100, 100, 111, 111, 111, 111], index=IDX, dtype=float)
    sig = pd.Series([1, 1, 1, 1, 1, 1], index=IDX, dtype=float)
    out = run_carry(spot, perp, pd.Series(dtype=float, index=pd.DatetimeIndex([], tz="UTC")),
                    sig, Costs(0, 0), Costs(0, 0), w=0.5)
    # bar 1: spot +11%, perp +10% → basis 0.5*0.01
    assert out["basis"].iloc[1] == pytest.approx(0.005)


def test_liquidation_loses_margin():
    perp = _perp([100, 100, 100, 100, 100, 100], highs=[100, 100, 199.6, 100, 100, 100])
    spot = pd.Series(100.0, index=IDX)
    sig = pd.Series(1.0, index=IDX)
    out = run_carry(spot, perp, pd.Series(dtype=float, index=pd.DatetimeIndex([], tz="UTC")),
                    sig, Costs(0, 0), Costs(0, 0), w=0.5, mmr=0.005)
    assert out["liquidated"].iloc[2] == 1 and out["net"].iloc[2] == -0.5


def test_tradable_freezes_position():
    perp = _perp([100] * 6)
    spot = pd.Series(100.0, index=IDX)
    sig = pd.Series([1, 1, 1, 1, 1, 1], index=IDX, dtype=float)
    trad = pd.Series([True, False, True, True, True, True], index=IDX)
    out = run_carry(spot, perp, pd.Series(dtype=float, index=pd.DatetimeIndex([], tz="UTC")),
                    sig, CS, CP, tradable=trad)
    assert out["pos"].tolist() == [0, 0, 1, 1, 1]


def test_funding_per_bar_boundaries():
    fund = pd.Series([1.0, 2.0, 4.0], index=[IDX[1], IDX[1] + pd.Timedelta("1min"), IDX[5]])
    assert funding_per_bar(fund, IDX).tolist() == [1, 2, 0, 0, 4, 0]


def test_signal_hysteresis_and_timing():
    ev = pd.date_range("2024-01-01 00:00", periods=4, freq="2h", tz="UTC")
    fund = pd.Series([0.0003, 0.00015, 0.00004, 0.0003], index=ev)
    idx = pd.date_range("2024-01-01", periods=8, freq="1h", tz="UTC")
    s = carry_signal(fund, idx, k=1, theta=0.0002)
    # el bar t ve los eventos con ts <= su close: el bar 00:00 (close 01:00) ve 00:00
    # 02:00 (0.00015) está en la banda → mantiene; 04:00 (<θ/2) sale; 06:00 entra
    assert s.tolist() == [1, 1, 1, 0, 0, 1, 1, 1]


def test_signal_no_lookahead():
    rng = np.random.default_rng(0)
    idx = pd.date_range("2023-01-01", periods=600, freq="1h", tz="UTC")
    ev = pd.date_range("2023-01-01", periods=75, freq="8h", tz="UTC")
    df = pd.DataFrame({"rate": rng.normal(0.0001, 0.0002, 75)}, index=ev)

    # alterar eventos posteriores al evento t no cambia la señal hasta ese evento
    base = carry_signal(df["rate"], idx, 3, 0.0001)
    for t in [10, 40, 70]:
        alt = df.copy()
        alt.iloc[t + 1:, 0] = rng.normal(0.01, 0.01, len(alt) - t - 1)
        got = carry_signal(alt["rate"], idx, 3, 0.0001)
        cut = idx < ev[t + 1] - pd.Timedelta("1h")   # bars cuyo close < evento t+1
        pd.testing.assert_series_equal(base[cut], got[cut])


@pytest.mark.parametrize("seed", [0, 1])
def test_null_random_signal_zero_funding_loses_costs(seed):
    rng = np.random.default_rng(seed)
    n = 20_000
    idx = pd.date_range("2022-01-01", periods=n, freq="1h", tz="UTC")
    p = 100 * np.exp(np.cumsum(rng.normal(0, 0.005, n)))
    noise = np.exp(rng.normal(0, 0.0005, n))
    perp = pd.DataFrame({"open": p, "high": p}, index=idx)
    spot = pd.Series(p * noise, index=idx)
    sig = pd.Series(rng.integers(0, 2, n).astype(float), index=idx)
    empty = pd.Series(dtype=float, index=pd.DatetimeIndex([], tz="UTC"))
    out = run_carry(spot, perp, empty, sig, CS, CP)
    se = out["basis"].std() / np.sqrt(len(out))
    assert abs(out["basis"].mean()) < 4 * se
    assert out["net"].mean() < 0
    assert out["net"].sum() == pytest.approx(out["basis"].sum() - out["cost"].sum()
                                             - out["rebalance"].sum())
