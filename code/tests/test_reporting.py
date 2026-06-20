import pandas as pd
import pytest

from lur.reporting import analyze_benchmark, build_gate_report


def _gate(rows, name):
    return next(row for row in rows if row["gate"] == name)


def test_gate_report_uses_current_benchmark_analysis_not_stale_legacy_stats():
    current = {
        "run_id": "new",
        "noninferiority": {
            "ASF": {
                "noninferior": True,
                "mean_diff": 0.001,
                "ci": [-0.001, 0.003],
            },
            "MMR": {
                "noninferior": True,
                "mean_diff": 0.002,
                "ci": [0.0, 0.004],
            },
        },
        "wilcoxon_vs_LUR": {},
    }
    stale = {
        "run_id": "old",
        "noninferiority": {
            "ASF": {"noninferior": False},
            "MMR": {"noninferior": False},
        },
    }

    rows = build_gate_report(
        {"benchmark_analysis": current, "benchmark_stats": stale},
        cfg={},
        run_id="new",
    )

    assert _gate(rows, "tail_noninferiority_asf")["result"] == "PASS"
    assert _gate(rows, "tail_noninferiority_mmr")["result"] == "PASS"


def test_gate_report_rejects_analysis_from_another_run():
    with pytest.raises(ValueError, match="run_id"):
        build_gate_report(
            {"benchmark_analysis": {"run_id": "old"}},
            cfg={},
            run_id="new",
        )


def test_gate_report_marks_missing_benchmark_evidence():
    rows = build_gate_report({}, cfg={}, run_id="new")
    assert _gate(rows, "tail_noninferiority_asf")["result"] == "MISSING"
    assert _gate(rows, "tail_noninferiority_mmr")["result"] == "MISSING"


def test_analyze_benchmark_records_design_and_noninferiority():
    methods = ["ASF", "MMR", "LUR"]
    rows = []
    for replication in range(4):
        for method, loss in zip(methods, [0.20, 0.21, 0.205]):
            rows.append({
                "run_id": "run-a",
                "N": 10,
                "m": 3,
                "geometry": "linear",
                "replication": replication,
                "method": method,
                "mean_loss": loss - 0.05,
                "tail_loss": loss,
            })
    cfg = {
        "methods": methods,
        "seed": 7,
        "noninferiority": {
            "metric": "tail_loss",
            "margin_absolute": 0.01,
            "confidence": 0.95,
            "controls": ["ASF", "MMR"],
            "bootstrap_unit": ["N", "m", "geometry", "replication"],
            "bootstrap_repetitions": 100,
        },
    }

    result = analyze_benchmark(pd.DataFrame(rows), cfg)

    assert result["run_id"] == "run-a"
    assert result["n_instances"] == 4
    assert result["n_methods"] == 3
    assert set(result["noninferiority"]) == {"ASF", "MMR"}
