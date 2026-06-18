from lur.claim_gate import summarize_claim

def test_failed_required_gate_prevents_supported_status():
    claim = {"stage": "core", "gates": ["a", "b"]}
    gates = {"a": {"pass": True, "result": "PASS"}, "b": {"pass": False, "result": "CHECK"}}
    assert summarize_claim(claim, gates) == "qualified"

def test_missing_evidence_makes_exploratory():
    claim = {"stage": "extension", "gates": ["c"]}
    gates = {}
    assert summarize_claim(claim, gates) == "exploratory"

def test_failing_falsification_makes_unsupported():
    claim = {"stage": "core", "gates": ["a", "falsification"]}
    gates = {"a": {"pass": True, "result": "PASS"}, "falsification": {"pass": False, "result": "FAIL"}}
    assert summarize_claim(claim, gates) == "unsupported"

def test_all_pass_makes_supported():
    claim = {"stage": "core", "gates": ["a", "b"]}
    gates = {"a": {"pass": True, "result": "PASS"}, "b": {"pass": True, "result": "PASS"}}
    assert summarize_claim(claim, gates) == "supported"
