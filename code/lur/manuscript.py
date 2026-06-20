from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .claim_gate import summarize_claim


@dataclass(frozen=True)
class PublicationEvidence:
    run_id: str
    instances: int
    methods: int
    geometries: int
    families: int
    nemenyi_cd: float
    average_ranks: dict[str, float]
    noninferiority: dict
    gates: list[dict]
    claims: dict[str, str]


@dataclass
class ManuscriptCheck:
    errors: list[str] = field(default_factory=list)


def _table_dir(results_dir: Path) -> Path:
    return results_dir / "tables" if (results_dir / "tables").is_dir() else results_dir


def load_publication_evidence(
    results_dir: str | Path,
    config_path: str | Path,
    claims_path: str | Path,
) -> PublicationEvidence:
    results_dir = Path(results_dir)
    tables = _table_dir(results_dir)
    analysis = json.loads((tables / "benchmark_analysis.json").read_text())
    gates = json.loads((tables / "gates_report.json").read_text())
    cfg = yaml.safe_load(Path(config_path).read_text())
    claims_cfg = yaml.safe_load(Path(claims_path).read_text())["claims"]

    run_id = analysis["run_id"]
    if any(row.get("run_id") != run_id for row in gates):
        raise ValueError("gate report run_id does not match benchmark analysis")
    expected_instances = (
        len(cfg["candidate_sizes"])
        * len(cfg["criteria"])
        * len(cfg["geometries"])
        * int(cfg["replications"])
    )
    if analysis["n_instances"] != expected_instances:
        raise ValueError("benchmark instance count does not match frozen config")
    if analysis["n_methods"] != len(cfg["methods"]):
        raise ValueError("benchmark method count does not match frozen config")

    gate_map = {
        row["gate"]: {
            "pass": row["result"] == "PASS",
            "result": row["result"],
        }
        for row in gates
    }
    claims = {
        claim_id: summarize_claim(claim, gate_map)
        for claim_id, claim in claims_cfg.items()
    }
    return PublicationEvidence(
        run_id=run_id,
        instances=expected_instances,
        methods=len(cfg["methods"]),
        geometries=len(cfg["geometries"]),
        families=len(cfg["families"]),
        nemenyi_cd=float(analysis["nemenyi_cd"]),
        average_ranks=analysis["average_ranks"],
        noninferiority=analysis.get("noninferiority", {}),
        gates=gates,
        claims=claims,
    )


def check_manuscript(
    paths: list[str | Path], evidence: PublicationEvidence
) -> ManuscriptCheck:
    result = ManuscriptCheck()
    stale_patterns = []
    if evidence.instances != 2400:
        stale_patterns.append((re.compile(r"(?<!\d)2,?400(?!\d)"), "2,400"))
    if evidence.methods != 12:
        stale_patterns.append((re.compile(r"\b12\s+methods\b", re.I), "12 methods"))
    if evidence.geometries != 6:
        stale_patterns.append((re.compile(r"\b6\s+geometr(?:y|ies)\b", re.I), "6 geometries"))

    for path_value in paths:
        path = Path(path_value)
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern, label in stale_patterns:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                result.errors.append(
                    f"{path}:{line}: stale protocol value {label}; "
                    f"current run {evidence.run_id[:12]} has "
                    f"{evidence.instances} instances, {evidence.methods} methods, "
                    f"and {evidence.geometries} geometries"
                )
    return result


def _latex_escape(value) -> str:
    text = str(value)
    for old, new in (("\\", r"\textbackslash{}"), ("_", r"\_"),
                     ("%", r"\%"), ("&", r"\&"), ("#", r"\#")):
        text = text.replace(old, new)
    return text


def write_generated_inputs(
    evidence: PublicationEvidence, generated_dir: str | Path
) -> None:
    generated_dir = Path(generated_dir)
    generated_dir.mkdir(parents=True, exist_ok=True)
    numbers = (
        "% Generated from validated ALUR evidence. Do not edit.\n"
        f"\\newcommand{{\\protocolInstances}}{{{evidence.instances:,}}}\n"
        f"\\newcommand{{\\protocolMethods}}{{{evidence.methods}}}\n"
        f"\\newcommand{{\\protocolGeometries}}{{{evidence.geometries}}}\n"
        f"\\newcommand{{\\protocolFamilies}}{{{evidence.families}}}\n"
        f"\\newcommand{{\\protocolCD}}{{{evidence.nemenyi_cd:.3f}}}\n"
        f"\\newcommand{{\\protocolRunId}}{{{evidence.run_id[:12]}}}\n"
    )
    (generated_dir / "protocol_numbers.tex").write_text(numbers, encoding="utf-8")

    gate_lines = [
        r"\begin{tabular}{lll}",
        r"\toprule",
        r"Gate & Status & Evidence \\",
        r"\midrule",
    ]
    gate_lines.extend(
        f"{_latex_escape(row['gate'])} & {_latex_escape(row['result'])} & "
        f"{_latex_escape(row.get('detail', ''))} \\\\"
        for row in evidence.gates
    )
    gate_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (generated_dir / "protocol_gates.tex").write_text(
        "\n".join(gate_lines), encoding="utf-8"
    )

    result_lines = ["% Generated from validated ALUR evidence. Do not edit."]
    if "LUR" in evidence.average_ranks:
        result_lines.append(
            f"\\newcommand{{\\protocolLURRank}}{{{evidence.average_ranks['LUR']:.3f}}}"
        )
    (generated_dir / "protocol_results.tex").write_text(
        "\n".join(result_lines) + "\n", encoding="utf-8"
    )
