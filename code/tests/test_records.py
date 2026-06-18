from lur.records import expected_benchmark_cells, validate_benchmark_frame


def test_expected_full_protocol_count():
    cfg = {
        "candidate_sizes": [100, 300, 1000],
        "criteria": [3, 5, 8, 10, 15, 20],
        "geometries": ["a", "b", "c", "d", "e", "f", "g", "h"],
        "replications": 50,
    }
    assert expected_benchmark_cells(cfg) == 7200
