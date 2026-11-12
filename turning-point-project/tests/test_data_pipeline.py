import json

import numpy as np
import pandas as pd
import pytest

from turning_point.constructs import ConstructDefinition, cronbach_alpha, score_construct, score_scale
from turning_point.ingestion import DatasetSpec, load_extract
from turning_point.preprocessing import recode_missing, reverse_code
from turning_point.validation import (git_tracked_data_files, min_cell_suppression, missingness_table,
                                      validate_frame)
from turning_point.config import PROJECT_ROOT

CODES = {-1: "refusal", -2: "dont_know", -4: "valid_skip", -5: "noninterview"}  # test codes only


def test_recode_missing_keeps_reasons():
    df = pd.DataFrame({"a": [1, -1, -4, np.nan, 3], "b": [-5, 2, 2, 2, -2]})
    clean, reasons = recode_missing(df, CODES)
    assert clean["a"].isna().sum() == 3
    assert [None if pd.isna(v) else v for v in reasons["a"]] == [None, "refusal", "valid_skip", "system_missing", None]
    tab = missingness_table(reasons).set_index("variable")
    assert tab.loc["b", "n_noninterview"] == 1 and tab.loc["b", "n_missing"] == 2


def test_reverse_code_bounds():
    assert list(reverse_code(pd.Series([1, 4]), 1, 4)) == [4, 1]
    with pytest.raises(ValueError):
        reverse_code(pd.Series([5]), 1, 4)


def test_scale_scoring_min_items_and_alpha():
    df = pd.DataFrame({"i1": [1, 2, np.nan, 4], "i2": [1, 2, np.nan, 4], "i3": [2, 2, 3, np.nan]})
    s = score_scale(df, ["i1", "i2", "i3"], min_items=2)
    assert np.isnan(s[2]) and s[3] == 4
    perfect = pd.DataFrame({"a": [1, 2, 3, 4], "b": [1, 2, 3, 4]})
    assert cronbach_alpha(perfect) == pytest.approx(1.0)


def test_unverified_construct_refused():
    c = ConstructDefinition("support", "adults", ["i1"], verified=False)
    with pytest.raises(ValueError, match="not verified"):
        score_construct(pd.DataFrame({"i1": [1]}), c)


def test_validation_flags_identifiers_ranges_duplicates():
    df = pd.DataFrame({"id": [1, 1], "home_address": ["x", "y"], "score": [2, 9]})
    rep = validate_frame(df, required=["id", "score"], id_col="id", ranges={"score": (1, 4)})
    checks = set(rep.to_frame()["check"])
    assert {"identifiers", "range", "unique_id"} <= checks and not rep.ok


def test_load_extract_mapping_and_manifest(tmp_path):
    f = tmp_path / "extract.csv"
    pd.DataFrame({"SRC1": [1, 2], "SRC2": [3, 4], "OTHER": [0, 0]}).to_csv(f, index=False)
    df, man = load_extract(f, {"id": "SRC1", "x": "SRC2"}, dataset="toy", manifest_dir=tmp_path)
    assert list(df.columns) == ["id", "x"]
    assert json.loads((tmp_path / "toy_manifest.json").read_text())["n_rows"] == 2
    with pytest.raises(ValueError, match="unverified"):
        load_extract(f, {"id": "SRC1", "x": "TODO"}, dataset="toy")


def test_registry_parsing():
    reg = {"toy": {"access": "public-use", "missing_codes": {"-4": "valid_skip"}, "weight_vars": "W1"}}
    spec = DatasetSpec.from_registry("toy", reg)
    assert spec.missing_codes == {-4: "valid_skip"} and spec.weight_vars == ["W1"]


def test_small_cell_suppression():
    out = min_cell_suppression(pd.Series([3, 50]), min_n=10)
    assert np.isnan(out[0]) and out[1] == 50


def test_repository_tracks_no_microdata():
    assert git_tracked_data_files(PROJECT_ROOT) == []


def test_project_registry_loads_all_datasets():
    for key in ("nlsy97", "hsls09", "els2002"):
        spec = DatasetSpec.from_registry(key)
        assert spec.missing_codes and all(isinstance(k, int) for k in spec.missing_codes)
    nlsy = DatasetSpec.from_registry("nlsy97")
    assert nlsy.strata_var == "VSTRAT" and nlsy.psu_var == "VPSU"
