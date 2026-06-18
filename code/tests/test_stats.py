import numpy as np
from lur.stats import holm_adjust


def test_holm_adjust_is_monotone_in_sorted_order():
    raw = np.array([0.01, 0.04, 0.03])
    adjusted = holm_adjust(raw)
    assert np.allclose(adjusted, [0.03, 0.06, 0.06])


def test_holm_adjust_caps_at_one():
    assert np.all(holm_adjust(np.array([0.6, 0.8])) <= 1.0)
