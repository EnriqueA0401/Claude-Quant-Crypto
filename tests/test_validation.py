import numpy as np
import pandas as pd
import pytest

from src.validation import holdout_split, walk_forward


def test_holdout_is_last_12_months():
    idx = pd.date_range("2020-01-01", "2024-12-31", freq="1D", tz="UTC")
    dev, hold = holdout_split(idx, 12)
    assert idx[hold].min() > pd.Timestamp("2023-12-31", tz="UTC")
    assert idx[dev].max() <= pd.Timestamp("2023-12-31", tz="UTC")
    assert dev.sum() + hold.sum() == len(idx) and not (dev & hold).any()


@pytest.mark.parametrize("expanding", [True, False])
def test_walk_forward_purge_embargo(expanding):
    n, h, e = 1000, 5, 3
    folds = walk_forward(n, n_folds=5, min_train=300, horizon=h, embargo=e,
                         expanding=expanding)
    tests = np.concatenate([t for _, t in folds])
    assert np.array_equal(tests, np.arange(300, n))      # cubren todo sin solapar
    for tr, te in folds:
        assert tr.max() < te.min() - h - e + 1           # hueco >= horizon + embargo
        assert te.min() - tr.max() - 1 == h + e
        if not expanding:
            assert len(tr) == 300 - h - e


def test_walk_forward_rejects_too_short():
    with pytest.raises(ValueError):
        walk_forward(10, n_folds=5, min_train=8)
