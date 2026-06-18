import json
from pathlib import Path

from lur.provenance import build_manifest, sha256_file


def test_manifest_contains_reproducibility_fields(tmp_path: Path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("seed: 17\n", encoding="utf-8")
    manifest = build_manifest(str(cfg), seed=17)
    assert manifest["seed"] == 17
    assert manifest["config_sha256"] == sha256_file(cfg)
    assert manifest["python"]
    assert manifest["packages"]["numpy"]
    assert "git_commit" in manifest


def test_manifest_round_trip(tmp_path: Path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("seed: 17\n", encoding="utf-8")
    payload = build_manifest(str(cfg), seed=17)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert json.loads(path.read_text())["config_sha256"] == payload["config_sha256"]
