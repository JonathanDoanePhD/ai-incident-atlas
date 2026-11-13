"""Software tests of the human-run PSID and FFCWS scripts on SYNTHETIC files (no PSID/FFCWS data involved)."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load(rel):
    spec = importlib.util.spec_from_file_location(Path(rel).stem, ROOT / rel)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_psid_script_synthetic(tmp_path):
    rng = np.random.default_rng(1); n = 2500
    by = rng.integers(1990, 1995, n)
    d = pd.DataFrame({"ER30001": rng.integers(1, 800, n), "ER30002": rng.integers(1, 200, n), "SEXV": rng.integers(1, 3, n), "BYV": by,
                      "ER16462": rng.integers(-500, 150000, n), "ER15928": rng.integers(1, 6, n), "ER34548": rng.integers(10, 18, n),
                      "CH07PRWT": rng.uniform(10, 300, n)})
    for v in ("Q23H5A", "Q23H5G", "Q23H5H", "Q33H5A", "Q33H5G", "Q33H5H"):
        d[v] = rng.choice([1, 2, 3, 4, 4, 4, 9], n)
    d.to_csv(tmp_path / "psid.csv", index=False)
    _load("scripts/psid_offline/run_psid_closeness_timing.py").main(
        ["--data", str(tmp_path / "psid.csv"), "--edu", "ER34548:2017", "--sex", "SEXV", "--birthyear", "BYV", "--out", str(tmp_path / "o")])
    E = pd.read_csv(tmp_path / "o" / "r1_estimates.csv")
    assert set(E.query("analysis == 'primary'")["adult"]) == {"mother", "teachers", "other_adults"}


def test_ffcws_script_synthetic(tmp_path):
    rng = np.random.default_rng(2); n = 3000; idn = np.arange(n)
    pd.DataFrame({"idnum": idn, "cm1bsex": rng.integers(1, 3, n), "cm1ethrace": rng.integers(1, 5, n), "cm1edu": rng.integers(1, 5, n),
                  "cm1inpov": rng.uniform(0, 5, n), "cm1relf": rng.integers(1, 4, n), "cm1age": rng.integers(16, 40, n)}).to_csv(tmp_path / "b.csv", index=False)
    pd.DataFrame({"idnum": idn, "k5a2e": rng.choice([1, 1, 2, 3, 4, -3], n)}).to_csv(tmp_path / "y9.csv", index=False)
    pd.DataFrame({"idnum": idn, "k6c17": rng.choice([1, 2, 2, 3, 4, -6], n)}).to_csv(tmp_path / "y15.csv", index=False)
    pd.DataFrame({"idnum": idn, "ck7edu": rng.choice([1, 2, 3, 4, 5, -9], n), "k7natwt": rng.uniform(2, 500, n)}).to_csv(tmp_path / "y22.csv", index=False)
    _load("scripts/ffcws_offline/run_ffcws_age9_age15.py").main(
        ["--files", *(str(tmp_path / f) for f in ("b.csv", "y9.csv", "y15.csv", "y22.csv")), "--out", str(tmp_path / "o")])
    E = pd.read_csv(tmp_path / "o" / "r2_estimates.csv")
    assert "PRIMARY any postsecondary" in set(E["analysis"])
