"""Export the static JSON bundle consumed by the app (``app/public/data``).

Privacy & licensing rules enforced here (tested in tests/test_export.py):
* No report full text. Quotes ≤ 25 words, each with publisher domain + link. Report headlines truncated to 25 words.
* Names of private individuals linked to an incident are redacted from AIID titles/descriptions; private
  individuals never appear in entity lists.
* Placeholder strings ("nan", "unknown", "", "None") are removed, never shown raw.

Files
-----
* ``meta.json``        — taxonomy labels, palettes, counts, versions, attribution.
* ``nodes.json``       — one compact record per incident (fields documented in ``NODE_FIELDS``).
* ``edges.json``       — per similarity view: ``[[source, target, weight, explanation_index], ...]`` + string table.
* ``profiles/p{k}.json`` — detailed profiles, chunked by ``incident_id // 100``.
* ``clusters.json``, ``insights.json``, ``evaluation.json``, ``entities.json``.
"""

from __future__ import annotations

import json
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import numpy as np

from atlas import paths, taxonomy
from atlas.extract.grounding import redact_private_names
from atlas.graph.similarity import load_features, related, view_matrices
from atlas.ingest.load import clean_text, connect
from atlas.privacy import SHOWN_AS_ACTOR, entity_kind, private_names_by_incident

CHUNK = 100
MAX_WORDS = 25
SEV = {"s0_none": 0, "s1_minor": 1, "s2_moderate": 2, "s3_severe": 3, "s4_critical": 4}
NODE_FIELDS = {
    "id": "AIID incident id", "t": "title (private names redacted)", "y": "incident year", "d": "incident date",
    "s": "our plain-language summary", "sec": "sector terms", "tech": "technology terms", "fm": "failure-mode terms",
    "pfm": "primary failure mode", "harm": "harm-type terms", "pop": "affected-population terms",
    "life": "lifecycle stages", "sev": "severity rank 0–4 or null", "rd": "MIT-aligned risk domain id",
    "int": "intent", "cause": "cause entity", "org": "visible developer/deployer entity ids",
    "nrep": "number of reports", "cl": "cluster id", "p": "3-D layout position", "br": "bridge incident (1/0)",
    "x": "1 if our evidence-grounded LLM extraction exists for the incident",
    "pr": "1 if tags are kNN-predicted from coded neighbours (no LLM extraction)",
}

# Accessible categorical palette (Okabe–Ito + Tableau-like extensions), gray reserved for unknown.
PALETTE = ["#56B4E9", "#E69F00", "#009E73", "#F0E442", "#CC79A7", "#D55E00", "#0072B2", "#9ADBE8", "#B79AF0",
           "#F28E8E", "#8CD17D", "#FFBE7D", "#A0CBE8", "#F1CE63", "#86BCB6", "#E15759", "#B6992D", "#D4A6C8",
           "#79706E", "#59A14F", "#FF9DA7", "#9C755F", "#BAB0AC", "#4E79A7"]
UNKNOWN = "#6b7280"


def words(text: str | None, n: int = MAX_WORDS) -> str | None:
    t = clean_text(text)
    if t is None:
        return None
    w = t.split()
    return " ".join(w[:n]) + ("…" if len(w) > n else "")


def clean_list(xs) -> list:
    return [x for x in (clean_text(v) for v in xs or []) if x is not None]


