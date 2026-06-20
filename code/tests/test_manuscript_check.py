from pathlib import Path

from lur.manuscript import PublicationEvidence, check_manuscript


def _evidence():
    return PublicationEvidence(
        run_id="run-a",
        instances=7200,
        methods=11,
        geometries=8,
        families=10,
        nemenyi_cd=0.31,
        average_ranks={"LUR": 4.67},
        noninferiority={},
        gates=[],
        claims={},
    )


def test_checker_rejects_stale_instance_count(tmp_path: Path):
    tex = tmp_path / "main.tex"
    tex.write_text("The protocol contains 2,400 paired instances.\n")

    result = check_manuscript([tex], _evidence())

    assert any("2,400" in error for error in result.errors)


def test_checker_accepts_generated_instance_macro(tmp_path: Path):
    tex = tmp_path / "main.tex"
    tex.write_text("The protocol contains \\protocolInstances{} paired instances.\n")

    result = check_manuscript([tex], _evidence())

    assert result.errors == []


def test_checker_rejects_stale_method_and_geometry_counts(tmp_path: Path):
    tex = tmp_path / "main.tex"
    tex.write_text("The audit uses 12 methods and 6 geometries.\n")

    result = check_manuscript([tex], _evidence())

    assert len(result.errors) == 2
