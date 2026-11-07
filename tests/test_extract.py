"""Schema validation and quote-grounding tests."""

import pytest
from pydantic import ValidationError

from atlas.extract.grounding import (check_record, contains_private_name, is_grounded, normalize,
                                     redact_private_names, repair, snap)
from atlas.extract.schema import IncidentRecord, Tag
from atlas.privacy import heuristic_kind

REPORT = ("An Uber self-driving SUV struck and killed a woman in Tempe, Arizona — the first known pedestrian "
          "fatality involving an autonomous vehicle. The car’s sensors detected her six seconds before impact.")


def _rec(**over):
    base = {
        "incident_id": 4, "summary": "A self-driving test car struck and killed a pedestrian.",
        "technical_summary": "The perception system misclassified the pedestrian and did not brake.",
        "tags": {"technology": [{"id": "autonomous_vehicle", "evidence": "confirmed",
                                 "quote": "An Uber self-driving SUV struck and killed a woman", "report": 1}],
                 "failure_mode": [{"id": "robustness_failure", "evidence": "inferred"}]},
        "primary_failure_mode": "robustness_failure",
        "severity": {"id": "s4_critical", "evidence": "confirmed", "quote": "first known pedestrian fatality", "report": 1},
        "intent": "unintentional", "cause_entity": "ai"}
    base.update(over)
    return IncidentRecord.model_validate(base)


def test_normalization_ignores_case_punctuation_and_unicode_quotes():
    assert normalize("The car’s  sensors—detected") == "the car s sensors detected"
    assert is_grounded("the car's sensors detected her", REPORT)
    assert is_grounded("Tempe,  Arizona -- the first", REPORT)


def test_ungrounded_quote_detected():
    assert not is_grounded("the car never saw the pedestrian", REPORT)


def test_confirmed_tag_requires_quote():
    with pytest.raises(ValidationError):
        Tag(id="x", evidence="confirmed")


def test_unknown_term_rejected():
    with pytest.raises(ValidationError):
        _rec(tags={"technology": [{"id": "quantum_ai", "evidence": "inferred"}]})


def test_long_quote_rejected():
    with pytest.raises(ValidationError):
        Tag(id="x", evidence="confirmed", quote=" ".join(["word"] * 30), report=1)


def test_primary_failure_mode_added_to_tags():
    r = _rec(tags={}, primary_failure_mode="hallucination")
    assert [t.id for t in r.tags.failure_mode] == ["hallucination"]


def test_check_record_flags_unlinked_report_and_missing_quote():
    r = _rec()
    assert check_record(r, {1: REPORT}, []) == []
    issues = check_record(r, {2: REPORT}, [])
    assert {i.problem for i in issues} == {"report_not_linked"}


def test_snap_repairs_near_verbatim_quote():
    fixed = snap("An Uber self driving SUV struck and killed the woman", REPORT)
    assert fixed is not None and is_grounded(fixed, REPORT)


def test_repair_downgrades_fabricated_quote():
    r = _rec(severity={"id": "s4_critical", "evidence": "confirmed", "quote": "Totally invented sentence about policy", "report": 1})
    r, log = repair(r, {1: REPORT}, [])
    assert r.severity.evidence == "inferred" and r.severity.quote is None
    assert log[0]["action"] == "downgrade"
    assert check_record(r, {1: REPORT}, []) == []


def test_private_names_detected_and_redacted():
    names = ["Jane Q. Example"]
    assert contains_private_name("Police said Jane Q. Example was injured", names)
    assert contains_private_name("Example was injured", names)  # distinctive surname
    assert redact_private_names("Jane Q. Example was hurt", names) == "[name withheld] was hurt"


def test_quote_with_private_name_is_downgraded():
    text = "Witnesses said Jane Q. Example was crossing the street when the robotaxi hit her."
    r = _rec(severity={"id": "s3_severe", "evidence": "confirmed", "quote": "Jane Q. Example was crossing the street", "report": 1})
    r, log = repair(r, {1: text + REPORT}, ["Jane Q. Example"])
    assert r.severity.evidence == "inferred" and log[-1]["reason"] == "private_name" and log[-1]["old"] is None


def test_heuristic_kind():
    assert heuristic_kind("John Smith") == "private_individual"
    assert heuristic_kind("Tesla") == "organization"
    assert heuristic_kind("Black voters") == "group"


def test_group_names_do_not_trigger_surname_matching():
    names = ["Employee of Department of Families Fairness and Housing"]
    assert not contains_private_name("Department of Families, Fairness and Housing (Victoria)", names)


def test_repair_reattributes_quote_to_the_right_report():
    r = _rec()
    r, log = repair(r, {2: "unrelated text", 1: REPORT}, [])  # quotes cite report 1 → fine
    assert log == []
    r = _rec(severity={"id": "s4_critical", "evidence": "confirmed", "quote": "first known pedestrian fatality", "report": 2})
    r, log = repair(r, {2: "unrelated text", 1: REPORT}, [])
    assert r.severity.report == 1 and r.severity.evidence == "confirmed" and log[0]["action"] == "reattribute"
