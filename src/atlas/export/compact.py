"""Lossless compaction of the app bundle.

The similarity explanation sentences were stored twice: once in ``edges.json`` and again, written out in full, in every
profile's ``related`` list (~2.1 MB of repeated text). This step moves all sentences into one shared
``explanations.json`` table and stores references instead:

* ``explanations.json`` — list of strings (edge explanations first, in their original order, then any extra sentences
  used only by ``related`` lists).
* ``edges.json`` — ``{"views": {view: [[source, target, weight, explanation_index], ...]}}``.
* ``profiles/p*.json`` — ``related`` becomes ``[[incident_id, weight, explanation_index], ...]``.

Nothing is dropped: the app re-expands references when loading (``app/src/lib/data.ts``). Idempotent: re-running on
an already-compacted bundle is a no-op.

    python -m atlas.export.compact app/public/data
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SEP = (",", ":")


def compact_bundle(out: Path) -> dict:
    out = Path(out)
    edges_f, expl_f = out / "edges.json", out / "explanations.json"
    edges = json.loads(edges_f.read_text())
    if "explanations" not in edges and expl_f.exists():
        return {"status": "already compact"}
    strings: list[str] = list(edges["explanations"])
    index = {s: i for i, s in enumerate(strings)}
    n_related = 0
    for pf in sorted((out / "profiles").glob("p*.json")):
        chunk = json.loads(pf.read_text())
        for prof in chunk.values():
            rel = prof.get("related") or []
            if rel and isinstance(rel[0], dict):
                packed = []
                for r in rel:
                    k = index.get(r["why"])
                    if k is None:
                        k = index[r["why"]] = len(strings)
                        strings.append(r["why"])
                    packed.append([r["id"], r["w"], k])
                    n_related += 1
                prof["related"] = packed
        pf.write_text(json.dumps(chunk, ensure_ascii=False, separators=SEP))
    expl_f.write_text(json.dumps(strings, ensure_ascii=False, separators=SEP))
    edges_f.write_text(json.dumps({"views": edges["views"]}, ensure_ascii=False, separators=SEP))
    return {"status": "compacted", "explanations": len(strings), "related_links": n_related}


if __name__ == "__main__":
    print(compact_bundle(Path(sys.argv[1] if len(sys.argv) > 1 else "app/public/data")))
