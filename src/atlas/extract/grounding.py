"""Quote grounding: every *confirmed* tag must quote its report verbatim.

Matching normalizes case, Unicode quotes/dashes, punctuation and whitespace on both sides, then requires the
normalized quote to be a substring of the normalized report text. A failed quote blocks loading.

``repair`` offers transparent, logged fixes:
0. **reattribute** — the quote is verbatim in a *different* report of the same incident: cite that report;
1. **snap** — if a near-verbatim match exists (rapidfuzz partial ratio ≥ 92 over the normalized text), the quote is
   replaced by the exact span from the report (e.g. the model fixed a typo or dropped a word);
2. **downgrade** — otherwise the tag is kept but downgraded to ``inferred`` and its quote removed.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from rapidfuzz import fuzz

from atlas.extract.schema import MAX_QUOTE_WORDS, IncidentRecord

_TRANSLATE = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "})
SNAP_THRESHOLD = 92.0


def normalize_with_map(text: str) -> tuple[str, list[int]]:
    """Lowercase alphanumeric-only projection of ``text`` with single spaces, plus index map to the original."""
    out: list[str] = []
    idx: list[int] = []
    prev_space = True
    for i, ch in enumerate(text):
        ch = unicodedata.normalize("NFKC", ch.translate(_TRANSLATE)).lower()
        if not ch:
            continue
        c = ch[0]
        if c.isalnum():
            out.append(c)
            idx.append(i)
            prev_space = False
        elif not prev_space:
            out.append(" ")
            idx.append(i)
            prev_space = True
    while out and out[-1] == " ":
        out.pop()
        idx.pop()
    return "".join(out), idx


def normalize(text: str) -> str:
    return normalize_with_map(text)[0]


def is_grounded(quote: str, report_text: str) -> bool:
    q = normalize(quote)
    return bool(q) and q in normalize(report_text)


def snap(quote: str, report_text: str) -> str | None:
    """Return the exact report span closest to ``quote`` if it is a near-verbatim match, else None."""
    q = normalize(quote)
    t, idx = normalize_with_map(report_text)
    if not q or not t:
        return None
    al = fuzz.partial_ratio_alignment(q, t, score_cutoff=SNAP_THRESHOLD)
    if al is None or al.dest_end <= al.dest_start:
        return None
    start, end = idx[al.dest_start], idx[al.dest_end - 1] + 1
    span = " ".join(report_text[start:end].split())
    if not span or len(span.split()) > MAX_QUOTE_WORDS + 3:
        return None
    return span if is_grounded(span, report_text) else None


@dataclass
class QuoteIssue:
    incident_id: int
    dimension: str
    tag: str
    report: int | None
    quote: str
    problem: str  # "report_not_linked" | "not_found" | "private_name"


def check_record(rec: IncidentRecord, report_texts: dict[int, str], private_names: list[str]) -> list[QuoteIssue]:
    """Return every grounding problem in ``rec``. ``report_texts`` holds texts of reports linked to the incident."""
    issues: list[QuoteIssue] = []
    for dim, tag in rec.all_tags():
        if tag.quote is None:
            continue
        if tag.report not in report_texts:
            issues.append(QuoteIssue(rec.incident_id, dim, tag.id, tag.report, tag.quote, "report_not_linked"))
            continue
        if not is_grounded(tag.quote, report_texts[tag.report]):
            issues.append(QuoteIssue(rec.incident_id, dim, tag.id, tag.report, tag.quote, "not_found"))
        if contains_private_name(tag.quote, private_names):
            issues.append(QuoteIssue(rec.incident_id, dim, tag.id, tag.report, tag.quote, "private_name"))
    return issues


def contains_private_name(text: str, private_names: list[str]) -> bool:
    nt = f" {normalize(text)} "
    for name in private_names:
        for part in _name_variants(name):
            if f" {part} " in nt:
                return True
    return False


_PARTICLES = {"de", "da", "del", "van", "von", "der", "bin", "al", "la", "le", "di", "du"}


def looks_like_personal_name(name: str) -> bool:
    """'Jane Q. Example' → True; 'Employee of Department of Housing' → False."""
    toks = name.replace(",", " ").split()
    if not 2 <= len(toks) <= 4:
        return False
    return all(t[:1].isupper() or t.lower() in _PARTICLES for t in toks) and not any(c.isdigit() for c in name)


def _name_variants(name: str) -> list[str]:
    n = normalize(name)
    out = [n] if n else []
    # The surname alone, when the entity is shaped like a personal name and the surname is distinctive (≥ 4 chars).
    toks = n.split()
    if looks_like_personal_name(name) and len(toks[-1]) >= 4:
        out.append(toks[-1])
    return out


def redact_private_names(text: str, private_names: list[str], replacement: str = "[name withheld]") -> str:
    """Replace full names (and distinctive surnames) of private individuals in free text."""
    for name in sorted(private_names, key=len, reverse=True):
        full = name.strip()
        if len(full) < 4:
            continue
        text = re.sub(re.escape(full), replacement, text, flags=re.IGNORECASE)
        toks = full.split()
        if looks_like_personal_name(full) and len(toks[-1]) >= 4:
            text = re.sub(rf"\b{re.escape(toks[-1])}\b", replacement, text)
    return text


def repair(rec: IncidentRecord, report_texts: dict[int, str], private_names: list[str]) -> tuple[IncidentRecord, list[dict]]:
    """Apply snap/downgrade fixes. Returns the repaired record and a log of actions."""
    log: list[dict] = []
    for dim, tag in rec.all_tags():
        if tag.quote is None:
            continue
        action = None
        text = report_texts.get(tag.report) if tag.report is not None else None
        if text is None or not is_grounded(tag.quote, text):
            # 1) verbatim in another report of the same incident → fix the attribution
            other = next((rn for rn, t in report_texts.items() if rn != tag.report and is_grounded(tag.quote, t)), None)
            if other is not None:
                action = {"action": "reattribute", "old_report": tag.report, "new_report": other}
                tag.report, text = other, report_texts[other]
            # 2) near-verbatim in the cited report → snap to the exact span
            elif text is not None:
                snapped = snap(tag.quote, text)
                if snapped:
                    action = {"action": "snap", "old": tag.quote, "new": snapped}
                    tag.quote = snapped
        if text is None or not is_grounded(tag.quote, text) or contains_private_name(tag.quote, private_names):
            why = "report_not_linked" if text is None else (
                "private_name" if is_grounded(tag.quote, text) else "not_found")
            action = {"action": "downgrade", "reason": why,
                      "old": None if why == "private_name" else tag.quote}
            tag.evidence = "inferred"
            tag.quote = None
            tag.report = None
        if action:
            log.append({"incident_id": rec.incident_id, "dimension": dim, "tag": tag.id, **action})
    return rec, log
