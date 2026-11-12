"""Reading survey extracts and recording provenance.

Survey microdata are never committed. A user downloads an extract (for example a
CSV from NLS Investigator, or an NCES/ICPSR public-use file) into ``data/raw/``;
these functions read it, keep only the variables named in a verified mapping,
rename them to analytic names, and write a provenance manifest (file hash, size,
time, mapping) so every downstream result can be traced to an exact input.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

import pandas as pd

from .config import PROJECT_ROOT, load_yaml

READERS = {".csv": "csv", ".tsv": "tsv", ".parquet": "parquet", ".dta": "stata",
           ".sav": "spss", ".sas7bdat": "sas"}


@dataclass
class DatasetSpec:
    """Registry entry for one study (from ``config/datasets.yaml``)."""

    name: str
    access: str = "unknown"
    id_var: str | None = None
    missing_codes: dict[int, str] = field(default_factory=dict)
    weight_vars: list[str] = field(default_factory=list)
    strata_var: str | None = None
    psu_var: str | None = None
    documentation_url: str | None = None
    notes: str = ""

    @classmethod
    def from_registry(cls, key: str, registry: Mapping | None = None) -> "DatasetSpec":
        """Build from a registry entry. Accepts the flat schema (``weight_vars``, ``strata_var``,
        ``psu_var``) or the nested ``design: {strata, psu, weights}`` schema used in
        ``config/datasets.yaml``. Only integer-keyed missing codes are kept."""
        reg = registry if registry is not None else load_yaml("datasets.yaml").get("datasets", {})
        if key not in reg:
            raise KeyError(f"Dataset {key!r} not in registry; known: {sorted(reg)}")
        e = dict(reg[key])
        codes = {}
        for k, v in (e.get("missing_codes") or {}).items():
            try:
                codes[int(k)] = str(v)
            except (TypeError, ValueError):
                continue  # notes or list-valued width-dependent codes
        design = e.get("design") or {}
        weights = e.get("weight_vars") or design.get("weights") or []
        if isinstance(weights, str):
            weights = [weights]
        elif isinstance(weights, dict):
            weights = [w for w in weights.values() if isinstance(w, str)]
        access = e.get("access", "unknown")
        if isinstance(access, dict):
            access = access.get("level", "unknown")
        return cls(name=key, access=str(access), id_var=e.get("id_var"), missing_codes=codes,
                   weight_vars=list(weights), strata_var=e.get("strata_var") or design.get("strata"),
                   psu_var=e.get("psu_var") or design.get("psu"),
                   documentation_url=e.get("documentation_url"), notes=str(e.get("notes", "")))


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


def read_table(path: str | Path, columns: list[str] | None = None) -> pd.DataFrame:
    """Read a survey file by extension, optionally only some columns."""
    path = Path(path)
    kind = READERS.get(path.suffix.lower())
    if kind is None:
        raise ValueError(f"Unsupported file type {path.suffix!r}; supported: {sorted(READERS)}")
    if kind in ("csv", "tsv"):
        return pd.read_csv(path, usecols=columns, sep="\t" if kind == "tsv" else ",", low_memory=False)
    if kind == "parquet":
        return pd.read_parquet(path, columns=columns)
    try:
        import pyreadstat  # optional dependency
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise ImportError("Reading Stata/SPSS/SAS files needs `pip install pyreadstat`") from exc
    fn = {"stata": pyreadstat.read_dta, "spss": pyreadstat.read_sav, "sas": pyreadstat.read_sas7bdat}[kind]
    df, _meta = fn(str(path), usecols=columns, apply_value_formats=False)
    return df


def warn_if_outside_ignored_dir(path: Path) -> str | None:
    """Return a warning if a raw data file sits somewhere git might track it."""
    try:
        rel = path.resolve().relative_to(PROJECT_ROOT)
    except ValueError:
        return None  # outside the repository entirely: fine
    if rel.parts[:2] not in {("data", "raw"), ("data", "processed")}:
        return (f"{rel} is inside the repository but not under data/raw or data/processed; "
                "it may be committed by accident. Move it under data/raw/.")
    return None


def load_extract(path: str | Path, mapping: Mapping[str, str], *, dataset: str,
                 manifest_dir: str | Path | None = None) -> tuple[pd.DataFrame, dict]:
    """Load ``path`` keeping only mapped variables, renamed source -> analytic name.

    ``mapping`` maps analytic names to *verified* source variable identifiers.
    Returns the frame and a provenance manifest (also written to ``manifest_dir``).
    """
    path = Path(path)
    if not mapping:
        raise ValueError("Empty variable mapping: fill config/mappings/<dataset>.yaml from the codebook first.")
    unverified = [k for k, v in mapping.items() if v is None or str(v).startswith("TODO")]
    if unverified:
        raise ValueError(f"Mapping has unverified entries (value None/TODO): {unverified}")
    sources = list(mapping.values())
    df = read_table(path, columns=sources)
    missing = sorted(set(sources) - set(df.columns))
    if missing:
        raise KeyError(f"Variables not found in {path.name}: {missing}")
    df = df[sources].rename(columns={v: k for k, v in mapping.items()})
    manifest = {
        "dataset": dataset,
        "file": path.name,
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "n_rows": int(len(df)),
        "mapping": dict(mapping),
        "loaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "warning": warn_if_outside_ignored_dir(path),
    }
    if manifest_dir is not None:
        out = Path(manifest_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{dataset}_manifest.json").write_text(json.dumps(manifest, indent=2))
    return df, manifest


def load_mapping(dataset: str) -> dict[str, str]:
    """Read ``config/mappings/<dataset>.yaml`` -> {analytic_name: source_variable}."""
    path = PROJECT_ROOT / "config" / "mappings" / f"{dataset}.yaml"
    raw = load_yaml(f"mappings/{dataset}.yaml") if path.exists() else {}
    return {k: (v["source"] if isinstance(v, dict) else v) for k, v in (raw.get("variables") or {}).items()}
