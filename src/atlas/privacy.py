"""Privacy rules for the public atlas.

Entity kinds (organization / government / product / group / generic / public_figure / private_individual) come from
an LLM classification pass (``prompts/entity_kind_v1.md``) stored in ``data/enrich/entity_kinds.csv``. The file is
keyed by an (unsalted) SHA-1 prefix of the entity id so that the public repository does not list private
individuals' names. Entities missing from the file fall back to a conservative heuristic.

Only entities of kind ``private_individual`` are hidden; their names are also redacted from free text.
"""

from __future__ import annotations

import csv
import hashlib
import re
from collections import defaultdict
from functools import lru_cache

from atlas import paths

KINDS_PATH = paths.ENRICH / "entity_kinds.csv"
VISIBLE_KINDS = {"organization", "government", "product", "group", "generic", "public_figure"}
SHOWN_AS_ACTOR = {"organization", "government", "product", "public_figure"}

_ORG_HINTS = re.compile(
    r"\b(inc|llc|ltd|corp|company|co|group|bank|university|college|school|police|department|ministry|agency|"
    r"government|council|court|hospital|news|times|post|media|tv|radio|association|foundation|institute|lab|labs|"
    r"party|club|network|services|systems|technologies|ai|app|users|people|residents|public|community|students|"
    r"workers|employees|customers|drivers|voters|citizens|patients|children|women|men|families|investors|owners|"
    r"developers|deployers|platform|platforms|unknown|unnamed|unidentified|scammers|individuals)\b", re.I)


def entity_key(entity_id: str) -> str:
    return hashlib.sha1(entity_id.encode("utf-8")).hexdigest()[:16]


@lru_cache(maxsize=1)
def _kinds() -> dict[str, str]:
    if not KINDS_PATH.exists():
        return {}
    with open(KINDS_PATH) as f:
        return {r["key"]: r["kind"] for r in csv.DictReader(f)}


def heuristic_kind(name: str) -> str:
    """Conservative fallback: names that look like 'Firstname Lastname' are treated as private individuals."""
    if not name:
        return "generic"
    if _ORG_HINTS.search(name):
        return "group"
    toks = [t for t in re.split(r"\s+", name.strip()) if t]
    if 2 <= len(toks) <= 4 and all(t[:1].isupper() for t in toks) and not any(ch.isdigit() for ch in name):
        return "private_individual"
    return "organization"


def entity_kind(entity_id: str, name: str | None) -> str:
    return _kinds().get(entity_key(entity_id)) or heuristic_kind(name or entity_id)


def private_names_by_incident(con) -> dict[int, list[str]]:
    """Names of private individuals linked (in any role) to each incident."""
    out: dict[int, list[str]] = defaultdict(list)
    for r in con.execute("SELECT ie.incident_id, e.entity_id, e.name FROM incident_entity ie JOIN entities e USING (entity_id)"):
        if entity_kind(r[1], r[2]) == "private_individual" and r[2]:
            out[r[0]].append(r[2])
    return dict(out)


def all_private_names(con) -> list[str]:
    names = set()
    for r in con.execute("SELECT DISTINCT e.entity_id, e.name FROM incident_entity ie JOIN entities e USING (entity_id)"):
        if r[1] and entity_kind(r[0], r[1]) == "private_individual":
            names.add(r[1])
    return sorted(names)