def build() -> dict[str, Any]:
    con = connect()
    out = paths.APP_DATA
    if out.exists():
        shutil.rmtree(out)
    (out / "profiles").mkdir(parents=True)

    tax = taxonomy.load()
    private = private_names_by_incident(con)
    ext = {r["incident_id"]: r for r in map(json.loads, (paths.PROCESSED / "extractions.jsonl").read_text().splitlines())}
    pred_path = paths.PROCESSED / "predicted.jsonl"
    pred = {r["incident_id"]: r for r in map(json.loads, pred_path.read_text().splitlines())} if pred_path.exists() else {}
    cv_path = paths.PROCESSED / "propagation_cv.json"
    cv = json.loads(cv_path.read_text()) if cv_path.exists() else None
    layout = np.load(paths.PROCESSED / "layout.npz")
    pos = {int(i): (xyz.tolist(), int(c)) for i, xyz, c in zip(layout["incident_ids"], layout["xyz"], layout["labels"])}
    bridges = {b["incident_id"] for b in json.loads((paths.PROCESSED / "bridges.json").read_text())}
    incs = con.execute("SELECT * FROM incidents WHERE is_duplicate_of IS NULL ORDER BY incident_id").fetchall()

    # ---- visible organizations -------------------------------------------------------------------
    org_by_inc: dict[int, dict[str, set[str]]] = defaultdict(lambda: {"developer": set(), "deployer": set()})
    ent_names: dict[str, str] = {}
    ent_kind: dict[str, str] = {}
    harmed_groups: dict[int, list[str]] = defaultdict(list)
    for iid, role, eid, name in con.execute(
            "SELECT ie.incident_id, ie.role, e.entity_id, e.name FROM incident_entity ie JOIN entities e USING (entity_id)"):
        kind = entity_kind(eid, name)
        if role in ("developer", "deployer") and kind in SHOWN_AS_ACTOR:
            org_by_inc[iid][role].add(eid)
            ent_names[eid] = clean_text(name) or eid
            ent_kind[eid] = kind
        elif role == "harmed" and kind in ("group", "organization", "government") and clean_text(name):
            harmed_groups[iid].append(clean_text(name))

    # ---- nodes -------------------------------------------------------------------------------------
    nodes = []
    for inc in incs:
        iid = inc["incident_id"]
        names = private.get(iid, [])
        r = ext.get(iid)
        pr = pred.get(iid) if r is None else None
        if r:
            tags = lambda d: [t["id"] for t in r["tags"].get(d, [])]  # noqa: E731
        elif pr:
            tags = lambda d: list(pr.get(d, []))  # noqa: E731
        else:
            tags = lambda d: []  # noqa: E731
        p, cl = pos.get(iid, ([0.0, 0.0, 0.0], -1))
        sev = SEV.get((r.get("severity") or {}).get("id")) if r else (SEV.get(pr.get("severity")) if pr else None)
        src = r or pr or {}
        nodes.append({
            "id": iid, "t": redact_private_names(inc["title"] or f"Incident {iid}", names),
            "y": inc["year"], "d": inc["date"],
            "s": r["summary"] if r else redact_private_names(words(inc["description"], 60) or "", names),
            "sec": tags("sector"), "tech": tags("technology"), "fm": tags("failure_mode"),
            "pfm": src.get("primary_failure_mode"), "harm": tags("harm_type"),
            "pop": tags("affected_population"), "life": tags("lifecycle_stage"), "sev": sev,
            "rd": src.get("risk_domain"), "int": src.get("intent"), "cause": src.get("cause_entity"),
            "org": sorted(org_by_inc[iid]["developer"] | org_by_inc[iid]["deployer"]),
            "nrep": inc["n_reports"], "cl": cl, "p": [round(v, 3) for v in p], "br": int(iid in bridges),
            "x": int(r is not None), "pr": int(pr is not None)})
    (out / "nodes.json").write_text(json.dumps(nodes, ensure_ascii=False, separators=(",", ":")))

    # ---- edges -------------------------------------------------------------------------------------
    edges = json.loads((paths.PROCESSED / "edges.json").read_text())
    strings: dict[str, int] = {}
    packed = {}
    for view, lst in edges.items():
        packed[view] = [[e["source"], e["target"], round(e["weight"], 3), strings.setdefault(e["explanation"], len(strings))]
                        for e in lst]
    (out / "edges.json").write_text(json.dumps({"explanations": list(strings), "views": packed}, ensure_ascii=False,
                                               separators=(",", ":")))

    # ---- profiles ----------------------------------------------------------------------------------
    f = load_features()
    mats = view_matrices(f)
    row = {int(i): k for k, i in enumerate(f.ids)}
    rep_rows = defaultdict(list)
    for rr in con.execute("""SELECT ir.incident_id, r.report_number, r.title, r.url, r.source_domain, r.date_published
                             FROM incident_report ir JOIN reports r USING (report_number)
                             WHERE r.is_incident_report = 1 ORDER BY r.date_published"""):
        rep_rows[rr[0]].append(rr)
    chunks: dict[int, dict] = defaultdict(dict)
    for inc in incs:
        iid = inc["incident_id"]
        names = private.get(iid, [])
        r = ext.get(iid)
        reps = {x[1]: x for x in rep_rows[iid]}
        prof: dict[str, Any] = {
            "id": iid, "aiid_url": f"https://incidentdatabase.ai/cite/{iid}/",
            "description": redact_private_names(clean_text(inc["description"]) or "", names) or None,
            "reports": [{"n": x[1], "title": words(redact_private_names(clean_text(x[2]) or "Untitled report", names)),
                         "url": clean_text(x[3]), "source": clean_text(x[4]),
                         "date": (clean_text(x[5]) or "")[:10] or None} for x in rep_rows[iid][:40]],
            "developers": sorted(ent_names[e] for e in org_by_inc[iid]["developer"]),
            "deployers": sorted(ent_names[e] for e in org_by_inc[iid]["deployer"]),
            "harmed_groups": sorted(set(harmed_groups[iid]))[:12],
        }
        if r:
            def tag_out(t):
                o = {"id": t["id"], "ev": t["evidence"]}
                if t.get("quote") and t.get("report") in reps:
                    x = reps[t["report"]]
                    o.update({"q": words(t["quote"]), "rn": t["report"], "src": clean_text(x[4]), "url": clean_text(x[3])})
                return o
            prof.update({
                "technical_summary": r["technical_summary"], "systems": clean_list(r["systems"]),
                "tags": {d: [tag_out(t) for t in r["tags"].get(d, [])] for d in taxonomy.TAG_DIMENSIONS},
                "severity": tag_out(r["severity"]) if r.get("severity") else None,
                "risk_subdomain": r.get("risk_subdomain"), "notes": clean_text(r.get("notes"))})
        if r is None and iid in pred:
            prof["predicted"] = {"confidence": pred[iid].get("confidence"), "risk_subdomain": None}
        if iid in row:
            prof["related"] = [{"id": j, "w": round(w, 3), "why": why} for j, w, why in related(f, mats, row[iid], 8)]
        chunks[iid // CHUNK][str(iid)] = prof
    for k, v in chunks.items():
        (out / "profiles" / f"p{k}.json").write_text(json.dumps(v, ensure_ascii=False, separators=(",", ":")))

    # ---- entities, clusters, insights, evaluation ---------------------------------------------------
    counts = defaultdict(int)
    for v in org_by_inc.values():
        for e in v["developer"] | v["deployer"]:
            counts[e] += 1
    ents = {e: {"name": ent_names[e], "kind": ent_kind[e], "n": counts[e]} for e in ent_names}
    (out / "entities.json").write_text(json.dumps(ents, ensure_ascii=False, separators=(",", ":")))
    for name in ("clusters", "insights", "evaluation", "entity_network", "bridges"):
        src = paths.PROCESSED / f"{name}.json"
        if src.exists():
            data = json.loads(src.read_text())
            if name == "evaluation":
                data = slim_evaluation(data)
            (out / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))

    dims = {}
    for d, spec in tax["dimensions"].items():
        terms = spec["terms"]
        dims[d] = {"label": spec["label"], "multi": spec.get("multi", True),
                   "terms": [{"id": str(t["id"]), "label": t["label"], "color": PALETTE[k % len(PALETTE)],
                              **({"parent": t["parent"]} if "parent" in t else {})} for k, t in enumerate(terms)],
                   **({"parents": spec["parents"]} if "parents" in spec else {})}
    meta = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "snapshot": paths.SNAPSHOT_FILE.name, "snapshot_date": "2026-11-02",
        "taxonomy_version": tax["version"], "n_incidents": len(nodes), "n_extracted": sum(n["x"] for n in nodes),
        "dimensions": dims, "unknown_color": UNKNOWN, "palette": PALETTE, "node_fields": NODE_FIELDS,
        "views": list(packed), "n_predicted": sum(n["pr"] for n in nodes),
        "propagation_cv": cv, "license": {
            "data": "CC BY-SA 4.0", "code": "MIT",
            "attribution": "Incident data from the AI Incident Database (incidentdatabase.ai), Responsible AI "
                           "Collaborative, licensed CC BY-SA 4.0. Report excerpts belong to their publishers."},
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")))
    sizes = {p.name: p.stat().st_size for p in out.glob("*.json")}
    sizes["profiles/*"] = sum(p.stat().st_size for p in (out / "profiles").glob("*.json"))
    return {"total_mb": round(sum(sizes.values()) / 1e6, 2), "sizes": sizes}


def slim_evaluation(ev: dict) -> dict:
    """Drop long example lists from the app copy (they stay in reports/evaluation.md)."""
    ev = json.loads(json.dumps(ev))
    ev["mit"]["disagreements"] = ev["mit"]["disagreements"][:8]
    for k in ("gmf_failure", "cset_sector"):
        if "disagreements" in ev.get(k, {}):
            ev[k]["disagreements"] = ev[k]["disagreements"][:8]
    return ev


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
