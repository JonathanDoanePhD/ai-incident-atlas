"""Project paths and configuration, without machine-specific hardcoding.

Resolution order for the data directory:
1. the ``TPP_DATA_DIR`` environment variable;
2. ``data_dir`` in ``config/local.yaml`` (git-ignored);
3. ``<project root>/data``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_local() -> dict:
    local = PROJECT_ROOT / "config" / "local.yaml"
    if local.exists():
        return yaml.safe_load(local.read_text()) or {}
    return {}


def _resolve(p: str | Path) -> Path:
    p = Path(p).expanduser()
    return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()


@dataclass(frozen=True)
class Paths:
    data_dir: Path
    outputs_dir: Path

    @property
    def raw(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed(self) -> Path:
        return self.data_dir / "processed"


def get_paths() -> Paths:
    local = _load_local()
    data_dir = os.environ.get("TPP_DATA_DIR") or local.get("data_dir", "data")
    outputs = os.environ.get("TPP_OUTPUTS_DIR") or local.get("outputs_dir", "outputs")
    return Paths(data_dir=_resolve(data_dir), outputs_dir=_resolve(outputs))


def load_yaml(name: str) -> dict:
    """Load ``config/<name>`` (e.g. ``datasets.yaml``)."""
    path = PROJECT_ROOT / "config" / name
    return yaml.safe_load(path.read_text()) or {}
