import numpy as np

from lexur import methods, problems


def test_seeded_candidate_selection_is_deterministic():
    f1 = problems.make_candidate_set("concave", 40, 4, np.random.default_rng(19))
    f2 = problems.make_candidate_set("concave", 40, 4, np.random.default_rng(19))
    assert np.array_equal(f1, f2)
    assert methods.lexur(f1) == methods.lexur(f2)
