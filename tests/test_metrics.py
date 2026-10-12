import numpy as np
import pytest

from src import metrics


def test_sharpe_and_drawdown_known():
    r = np.array([0.1, -0.5, 0.2])
    assert metrics.max_drawdown(r) == pytest.approx(-0.5)
    assert metrics.sharpe(np.array([0.01, 0.03])) == pytest.approx(0.02 / np.std([0.01, 0.03], ddof=1))
    assert metrics.sharpe(np.zeros(10)) == 0.0


def test_psr_and_dsr_behave():
    rng = np.random.default_rng(0)
    r = rng.normal(0.001, 0.01, 2000)       # SR por periodo ~0.1
    psr = metrics.probabilistic_sharpe(r)
    assert psr > 0.99
    dsr_few = metrics.deflated_sharpe(r, n_trials=2, sr_var=0.002)
    dsr_many = metrics.deflated_sharpe(r, n_trials=1000, sr_var=0.002)
    assert dsr_many < dsr_few <= psr


def test_expected_max_sharpe_grows_with_trials():
    a = metrics.expected_max_sharpe(0.01, 10)
    b = metrics.expected_max_sharpe(0.01, 1000)
    assert 0 < a < b


def test_block_bootstrap_ci_contains_truth():
    rng = np.random.default_rng(3)
    r = rng.normal(0.0, 0.01, 3000)
    lo, hi = metrics.block_bootstrap_mean_ci(r, block=20, n_boot=2000)
    assert lo < 0 < hi


def test_pbo_noise_vs_edge():
    # con ruido puro el PBO de un solo dataset varía mucho; su media debe ser ~0,5
    pbos = [metrics.pbo_cscv(np.random.default_rng(s).normal(0, 0.01, (1000, 20)), 8)
            for s in range(40)]
    assert 0.4 < np.mean(pbos) < 0.6
    noise = np.random.default_rng(7).normal(0, 0.01, (2000, 30))
    edge = noise.copy()
    edge[:, 0] += 0.003
    assert metrics.pbo_cscv(edge, n_splits=10) < 0.05
