"""Phase 1 — load the AIID snapshot into a normalized SQLite database.

Design:
* ``raw_*`` tables keep source records verbatim (one JSON blob per document) for provenance.
* Clean tables (``incidents``, ``reports``, ``entities``) hold typed, normalized columns.
* Bridge tables model many-to-many relations: ``incident_report``, ``incident_entity`` (with role)
  and ``expert_label`` (incident ↔ namespace/field/value from expert taxonomies).
* ``provenance`` records which file each table came from, with its checksum and load time.

The loader is idempotent: it rebuilds the database from the snapshot in a single transaction.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sqlite3
import tarfile
import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import bson
import pandas as pd

from atlas import paths

SCHEMA = """
CREATE TABLE provenance (
  table_name TEXT PRIMARY KEY, source_file TEXT, source_sha256 TEXT, snapshot TEXT,
  row_count INTEGER, loaded_at TEXT);
CREATE TABLE raw_document (
  collection TEXT, doc_id TEXT, payload TEXT, PRIMARY KEY (collection, doc_id));
CREATE TABLE incidents (
  incident_id INTEGER PRIMARY KEY, date TEXT, year INTEGER, title TEXT, description TEXT,
  n_reports INTEGER, is_duplicate_of INTEGER, created_at TEXT);
CREATE TABLE reports (
  report_number INTEGER PRIMARY KEY, title TEXT, url TEXT, source_domain TEXT,
  date_published TEXT, language TEXT, authors TEXT, text TEXT, text_chars INTEGER,
  is_incident_report INTEGER);
CREATE TABLE incident_report (
  incident_id INTEGER, report_number INTEGER, PRIMARY KEY (incident_id, report_number));
