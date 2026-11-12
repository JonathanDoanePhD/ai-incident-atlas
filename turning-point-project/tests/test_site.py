"""The website must be generated from docs/, cite only verified references, and show no findings."""
import csv
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_site_data", ROOT / "scripts" / "build_site_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_site_builds_and_cites_only_bib_keys():
    b = _load_builder()
    data = b.build()
    keys = b.bib_keys()
    for s in b.STAGES:
        for item in s["evidence"] + s["open"]:
            assert "cite" not in item or item["cite"]  # resolved to author-year
    assert {r["citation_key"] for r in data["evidence"]} <= keys
    assert len(data["datasets"]) == len(b.DATASET_META)


def test_evidence_matrix_rows_have_dois_logged_as_verified():
    log = {json.loads(l)["doi"].lower() for l in (ROOT / "docs" / "citation_verification_log.jsonl").read_text().splitlines() if l.strip()}
    with open(ROOT / "docs" / "evidence_matrix.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["doi"]:
                assert r["doi"].lower() in log, r["citation_key"]


def test_site_data_has_no_findings_and_findings_are_aggregate_only():
    js = (ROOT / "website" / "data" / "site.js").read_text()
    data = json.loads(js[js.index("=") + 1:].rstrip().rstrip(";"))
    assert not any(k in data for k in ("findings", "estimates", "results"))
    f = ROOT / "website" / "data" / "findings.js"
    if f.exists():  # generated only from outputs/paper1_results.json
        txt = f.read_text()
        fd = json.loads(txt[txt.index("=") + 1:].rstrip().rstrip(";"))
        for p in fd["parents"].values():
            for row in p["descriptives"]:
                assert row["n_valid_exposure"] >= 10  # small-cell rule
        assert "R0000100" not in txt and "pubid" not in txt.lower()  # no respondent identifiers


def test_add_health_marked_excluded():
    b = _load_builder()
    ah = next(d for d in b.build()["datasets"] if d["short"] == "Add Health")
    assert "forbids" in ah["access"]


def test_html_basic_accessibility():
    html = (ROOT / "website" / "index.html").read_text()
    assert '<html lang="en">' in html and 'class="skip"' in html
    for m in re.finditer(r"<input[^>]*id=\"(\w+)\"", html):
        assert f'for="{m.group(1)}"' in html or re.search(rf"<label[^>]*>[^<]*<input[^>]*id=\"{m.group(1)}\"", html) \
            or re.search(rf"<label[^>]*><input[^>]*id=\"{m.group(1)}\"", html), m.group(1)
