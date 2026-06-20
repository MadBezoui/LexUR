import numpy as np

from lur import gates, problems
from run_protocol import _bench_block


def test_nadir_gate_reuses_problem_identity_across_error_levels(monkeypatch):
    calls = []
    original = problems.make_candidate_set

    def record(*args, **kwargs):
        value = original(*args, **kwargs)
        calls.append(value.copy())
        return value

    monkeypatch.setattr(problems, "make_candidate_set", record)

    result = gates.gate_nadir_error(
        [0.0, 0.1, 0.2], reps=4, n=20, m=3, n_test=10
    )

    assert len(calls) == 4
    assert len(result["records"]) == 12


def _benchmark_config(methods):
    return {
        "geometries": ["linear"],
        "_geoms": None,
        "replications": 2,
        "utilities_per_family": 10,
        "dirichlet_alphas": [1.0],
        "families": ["linear"],
        "methods": methods,
        "tail_q": 0.9,
        "seed": 17,
        "family_scopes": {"linear": "in_class"},
    }


def test_randomized_method_results_do_not_depend_on_method_order():
    methods = ["RW", "SMAA", "MMR", "ChebMMR"]
    manifest = {"run_id": "run-a", "config_sha256": "cfg-a"}

    forward = _bench_block(_benchmark_config(methods), [30], [3], manifest)
    reverse = _bench_block(
        _benchmark_config(list(reversed(methods))), [30], [3], manifest
    )

    key = lambda row: (row["replication"], row["method"])
    forward = {key(row): row for row in forward}
    reverse = {key(row): row for row in reverse}
    assert forward.keys() == reverse.keys()
    for cell in forward:
        assert forward[cell]["selected_index"] == reverse[cell]["selected_index"]
        assert np.isclose(forward[cell]["mean_loss"], reverse[cell]["mean_loss"])
        assert np.isclose(forward[cell]["tail_loss"], reverse[cell]["tail_loss"])
