"""Data validation: schema, ranges, identifiers, missingness, and data-safety checks."""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

# Column-name patterns that suggest direct identifiers. Public-use survey files should not
# contain these; if one appears, stop and check the data-use agreement before continuing.
IDENTIFIER_PATTERNS = [r"\bname\b", r"first_?name", r"last_?name", r"address", r"street", r"phone",
                       r"e-?mail", r"\bssn\b", r"social_?security", r"\bdob\b", r"birth_?date",
                       r"zip(_?code)?\b", r"latitude", r"longitude", r"ip_?addr"]


@dataclass
class Issue:
    level: str  # "error" | "warning"
    check: str
    message: str


@dataclass
class ValidationReport:
    issues: list[Issue] = field(default_factory=list)

    def add(self, level: str, check: str, message: str) -> None:
        self.issues.append(Issue(level, check, message))

    @property
    def ok(self) -> bool:
        return not any(i.level == "error" for i in self.issues)

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([i.__dict__ for i in self.issues], columns=["level", "check", "message"])

    def raise_if_errors(self) -> None:
        if not self.ok:
            msgs = "\n".join(f"- [{i.check}] {i.message}" for i in self.issues if i.level == "error")
            raise ValueError(f"Validation failed:\n{msgs}")


def check_required_columns(df: pd.DataFrame, required: list[str], report: ValidationReport) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        report.add("error", "required_columns", f"missing columns: {missing}")


def check_unique_id(df: pd.DataFrame, id_col: str, report: ValidationReport) -> None:
    if id_col not in df.columns:
        report.add("error", "unique_id", f"id column {id_col!r} absent")
        return
    dup = int(df[id_col].duplicated().sum())
    if dup:
        report.add("error", "unique_id", f"{dup} duplicated values of {id_col!r}")


def check_ranges(df: pd.DataFrame, ranges: Mapping[str, tuple[float, float]], report: ValidationReport) -> None:
    """Values (after missing-code recoding) must fall inside documented ranges."""
    for col, (lo, hi) in ranges.items():
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        bad = s.notna() & ((s < lo) | (s > hi))
        if bad.any():
            report.add("error", "range", f"{col}: {int(bad.sum())} values outside [{lo}, {hi}] "
                       f"(e.g. {sorted(s[bad].unique())[:5]}); unrecoded missing codes?")


def check_no_direct_identifiers(df: pd.DataFrame, report: ValidationReport) -> None:
    for col in df.columns:
        for pat in IDENTIFIER_PATTERNS:
            if re.search(pat, str(col), flags=re.I):
                report.add("error", "identifiers", f"column {col!r} looks like a direct identifier ({pat})")
                break


def check_weights(df: pd.DataFrame, weight_col: str, report: ValidationReport) -> None:
    if weight_col not in df.columns:
        report.add("error", "weights", f"weight {weight_col!r} absent")
        return
    w = pd.to_numeric(df[weight_col], errors="coerce")
    if (w < 0).any():
        report.add("error", "weights", f"{weight_col}: negative weights")
    n0 = int((w == 0).sum())
    if n0:
        report.add("warning", "weights", f"{weight_col}: {n0} zero weights (cases out of scope for this weight)")
    if w.isna().any():
        report.add("warning", "weights", f"{weight_col}: {int(w.isna().sum())} missing weights")


def missingness_table(reasons: pd.DataFrame) -> pd.DataFrame:
    """Per-variable counts of each missingness reason (from ``preprocessing.recode_missing``)."""
    rows = []
    for col in reasons.columns:
        vc = reasons[col].value_counts(dropna=True)
        row = {"variable": col, "n": len(reasons), "n_missing": int(vc.sum())}
        row.update({f"n_{k}": int(v) for k, v in vc.items()})
        rows.append(row)
    out = pd.DataFrame(rows).fillna(0)
    out["pct_missing"] = np.round(100 * out["n_missing"] / out["n"], 1)
    return out


def min_cell_suppression(counts: pd.Series, min_n: int = 10) -> pd.Series:
    """Suppress small cells before anything is published (disclosure control)."""
    return counts.where(counts >= min_n)


def git_tracked_data_files(repo_dir: str | Path,
                           suffixes=(".dta", ".sav", ".sas7bdat", ".por", ".NLSY97", ".parquet")) -> list[str]:
    """List tracked files that look like microdata, or under data/raw|processed (other than READMEs)."""
    try:
        out = subprocess.run(["git", "ls-files"], cwd=repo_dir, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    bad = []
    for f in out.splitlines():
        p = Path(f)
        in_data = any(part in ("raw", "processed") for part in p.parts) and "data" in p.parts
        if p.suffix in suffixes or (in_data and p.name != "README.md"):
            bad.append(f)
    return bad


def validate_frame(df: pd.DataFrame, *, required: list[str], id_col: str | None = None,
                   ranges: Mapping[str, tuple[float, float]] | None = None,
                   weight_col: str | None = None) -> ValidationReport:
    report = ValidationReport()
    check_required_columns(df, required, report)
    if id_col:
        check_unique_id(df, id_col, report)
    if ranges:
        check_ranges(df, ranges, report)
    if weight_col:
        check_weights(df, weight_col, report)
    check_no_direct_identifiers(df, report)
    return report
