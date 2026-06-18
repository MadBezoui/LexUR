from __future__ import annotations

import hashlib
import importlib.metadata
import platform
import subprocess
from pathlib import Path


PACKAGES = ("numpy", "scipy", "pandas", "scikit-learn", "matplotlib", "PyYAML", "PuLP", "statsmodels")


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git_commit(cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=cwd, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
    )
    return result.stdout.strip() or None


def build_manifest(config_path: str, seed: int) -> dict:
    root = Path(config_path).resolve().parents[2]
    versions = {}
    for package in PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {
        "seed": int(seed),
        "config_path": str(Path(config_path).resolve()),
        "config_sha256": sha256_file(config_path),
        "git_commit": _git_commit(root),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": versions,
    }
