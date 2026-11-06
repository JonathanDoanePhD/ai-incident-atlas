"""Checks on the exported public bundle: privacy, excerpt length, placeholders."""

import json
import re

import pytest

from atlas import paths

DATA = paths.APP_DATA
needs_bundle = pytest.mark.skipif(not (DATA / "nodes.json").exists(), reason="bundle not exported")
needs_db = pytest.mark.skipif(not paths.DB_PATH.exists(), reason="data/atlas.sqlite not built")
PLACEHOLDER = re.compile(r'"(nan|NaN|None|null|unknown|Unknown|)"')


def _profiles():
    for p in sorted((DATA / "profiles").glob("*.json")):
        yield from json.loads(p.read_text()).values()


@needs_bundle
def test_quotes_and_headlines_are_short():
    for prof in _profiles():
        for r in prof["reports"]:
            assert len(r["title"].rstrip("…").split()) <= 25
        for tags in (prof.get("tags") or {}).values():
            for t in tags:
                if "q" in t:
                    assert len(t["q"].rstrip("…").split()) <= 25
                    assert t.get("url") or t.get("src")


@needs_bundle
def test_no_report_text_field_exported():
    for prof in _profiles():
        assert "text" not in prof
        for r in prof["reports"]:
            assert set(r) <= {"n", "title", "url", "source", "date"}


@needs_bundle
def test_no_raw_placeholders_in_nodes():
    raw = (DATA / "nodes.json").read_text()
    assert not re.search(r'"t":"(nan|None|)"', raw)
    nodes = json.loads(raw)
    for n in nodes:
        for k in ("sec", "tech", "fm", "harm", "org"):
            assert all(v not in ("nan", "None", "", "unknown") for v in n[k])


@needs_bundle
@needs_db
def test_private_individuals_not_in_public_entities():
    import sqlite3

    from atlas.privacy import entity_kind

    ents = json.loads((DATA / "entities.json").read_text())
    con = sqlite3.connect(paths.DB_PATH)
    names = dict(con.execute("SELECT entity_id, name FROM entities"))
    for eid in ents:
        assert entity_kind(eid, names.get(eid)) != "private_individual"


@needs_bundle
@needs_db
def test_private_names_not_in_summaries():
    import sqlite3

    from atlas.extract.grounding import contains_private_name
    from atlas.privacy import private_names_by_incident

    con = sqlite3.connect(paths.DB_PATH)
    priv = private_names_by_incident(con)
    nodes = {n["id"]: n for n in json.loads((DATA / "nodes.json").read_text())}
    bad = [i for i, n in nodes.items() if n["x"] and contains_private_name(n["s"] + " " + n["t"], priv.get(i, []))]
    assert bad == []
