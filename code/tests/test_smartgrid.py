import numpy as np
import pytest

from lur import smartgrid


def test_empty_efficient_set_raises_clear_error(monkeypatch):
    monkeypatch.setattr(
        smartgrid, "_nd_mask", lambda F: np.zeros(F.shape[0], dtype=bool)
    )
    with pytest.raises(RuntimeError, match="no non-dominated candidates"):
        smartgrid.build_candidates(n_candidates=5, n_scenarios=2, seed=3)
