"""Ingestion tests. Unit tests run anywhere; integration tests need the built database."""

import sqlite3

import pytest

from atlas import paths
from atlas.ingest.load import clean_text, domain_of, iter_expert_labels, parse_list

needs_db = pytest.mark.skipif(not paths.DB_PATH.exists(), reason="data/atlas.sqlite not built")


def test_parse_list_handles_json_and_python_repr():
    assert parse_list("[1, 2]") == [1, 2]
    assert parse_list("['a', 'b']") == ["a", "b"]
    assert parse_list("nan") == [] and parse_list(None) == [] and parse_list("[]") == []


def test_clean_text_removes_placeholders():
    for v in ["", " nan ", "None", "unknown", "--", float("nan"), None]:
        assert clean_text(v) is None
    assert clean_text(" Uber ") == "Uber"


def test_domain_of():
    assert domain_of("https://www.nytimes.com/2020/x.html") == "nytimes.com"
    assert domain_of(None) is None


def test_expert_labels_flatten_lists_and_skip_unknown_fields():
    doc = {"namespace": "MIT", "publish": "True", "incidents": "[7]",
           "attributes": "[{'short_name': 'Risk Domain', 'value_json': '\"3. Misinformation\"'},"
                         " {'short_name': 'Ignored', 'value_json': '\"x\"'}]"}
    assert list(iter_expert_labels([doc])) == [(7, "MIT", "Risk Domain", "3. Misinformation", 1)]
    doc2 = {"namespace": "GMF", "publish": "False", "incidents": "[8]",
            "attributes": "[{'short_name': 'Known AI Technology', 'value_json': '[\"Face Detection\", \"CNN\"]'}]"}
    assert [r[3] for r in iter_expert_labels([doc2])] == ["Face Detection", "CNN"]


@needs_db
def test_database_integrity():
    con = sqlite3.connect(paths.DB_PATH)
    n_inc = con.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    assert n_inc > 1500
    # incident ids unique & every bridge row points at a known incident
    assert con.execute("SELECT COUNT(*) FROM incident_report WHERE incident_id NOT IN (SELECT incident_id FROM incidents)").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM incident_entity WHERE entity_id NOT IN (SELECT entity_id FROM entities)").fetchone()[0] == 0
    roles = {r[0] for r in con.execute("SELECT DISTINCT role FROM incident_entity")}
    assert roles == {"deployer", "developer", "harmed"}
    # no placeholder strings survive in clean columns
    assert con.execute("SELECT COUNT(*) FROM incidents WHERE lower(title) IN ('nan','none','') ").fetchone()[0] == 0
    # provenance recorded for every clean table
    assert con.execute("SELECT COUNT(*) FROM provenance").fetchone()[0] >= 9
