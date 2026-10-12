"""Protocolo de revisión, pasos 1–3: PnL a mano, anti-lookahead y test nulo."""
import numpy as np
import pandas as pd
import pytest

from src import backtest
from src.checks import assert_no_lookahead
from src.costs import Costs
from src.signals import ts_momentum

IDX = pd.date_range("2024-01-01", periods=5, freq="1h", tz="UTC")
OPEN = pd.Series([100.0, 110.0, 99.0, 99.0, 120.0], index=IDX)
C = Costs(fee=0.001, slippage=0.0)


# ---------- 1. PnL calculado a mano ----------

def test_long_spot_hand_pnl():
    sig = pd.Series([1, 1, 0, 0, 0], index=IDX, dtype=float)
    out = backtest.run(OPEN, sig, C, spot=True)
    # pos=[0,1,1,0]; ret=[.1,-.1,0,.2121]; turnover=[0,1,0,1]
    assert out["net"].tolist() == pytest.approx([0.0, -0.101, 0.0, -0.001], abs=1e-15)
    assert out["net"].sum() == pytest.approx(-0.102, abs=1e-15)


def test_short_perp_hand_pnl():
    sig = pd.Series([-1, -1, 0, 0, 0], index=IDX, dtype=float)
    out = backtest.run(OPEN, sig, C, spot=False)
    assert out["net"].tolist() == pytest.approx([0.0, 0.099, 0.0, -0.001], abs=1e-15)


def test_spot_cannot_short():
    sig = pd.Series([-1, -1, -1, 0, 0], index=IDX, dtype=float)
    out = backtest.run(OPEN, sig, C, spot=True)
    assert (out["pos"] == 0).all() and out["net"].sum() == 0


def test_funding_assigned_to_holding_bar():
    sig = pd.Series([1, 1, 0, 0, 0], index=IDX, dtype=float)
    fund = pd.Series([0.5, 0.0001, 0.7],
                     index=[IDX[1],                         # en open[1] -> bar 0 (pos 0)
                            IDX[1] + pd.Timedelta("30min"),  # dentro de bar 1 (pos 1)
                            IDX[3] + pd.Timedelta("1min")])  # bar 3 (pos 0)
    out = backtest.run(OPEN, sig, C, spot=False, funding=fund)
    assert out["net"].tolist() == pytest.approx([0.0, -0.1011, 0.0, -0.001], abs=1e-15)
    sig_s = -sig
    out_s = backtest.run(OPEN, sig_s, C, spot=False, funding=fund)
    assert out_s["net"].iloc[1] == pytest.approx(0.1 - 0.001 + 0.0001, abs=1e-15)


def test_signal_executes_next_open():
    sig = pd.Series([0, 0, 1, 0, 0], index=IDX, dtype=float)
    out = backtest.run(OPEN, sig, C, spot=True)
    assert out["pos"].tolist() == [0, 0, 0, 1]


# ---------- 2. Anti-lookahead ----------

def _random_bars(n=500, seed=1):
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    idx = pd.date_range("2023-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame({"open": np.r_[100, close[:-1]], "close": close}, index=idx)


def test_ts_momentum_no_lookahead():
    df = _random_bars()
    assert_no_lookahead(lambda d: ts_momentum(d, 24), df, cut_points=[30, 100, 250, 498])


def test_positions_no_lookahead():
    df = _random_bars()

    def pos_fn(d):
        return backtest.run(d["open"], ts_momentum(d, 24), C, spot=False)["pos"]

    # pos[t] depende de la señal en t-1: alterar datos tras t no cambia pos hasta t
    assert_no_lookahead(pos_fn, df, cut_points=[30, 100, 250, 497])


# ---------- 3. Test nulo ----------

@pytest.mark.parametrize("seed", [0, 1, 2])
def test_random_signals_lose_costs(seed):
    rng = np.random.default_rng(seed)
    n = 50_000
    df = _random_bars(n, seed=seed + 10)
    sig = pd.Series(rng.choice([-1.0, 0.0, 1.0], size=n), index=df.index)
    costs = Costs(fee=0.0005, slippage=0.0005)
    out = backtest.run(df["open"], sig, costs, spot=False)
    se = out["gross"].std() / np.sqrt(len(out))
    assert abs(out["gross"].mean()) < 4 * se          # sin ventaja bruta
    assert out["net"].mean() == pytest.approx(out["gross"].mean() - out["cost"].mean())
    assert out["net"].mean() < 0                       # pierde aprox. los costes
    assert out["cost"].mean() == pytest.approx(costs.per_side * out["turnover"].mean())
