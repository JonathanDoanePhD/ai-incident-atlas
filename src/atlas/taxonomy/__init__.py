"""Load and query the versioned taxonomy in config/taxonomy.yaml."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml

from atlas import paths

TAG_DIMENSIONS = ("sector", "technology", "failure_mode", "harm_type", "lifecycle_stage", "affected_population")


@lru_cache(maxsize=1)
def load() -> dict[str, Any]:
    with open(paths.CONFIG / "taxonomy.yaml") as f:
        return yaml.safe_load(f)


def term_ids(dimension: str) -> list[str]:
    return [t["id"] for t in load()["dimensions"][dimension]["terms"]]


def labels(dimension: str) -> dict[str, str]:
    return {t["id"]: t["label"] for t in load()["dimensions"][dimension]["terms"]}


def sector_parent(term: str) -> str:
    for t in load()["dimensions"]["sector"]["terms"]:
        if t["id"] == term:
            return t.get("parent", term)
    return term


def crosswalk(name: str) -> dict[str, Any]:
    return load()["crosswalk"][name]
