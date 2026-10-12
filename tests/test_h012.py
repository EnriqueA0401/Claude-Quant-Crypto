"""Protocolo pasos 1–3 para experiments/h012_quarterly_basis.py."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import h012_quarterly_basis as h12  # noqa: E402

IDX = pd.date_range("2021-01-01", periods=24 * 60, freq="1h", tz="UTC")


def _spot(px=100.0):
    return pd.DataFrame({"open": px, "close": px}, index=IDX)


def _fut(start, end_px, last_i, first_px):
    i = IDX[:last_i + 1]
    p = np.linspace(first_px, end_px, len(i))
    return pd.DataFrame({"open": p, "high": p, "close": np.r_[p[1:], end_px]}, index=i)


def test_hand_pnl_convergence_to_expiry():
    # futuro de 102 a 100 en 30 días; spot plano en 100 → basis ann ≈ 24 %
    fut = _fut(0, 100.0, 24 * 30, 102.0)
    out = h12.run(_spot(), {"X_1": fut}, 0.05, "expiry")
    t_in = int(np.flatnonzero(out["entry"])[0])
    assert t_in == 1                                     # decide al close de 0, entra en 1
    f_in = fut["open"].iloc[1]
    expected = h12.W * (1 - 100.0 / f_in) - 2 * h12.W * (h12.CS + h12.CF)
    assert out["net"].sum() == pytest.approx(expected, rel=1e-9)
    assert out["entry"].sum() == 1                       # tras vencer no hay contrato
    assert out.loc[out.index > fut.index[-1], "pos"].sum() == 0


def test_no_entry_below_theta_or_too_close_to_expiry():
    fut = _fut(0, 100.0, 24 * 30, 100.1)               # basis ≈ 1,2 % anual
    assert h12.run(_spot(), {"X_1": fut}, 0.05, "expiry")["entry"].sum() == 0
    fut2 = _fut(0, 100.0, 24 * 10, 103.0)              # < 14 días
    assert h12.run(_spot(), {"X_1": fut2}, 0.05, "expiry")["entry"].sum() == 0


def test_early_exit_when_basis_collapses():
    p = np.r_[np.full(24 * 5, 103.0), np.full(24 * 25 + 1, 100.01)]
    i = IDX[:len(p)]
    fut = pd.DataFrame({"open": p, "high": p, "close": np.r_[p[1:], 100.01]}, index=i)
    out = h12.run(_spot(), {"X_1": fut}, 0.10, "early")
    held = np.flatnonzero(out["pos"] > 0)
    assert held.max() < 24 * 6                           # sale poco después del colapso


def test_no_lookahead():
    rng = np.random.default_rng(0)
    s = _spot()
    s["open"] = s["close"] = 100 * np.exp(np.cumsum(rng.normal(0, 0.003, len(IDX))))
    f = s.iloc[:24 * 50].copy()
    f["open"] = f["open"] * (1 + 0.01 * np.linspace(1, 0, len(f)))
    f["close"] = f["open"].shift(-1).fillna(f["open"].iloc[-1])
    f["high"] = f[["open", "close"]].max(axis=1)
    base = h12.run(s, {"X_1": f}, 0.05, "early")
    cut = 24 * 20
    s2, f2 = s.copy(), f.copy()
    s2.iloc[cut + 1:] *= 1.3
    f2.iloc[cut + 1:] *= 0.8
    alt = h12.run(s2, {"X_1": f2}, 0.05, "early")
    pd.testing.assert_series_equal(base["pos"].iloc[:cut + 1], alt["pos"].iloc[:cut + 1])


def test_null_no_basis_loses_costs():
    rng = np.random.default_rng(1)
    s = _spot()
    s["open"] = s["close"] = 100 * np.exp(np.cumsum(rng.normal(0, 0.003, len(IDX))))
    f = s.iloc[:24 * 50].copy()
    f["high"] = f["open"]
    f["close"] = s["open"].shift(-1).iloc[:len(f)]       # liquida al precio spot
    out = h12.run(s, {"X_1": f}, -1.0, "expiry")       # θ negativo: entra siempre
    assert abs(out["basis"].sum()) < 1e-9 and out["net"].sum() < 0


def test_liquidation_total_loss_is_margin_minus_capped_spot():
    # spot y futuro suben juntos de 100 a 300; el futuro empieza con prima 3 %
    n = 24 * 40
    px = np.r_[np.full(48, 100.0), np.full(n - 48, 300.0)]
    s = pd.DataFrame({"open": px, "close": px}, index=IDX[:n])
    fp = px * 1.03
    fc = np.r_[fp[1:], fp[-1]]
    f = pd.DataFrame({"open": fp, "high": np.maximum(fp, fc), "close": fc}, index=IDX[:n])
    out = h12.run(s, {"X_1": f}, 0.05, "expiry")
    assert out["liquidated"].sum() == 1
    # entrada en t=1 a F=103, S=100; liquidación a 2·103: futuro −W, spot +W (tope +100 %)
    liq_bar = int(np.flatnonzero(out["liquidated"])[0])
    total = out["basis"].iloc[:liq_bar + 1].sum()
    assert total == pytest.approx(h12.W * 1.0 - h12.W * 1.0, abs=1e-12)
