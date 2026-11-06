"""Extraction progress: which batches are done, which incidents are missing, and fill batches for the gaps.

``python -m atlas.extract.status`` prints a summary; ``... status fill`` writes fill-batch inputs
(``data/interim/batches/fill_XX.json``) for incidents whose batch is complete but whose record is missing or failed
validation, so they can be re-coded.
"""

from __future__ import annotations

import json
import sys

from atlas import paths
from atlas.extract.batches import IN_DIR, OUT_DIR, PLAN_PATH, incident_input
from atlas.ingest.load import connect


def status() -> dict:
    plan = json.loads(PLAN_PATH.read_text())
    loaded = set()
    ext = paths.PROCESSED / "extractions.jsonl"
    if ext.exists():
        loaded = {json.loads(l)["incident_id"] for l in ext.read_text().splitlines()}
    done, pending, missing = [], [], []
    for b in plan["batches"]:
        if (OUT_DIR / f"{b['batch']}.json").exists():
            done.append(b["batch"])
            missing += [i for i in b["incidents"] if i not in loaded]
        else:
            pending.append(b["batch"])
    fills = sorted(p.stem for p in OUT_DIR.glob("fill_*.json"))
    missing = [i for i in missing if i not in loaded]
    return {"batches_done": len(done), "batches_total": len(plan["batches"]), "incidents_loaded": len(loaded),
            "incidents_total": plan["n_incidents"], "missing_in_done_batches": missing,
            "next_pending": pending[:6], "fill_batches_done": fills}


def write_fill(missing: list[int], size: int = 12) -> list[str]:
    con = connect()
    existing = sorted(IN_DIR.glob("fill_*.json"))
    k = len(existing)
    out = []
    for s in range(0, len(missing), size):
        path = IN_DIR / f"fill_{k:02d}.json"
        path.write_text(json.dumps([incident_input(con, i) for i in missing[s:s + size]], ensure_ascii=False, indent=1))
        out.append(str(path))
        k += 1
    return out


if __name__ == "__main__":
    st = status()
    if len(sys.argv) > 1 and sys.argv[1] == "fill":
        print("\n".join(write_fill(st["missing_in_done_batches"])))
    else:
        print(json.dumps(st, indent=1))
