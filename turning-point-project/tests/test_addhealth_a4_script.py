"""Software test of the offline Add Health A4 script on SYNTHETIC files (no Add Health data involved)."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    spec = importlib.util.spec_from_file_location("a4", ROOT / "scripts/addhealth_offline/run_addhealth_a4_continuity.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_a4_runs_on_synthetic_files(tmp_path):
    rng = np.random.default_rng(1); n = 4000
    aid = np.arange(n) + 500000
    by = rng.integers(76, 83, n)
    pd.DataFrame({"AID": aid, "BIO_SEX": rng.integers(1, 3, n), "H1GI1Y": by, "IYEAR": 95, "H1GI4": rng.integers(0, 2, n),
                  **{f"H1GI6{k}": rng.integers(0, 2, n) for k in "ABCDE"}, "PA12": rng.integers(1, 10, n),
                  "PA55": rng.integers(5, 150, n)}).to_csv(tmp_path / "w1.csv", index=False)
    mn1 = rng.integers(0, 2, n); onset = rng.integers(5, 18, n); living = (rng.random(n) > .05).astype(int)
    still = np.where(living == 1, (rng.random(n) > .2).astype(int), 7)
    iy3 = rng.integers(2001, 2003, n); age3 = iy3 - (1900 + by)
    years = np.where(still == 1, age3 - onset, rng.integers(0, 8, n))
    pd.DataFrame({"AID": aid, "IYEAR3": iy3, "H3MN1": mn1, "H3MN2": np.where(mn1 == 1, rng.integers(1, 22, n), 97),
                  "H3MN3": np.where(mn1 == 1, living, 7), "H3MN6": np.where(mn1 == 1, onset, 97),
                  "H3MN7": np.where(mn1 == 1, still, 7), "H3MN8": np.where(mn1 == 1, years, 97),
                  "H3MN11": np.where((mn1 == 1) & (living == 1), rng.integers(0, 5, n), 7)}).to_csv(tmp_path / "w3.csv", index=False)
    pd.DataFrame({"AID": aid, "H4ED2": rng.integers(1, 14, n)}).to_csv(tmp_path / "w4.csv", index=False)
    pd.DataFrame({"AID": aid, "CLUSTER2": rng.integers(1, 120, n), "GSWGT134": rng.uniform(200, 3000, n)}).to_csv(tmp_path / "wt.csv", index=False)
    _mod().main(["--w1", str(tmp_path / "w1.csv"), "--w3", str(tmp_path / "w3.csv"), "--w4", str(tmp_path / "w4.csv"),
                 "--weights", str(tmp_path / "wt.csv"), "--out", str(tmp_path / "out")])
    txt = (tmp_path / "out" / "a4_results.txt").read_text()
    assert "PRIMARY Q-A4a" in txt and "correlation of years important" in txt
    E = pd.read_csv(tmp_path / "out" / "a4_estimates.csv")
    assert "Q-A4a ended_before_18" in set(E["analysis"])
