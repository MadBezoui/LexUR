import numpy as np

from lur import methods, problems


def test_seeded_candidate_selection_is_deterministic():
    f1 = problems.make_candidate_set("concave", 40, 4, np.random.default_rng(19))
    f2 = problems.make_candidate_set("concave", 40, 4, np.random.default_rng(19))
    assert np.array_equal(f1, f2)
    assert methods.lur(f1) == methods.lur(f2)
