"""Plan and prepare extraction batches.

* ``plan`` (deterministic, seed 13) orders incidents: a 20-incident stratified **pilot** first, then every incident
  that has CSETv1 or GMF expert labels (needed for evaluation), then the remainder in a stratified-shuffled order,
  so that stopping early still leaves a representative sample. The plan is committed (``data/enrich/plan.json``).
* ``prepare`` writes git-ignored batch input files with report excerpts to ``data/interim/batches/``.

Report text is third-party content: batch inputs are never committed.
"""

from __future__ import annotations

import json
import random
import sys
from typing import Any

import pandas as pd

from atlas import paths
from atlas.ingest.load import connect

BATCH_SIZE = 12
EXCERPT_CHARS = 2500
MAX_REPORTS = 3
SEED = 13
PLAN_PATH = paths.ENRICH / "plan.json"
IN_DIR = paths.DATA / "interim" / "batches"
OUT_DIR = paths.ENRICH / "raw"


def _strata(con) -> pd.DataFrame:
    inc = pd.read_sql_query("SELECT incident_id, year, n_reports FROM incidents WHERE is_duplicate_of IS NULL AND n_reports > 0", con)
    mit = pd.read_sql_query("SELECT incident_id, value AS mit FROM expert_label WHERE namespace='MIT' AND field='Risk Domain'", con)
    inc = inc.merge(mit.drop_duplicates("incident_id"), how="left")
    inc["mit"] = inc.mit.fillna("none")
    inc["year_bin"] = pd.cut(inc.year, [0, 2016, 2019, 2022, 2023, 2024, 2025, 2100],
                             labels=["<=2016", "2017-19", "2020-22", "2023", "2024", "2025", "2026"]).astype(str)
    inc["rep_bin"] = pd.cut(inc.n_reports, [0, 1, 4, 1000], labels=["1", "2-4", "5+"]).astype(str)
    return inc


def plan() -> dict[str, Any]:
    con = connect()
    inc = _strata(con)
    rng = random.Random(SEED)
    # --- pilot: round-robin over year bins, varying report bins and MIT domains -----------------------
    pilot: list[int] = []
    used_mit: dict[str, int] = {}
    year_bins = sorted(inc.year_bin.unique())
    rep_bins = ["1", "2-4", "5+"]
    i = 0
    while len(pilot) < 20:
        yb, rb = year_bins[i % len(year_bins)], rep_bins[(i // len(year_bins)) % 3]
        cand = inc[(inc.year_bin == yb) & (inc.rep_bin == rb) & ~inc.incident_id.isin(pilot)]
        if len(cand):
            cand = cand.assign(u=cand.mit.map(lambda m: used_mit.get(m, 0)))
            cand = cand[cand.u == cand.u.min()]
            pick = cand.sample(1, random_state=rng.randint(0, 10**6)).iloc[0]
            pilot.append(int(pick.incident_id))
            used_mit[pick.mit] = used_mit.get(pick.mit, 0) + 1
        i += 1
    expert = pd.read_sql_query(
        "SELECT DISTINCT incident_id FROM expert_label WHERE namespace IN ('CSETv1','GMF')", con).incident_id
    p1 = sorted(set(expert) & set(inc.incident_id) - set(pilot))
    rng.shuffle(p1)
    rest = inc[~inc.incident_id.isin(pilot + p1)].copy()
    # stratified shuffle: interleave year bins so any prefix is year-balanced proportionally
    rest["r"] = [rng.random() for _ in range(len(rest))]
    rest["rank"] = rest.groupby("year_bin").r.rank(pct=True)
    p2 = rest.sort_values("rank").incident_id.astype(int).tolist()
    order = p1 + p2
    batches = [{"batch": "pilot_00", "phase": "pilot", "incidents": pilot[:10]},
               {"batch": "pilot_01", "phase": "pilot", "incidents": pilot[10:]}]
    for k in range(0, len(order), BATCH_SIZE):
        chunk = order[k:k + BATCH_SIZE]
        batches.append({"batch": f"b{k // BATCH_SIZE:03d}", "phase": "expert" if chunk[0] in set(p1) else "rest",
                        "incidents": chunk})
    out = {"seed": SEED, "batch_size": BATCH_SIZE, "n_incidents": len(pilot) + len(order),
           "pilot": pilot, "batches": batches}
    paths.ENRICH.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(out, indent=1))
    return out


def _choose_reports(con, iid: int) -> list[dict[str, Any]]:
    rows = con.execute(
        """SELECT r.report_number, r.title, r.source_domain, r.language, r.text, r.text_chars
           FROM incident_report ir JOIN reports r USING (report_number)
           WHERE ir.incident_id = ? AND r.is_incident_report = 1 AND r.text_chars > 0""", (iid,)).fetchall()
    rows = sorted(rows, key=lambda r: (r["language"] not in (None, "en"), r["text_chars"] < 600, r["report_number"]))
    return [{"report_number": r["report_number"], "title": r["title"], "source": r["source_domain"],
             "excerpt": r["text"][:EXCERPT_CHARS]} for r in rows[:MAX_REPORTS]]


def incident_input(con, iid: int) -> dict[str, Any]:
    inc = con.execute("SELECT * FROM incidents WHERE incident_id = ?", (iid,)).fetchone()
    ents = con.execute(
        """SELECT ie.role, e.name FROM incident_entity ie JOIN entities e USING (entity_id)
           WHERE ie.incident_id = ? AND ie.role IN ('developer','deployer')""", (iid,)).fetchall()
    return {"incident_id": iid, "title": inc["title"], "date": inc["date"], "description": inc["description"],
            "developers": sorted({e["name"] for e in ents if e["role"] == "developer"}),
            "deployers": sorted({e["name"] for e in ents if e["role"] == "deployer"}),
            "reports": _choose_reports(con, iid)}


def prepare(batch_names: list[str] | None = None) -> list[str]:
    p = json.loads(PLAN_PATH.read_text())
    con = connect()
    IN_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for b in p["batches"]:
        if batch_names and b["batch"] not in batch_names:
            continue
        path = IN_DIR / f"{b['batch']}.json"
        if not path.exists():
            path.write_text(json.dumps([incident_input(con, i) for i in b["incidents"]], ensure_ascii=False, indent=1))
        written.append(str(path))
    return written


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        pl = plan()
        print(f"{pl['n_incidents']} incidents in {len(pl['batches'])} batches; pilot={pl['pilot']}")
    elif cmd == "prepare":
        print("\n".join(prepare(sys.argv[2:] or None)))