CREATE TABLE entities (entity_id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE incident_entity (
  incident_id INTEGER, entity_id TEXT, role TEXT, PRIMARY KEY (incident_id, entity_id, role));
CREATE TABLE expert_label (
  incident_id INTEGER, namespace TEXT, field TEXT, value TEXT, published INTEGER);
CREATE INDEX ix_expert_label ON expert_label (namespace, field);
CREATE TABLE incident_link (incident_id INTEGER, same_as TEXT, source_namespace TEXT);
CREATE TABLE entity_relationship (sub TEXT, obj TEXT, pred TEXT, is_symmetric INTEGER);
CREATE TABLE taxonomy_field (
  namespace TEXT, short_name TEXT, long_name TEXT, short_description TEXT, permitted_values TEXT);
"""

ROLE_COLUMNS = {
    "deployer": "Alleged deployer of AI system",
    "developer": "Alleged developer of AI system",
    "harmed": "Alleged harmed or nearly harmed parties",
}

# Fields from expert taxonomies we keep in the long-format expert_label table.
KEEP_FIELDS = {
    "MIT": {"Risk Domain", "Risk Subdomain", "Entity", "Timing", "Intent"},
    "GMF": {"Known AI Goal", "Potential AI Goal", "Known AI Technology", "Potential AI Technology",
            "Known AI Technical Failure", "Potential AI Technical Failure"},
    "CSETv1": {"Sector of Deployment", "Harm Domain", "Tangible Harm", "AI Harm Level",
               "Harm Distribution Basis", "Infrastructure Sectors", "AI Task", "AI tools and methods",
               "Intentional Harm", "Physical System Type", "Autonomy Level", "Special Interest Intangible Harm",
               "Lives Lost", "Injuries", "Public Sector Deployment", "Physical Objects",
               "Protected Characteristic", "Rights Violation", "Detrimental Content", "Involving Minor",
               "Impact on Critical Services"},
}
# Per-annotator CSETv1 namespaces are kept too: they let us measure expert inter-annotator agreement.
for _ns in ("CSETv1_Annotator-1", "CSETv1_Annotator-2", "CSETv1_Annotator-3"):
    KEEP_FIELDS[_ns] = KEEP_FIELDS["CSETv1"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_snapshot() -> None:
    """Download and extract the snapshot if missing; verify its checksum."""
    paths.RAW.mkdir(parents=True, exist_ok=True)
    if not paths.SNAPSHOT_FILE.exists():
        urllib.request.urlretrieve(paths.SNAPSHOT_URL, paths.SNAPSHOT_FILE)
    digest = sha256(paths.SNAPSHOT_FILE)
    if digest != paths.SNAPSHOT_SHA256:
        raise RuntimeError(f"Snapshot checksum mismatch: {digest}")
    if not paths.SNAPSHOT_DIR.exists():
        dest = paths.SNAPSHOT_DIR.parent
        dest.mkdir(parents=True, exist_ok=True)
        with tarfile.open(paths.SNAPSHOT_FILE, "r:bz2") as tf:
            tf.extractall(dest, filter="data")


def read_bson(name: str) -> list[dict[str, Any]]:
    with open(paths.SNAPSHOT_DIR / "aiidprod" / f"{name}.bson", "rb") as f:
        return bson.decode_all(f.read())


def parse_list(value: Any) -> list[Any]:
    """Parse list-valued fields stored as JSON or Python-repr strings ("[1, 2]", "['a']")."""
    if isinstance(value, list):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    s = str(value).strip()
    if not s or s in {"[]", "nan", "None"}:
        return []
    try:
        out = json.loads(s)
    except json.JSONDecodeError:
        out = ast.literal_eval(s)
    return list(out) if isinstance(out, (list, tuple)) else [out]


def clean_text(value: Any) -> str | None:
    """Normalize placeholder values ("nan", "None", "") to None."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    s = str(value).strip()
    return None if s.lower() in {"", "nan", "none", "null", "unknown", "--"} else s


def to_int(value: Any) -> int | None:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None


def domain_of(url: Any) -> str | None:
    """Hostname without a leading 'www.', used when AIID's source_domain is missing."""
    u = clean_text(url)
    if not u:
        return None
    host = urlparse(u).netloc.lower()
    return host[4:] if host.startswith("www.") else (host or None)


def _flatten_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        out: list[str] = []
        for v in value:
            out.extend(_flatten_value(v))
        return out
    if isinstance(value, dict):  # nested objects (e.g. CSET 'Entities') are kept as JSON
        return [json.dumps(value, sort_keys=True)]
    if isinstance(value, bool):
        return ["yes" if value else "no"]
    s = clean_text(value)
    return [s] if s is not None else []


def iter_expert_labels(classifications: Iterable[dict[str, Any]]) -> Iterable[tuple]:
    for doc in classifications:
        ns = doc.get("namespace")
        if ns not in KEEP_FIELDS:
            continue
        published = 1 if str(doc.get("publish")) == "True" else 0
        incidents = [to_int(i) for i in parse_list(doc.get("incidents"))]
        for attr in parse_list(doc.get("attributes")):
            field = attr.get("short_name")
            if field not in KEEP_FIELDS[ns]:
                continue
            try:
                value = json.loads(attr.get("value_json", "null"))
            except json.JSONDecodeError:
                value = attr.get("value_json")
            for v in _flatten_value(value):
                for iid in incidents:
                    if iid is not None:
                        yield (iid, ns, field, v, published)


def build(db_path: Path = paths.DB_PATH) -> dict[str, int]:
    ensure_snapshot()
    snapshot_sha = paths.SNAPSHOT_SHA256
    snap = paths.SNAPSHOT_FILE.name
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tmp = db_path.with_suffix(".tmp")
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(tmp)
    con.executescript(SCHEMA)
    counts: dict[str, int] = {}

    def prov(table: str, source: str) -> None:
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        counts[table] = n
        con.execute("INSERT OR REPLACE INTO provenance VALUES (?,?,?,?,?,?)",
                    (table, source, snapshot_sha, snap, n, now))

    # ---- raw documents (verbatim) for the CC BY-SA collections we use --------------------------------
    for coll in ("incidents", "entities", "classifications", "taxa", "duplicates", "incident_links",
                 "entity_relationships"):
        docs = read_bson(coll)
        con.executemany("INSERT OR REPLACE INTO raw_document VALUES (?,?,?)",
                        ((coll, str(d.get("_id")), json.dumps(d, default=str)) for d in docs))
    prov("raw_document", "aiidprod/*.bson")

    # ---- duplicates ---------------------------------------------------------------------------------
    dup = {to_int(d["duplicate_incident_number"]): to_int(d["true_incident_number"]) for d in read_bson("duplicates")}

    # ---- incidents + incident_report + incident_entity ----------------------------------------------
    inc_docs = read_bson("incidents")
    rows, ir, ie = [], set(), set()
    for d in inc_docs:
        iid = to_int(d["incident_id"])
        date = clean_text(d.get("date"))
        reps = [to_int(r) for r in parse_list(d.get("reports"))]
        rows.append((iid, date, int(date[:4]) if date else None, clean_text(d.get("title")),
                     clean_text(d.get("description")), len(reps), dup.get(iid), clean_text(d.get("created_at"))))
        ir.update((iid, r) for r in reps if r is not None)
        for role, col in ROLE_COLUMNS.items():
            for e in parse_list(d.get(col)):
                ie.add((iid, str(e), role))
    con.executemany("INSERT INTO incidents VALUES (?,?,?,?,?,?,?,?)", rows)
    con.executemany("INSERT INTO incident_report VALUES (?,?)", sorted(ir))
    con.executemany("INSERT INTO incident_entity VALUES (?,?,?)", sorted(ie))
    prov("incidents", "aiidprod/incidents.bson")
    prov("incident_report", "aiidprod/incidents.bson")
    prov("incident_entity", "aiidprod/incidents.bson")

    # ---- reports (text kept locally only; never exported in full) -----------------------------------
    rep_rows = []
    for d in read_bson("reports"):
        text = clean_text(d.get("plain_text")) or clean_text(d.get("text"))
        rep_rows.append((to_int(d["report_number"]), clean_text(d.get("title")), clean_text(d.get("url")),
                         clean_text(d.get("source_domain")) or domain_of(d.get("url")),
                         clean_text(d.get("date_published")),
                         clean_text(d.get("language")), json.dumps(parse_list(d.get("authors"))),
                         text, len(text) if text else 0,
                         0 if str(d.get("is_incident_report")) == "False" else 1))
    con.executemany("INSERT OR REPLACE INTO reports VALUES (?,?,?,?,?,?,?,?,?,?)", rep_rows)
    prov("reports", "aiidprod/reports.bson")

    # ---- entities -----------------------------------------------------------------------------------
    ents = {str(d["entity_id"]): clean_text(d.get("name")) for d in read_bson("entities")}
    con.executemany("INSERT INTO entities VALUES (?,?)", ents.items())
    prov("entities", "aiidprod/entities.bson")
    con.executemany("INSERT INTO entity_relationship VALUES (?,?,?,?)",
                    ((d.get("sub"), d.get("obj"), d.get("pred"), 1 if str(d.get("is_symmetric")) == "True" else 0)
                     for d in read_bson("entity_relationships")))
    prov("entity_relationship", "aiidprod/entity_relationships.bson")

    # ---- expert classifications + taxonomy definitions ----------------------------------------------
    con.executemany("INSERT INTO expert_label VALUES (?,?,?,?,?)", iter_expert_labels(read_bson("classifications")))
    prov("expert_label", "aiidprod/classifications.bson")
    tf_rows = []
    for t in read_bson("taxa"):
        for f in parse_list(t.get("field_list")):
            tf_rows.append((t.get("namespace"), f.get("short_name"), f.get("long_name"),
                            f.get("short_description"), json.dumps(f.get("permitted_values"))))
    con.executemany("INSERT INTO taxonomy_field VALUES (?,?,?,?,?)", tf_rows)
    prov("taxonomy_field", "aiidprod/taxa.bson")

    con.executemany("INSERT INTO incident_link VALUES (?,?,?)",
                    ((to_int(d.get("incident_id")), d.get("sameAs"), d.get("source_namespace"))
                     for d in read_bson("incident_links")))
    prov("incident_link", "aiidprod/incident_links.bson")

    con.commit()
    con.close()
    tmp.replace(db_path)
    return counts


def connect(db_path: Path = paths.DB_PATH) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
