"""Validate raw LLM batch outputs and load them into SQLite.

Pipeline for each ``data/enrich/raw/<batch>.json``:
1. parse JSON and validate each record with :class:`IncidentRecord` (taxonomy-aware);
2. check that the record's incident belongs to the batch;
3. check quote grounding against the full cached report text (and private-name rules);
4. if there are grounding issues, apply logged ``repair`` (snap → downgrade);
5. re-check: **any remaining issue blocks loading** of that record.

Outputs: ``data/processed/extractions.jsonl`` (one validated record per incident),
``data/enrich/repair_log.jsonl`` and ``reports/extraction_validation.md``. Tables ``extraction`` and
``extraction_tag`` are (re)built in SQLite.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any

from pydantic import ValidationError

from atlas import paths
from atlas.extract.batches import OUT_DIR, PLAN_PATH
from atlas.extract.grounding import check_record, contains_private_name, redact_private_names, repair
from atlas.extract.schema import IncidentRecord
from atlas.ingest.load import connect
from atlas.privacy import private_names_by_incident


def report_texts(con, iid: int) -> dict[int, str]:
    rows = con.execute(
        """SELECT r.report_number, r.text FROM incident_report ir JOIN reports r USING (report_number)
           WHERE ir.incident_id = ? AND r.text IS NOT NULL""", (iid,)).fetchall()
    return {r["report_number"]: r["text"] for r in rows}


def _scrub_free_text(rec: IncidentRecord, names: list[str]) -> list[str]:
    """Redact private names that slipped into free-text fields. Returns the list of fields changed."""
    changed = []
    for field in ("summary", "technical_summary", "notes"):
        v = getattr(rec, field)
        if v and contains_private_name(v, names):
            setattr(rec, field, redact_private_names(v, names))
            changed.append(field)
    for field in ("systems", "developers", "deployers"):
        vals = getattr(rec, field)
        kept = [v for v in vals if not contains_private_name(v, names)]
        if len(kept) != len(vals):
            setattr(rec, field, kept)
            changed.append(field)
    return changed


def validate_all(source: str = "primary") -> dict[str, Any]:
    con = connect()
    plan = json.loads(PLAN_PATH.read_text())
    batch_members = {b["batch"]: set(b["incidents"]) for b in plan["batches"]}
    private = private_names_by_incident(con)
    out_dir = OUT_DIR if source == "primary" else paths.ENRICH / source
    stats: Counter = Counter()
    errors: list[dict] = []
    repairs: list[dict] = []
    records: dict[int, dict] = {}
    for path in sorted(out_dir.glob("*.json")):
        batch = path.stem
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            errors.append({"batch": batch, "error": f"invalid JSON: {e}"})
            stats["batch_invalid_json"] += 1
            continue
        for raw in data:
            stats["records_seen"] += 1
            iid = raw.get("incident_id")
            if batch in batch_members and iid not in batch_members[batch]:
                errors.append({"batch": batch, "incident_id": iid, "error": "incident not in batch"})
                stats["not_in_batch"] += 1
                continue
            try:
                rec = IncidentRecord.model_validate(raw)
            except ValidationError as e:
                errors.append({"batch": batch, "incident_id": iid, "error": str(e).splitlines()[0:3]})
                stats["schema_invalid"] += 1
                continue
            texts = report_texts(con, rec.incident_id)
            names = private.get(rec.incident_id, [])
            issues = check_record(rec, texts, names)
            stats["quotes_total"] += sum(1 for _, t in rec.all_tags() if t.quote)
            if issues:
                stats["records_with_quote_issues"] += 1
                stats["quote_issues"] += len(issues)
                rec, log = repair(rec, texts, names)
                for entry in log:
                    stats[f"repair_{entry['action']}"] += 1
                repairs.extend({"batch": batch, **e} for e in log)
                remaining = check_record(rec, texts, names)
                if remaining:  # blocked
                    stats["blocked"] += 1
                    errors.append({"batch": batch, "incident_id": iid, "error": "unresolved quote issues"})
                    continue
            scrubbed = _scrub_free_text(rec, names)
            if scrubbed:
                stats["free_text_redactions"] += 1
            rec_d = rec.model_dump()
            rec_d["_batch"] = batch
            records[rec.incident_id] = rec_d
            stats["records_loaded"] += 1
    _write(con, records, repairs, errors, stats, source)
    return {"stats": dict(stats), "errors": errors[:20]}


def _write(con, records, repairs, errors, stats, source) -> None:
    suffix = "" if source == "primary" else f"_{source}"
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    with open(paths.PROCESSED / f"extractions{suffix}.jsonl", "w") as f:
        for iid in sorted(records):
            f.write(json.dumps(records[iid], ensure_ascii=False) + "\n")
    with open(paths.ENRICH / f"repair_log{suffix}.jsonl", "w") as f:
        for r in repairs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if source != "primary":
        return
    con.executescript("""
        DROP TABLE IF EXISTS extraction; DROP TABLE IF EXISTS extraction_tag;
        CREATE TABLE extraction (incident_id INTEGER PRIMARY KEY, summary TEXT, technical_summary TEXT,
          systems TEXT, developers TEXT, deployers TEXT, primary_failure_mode TEXT, severity TEXT,
          severity_evidence TEXT, risk_domain TEXT, risk_subdomain TEXT, intent TEXT, cause_entity TEXT,
          notes TEXT, batch TEXT);
        CREATE TABLE extraction_tag (incident_id INTEGER, dimension TEXT, term TEXT, evidence TEXT,
          quote TEXT, report_number INTEGER);""")
    for iid, r in records.items():
        sev = r.get("severity") or {}
        con.execute("INSERT INTO extraction VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (iid, r["summary"], r["technical_summary"], json.dumps(r["systems"]), json.dumps(r["developers"]),
                     json.dumps(r["deployers"]), r["primary_failure_mode"], sev.get("id"), sev.get("evidence"),
                     r.get("risk_domain"), r.get("risk_subdomain"), r["intent"], r["cause_entity"], r.get("notes"),
                     r["_batch"]))
        for dim, tags in r["tags"].items():
            for t in tags:
                con.execute("INSERT INTO extraction_tag VALUES (?,?,?,?,?,?)",
                            (iid, dim, t["id"], t["evidence"], t["quote"], t["report"]))
        if sev:
            con.execute("INSERT INTO extraction_tag VALUES (?,?,?,?,?,?)",
                        (iid, "severity", sev["id"], sev["evidence"], sev["quote"], sev["report"]))
    con.commit()
    ev = Counter(e for (e,) in con.execute("SELECT evidence FROM extraction_tag"))
    lines = ["# Extraction validation", "", "_Generated by `python -m atlas.extract.validate`._", "",
             "| metric | value |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(stats.items())]
    lines += [f"| tags_confirmed | {ev.get('confirmed', 0)} |", f"| tags_inferred | {ev.get('inferred', 0)} |"]
    if stats.get("quotes_total"):
        ok = stats["quotes_total"] - stats.get("quote_issues", 0)
        lines += ["", f"First-pass verbatim grounding rate: **{ok / stats['quotes_total']:.1%}** "
                      f"of {stats['quotes_total']} quotes (before repair)."]
    lines += ["", "## Errors (first 20)", ""] + [f"- `{json.dumps(e)[:300]}`" for e in errors[:20]]
    (paths.REPORTS / "extraction_validation.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    res = validate_all(sys.argv[1] if len(sys.argv) > 1 else "primary")
    print(json.dumps(res, indent=1)[:4000])
