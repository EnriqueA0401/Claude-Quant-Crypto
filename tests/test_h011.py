"""Protocolo pasos 1–3 para experiments/h011_alt_carry.py."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import h011_alt_carry as h11  # noqa: E402

IDX = pd.date_range("2021-01-04", periods=200, freq="1D", tz="UTC")   # lunes
COLS = [f"S{i}" for i in range(8)]


def _flat(price=100.0):
    return pd.DataFrame(price, index=IDX, columns=COLS)


def _ev(rates):
    ts = pd.date_range(pd.Timestamp("2021-01-01", tz="UTC"), IDX[-1], freq="8h")
    return {c: pd.Series(r, index=ts) for c, r in zip(COLS, rates)}


def test_hand_pnl_flat_prices():
    rates = [0.001 * (i + 1) for i in range(8)]          # S7 el mayor
    p = _flat()
    df = h11.run(p, p, p, _flat(1e6), p, p, _ev(rates), 7, None)
    act = df[df["n"] > 0]                                # tras 90 días de historia
    first, wk = act.iloc[0], act.iloc[1]                 # entrada; semana sin cambios
    top5 = sum(rates[3:])                                # S3..S7
    assert wk["n"] == 5 and wk["changes"] == 0 and wk["basis"] == 0
    assert wk["funding"] == pytest.approx(h11.W * 21 * top5)   # 21 eventos por semana
    assert first["cost"] == pytest.approx(5 * h11.W * (h11.SPOT_SIDE + h11.PERP_SIDE))
    assert df.index.get_loc(act.index[0]) >= 12           # < 90 días: sin operar


def test_theta_filter_and_hedge():
    rates = [0.0001] * 7 + [0.001]
    p = _flat()
    df = h11.run(p, p, p, _flat(1e6), p, p, _ev(rates), 7, 3e-4)
    assert set(df["n"].unique()) == {0, 1}               # solo S7 supera θ
    # cobertura: si spot y perp suben igual, basis = 0
    up = pd.DataFrame(np.linspace(100, 150, len(IDX))[:, None].repeat(8, 1), index=IDX,
                      columns=COLS)
    df2 = h11.run(up, up, up, _flat(1e6), up, up, _ev(rates), 7, 3e-4)
    assert df2["basis"].abs().max() < 1e-12


def test_no_lookahead_funding_after_monday():
    rng = np.random.default_rng(0)
    ts = pd.date_range(pd.Timestamp("2021-01-01", tz="UTC"), IDX[-1], freq="8h")
    ev = {c: pd.Series(rng.normal(1e-4, 1e-4, len(ts)), index=ts) for c in COLS}
    p = _flat()
    base = h11.run(p, p, p, _flat(1e6), p, p, ev, 3, None)
    cut = base.index[10]
    alt = {c: s.where(s.index < cut, rng.normal(0.01, 0.01, len(s))) for c, s in ev.items()}
    got = h11.run(p, p, p, _flat(1e6), p, p, alt, 3, None)
    pd.testing.assert_series_equal(base["changes"].loc[:cut], got["changes"].loc[:cut])


def test_null_zero_funding_loses_costs():
    rng = np.random.default_rng(1)
    lr = rng.normal(0, 0.03, (len(IDX), 8))
    px = pd.DataFrame(100 * np.exp(np.cumsum(lr, 0)), index=IDX, columns=COLS)
    ts = pd.date_range(pd.Timestamp("2021-01-01", tz="UTC"), IDX[-1], freq="8h")
    ev = {c: pd.Series(rng.normal(0, 1e-4, len(ts)), index=ts) for c in COLS}
    for c in COLS:   # funding de media 0 → solo costes
        ev[c] -= ev[c].mean()
    df = h11.run(px, px, px * 1.01, _flat(1e6), px, px, ev, 3, None)
    assert df["basis"].abs().max() < 1e-12
    assert df["net"].sum() < 0


def test_score_is_8h_equivalent_for_4h_funding():
    # S0 liquida cada 4 h a 0,0006 (= 0,0012 por 8 h): debe quedar por encima de S1..S7
    ts8 = pd.date_range(pd.Timestamp("2021-01-01", tz="UTC"), IDX[-1], freq="8h")
    ts4 = pd.date_range(pd.Timestamp("2021-01-01", tz="UTC"), IDX[-1], freq="4h")
    ev = {c: pd.Series(0.001, index=ts8) for c in COLS}
    ev["S0"] = pd.Series(0.0006, index=ts4)
    p = _flat()
    df = h11.run(p, p, p, _flat(1e6), p, p, ev, 7, 1.1e-3)
    assert set(df["n"].unique()) == {0, 1}               # solo S0 supera θ = 0,0011
