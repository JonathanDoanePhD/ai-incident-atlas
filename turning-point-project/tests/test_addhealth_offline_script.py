"""Software test of the offline Add Health script on SYNTHETIC files (no Add Health data involved)."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    spec = importlib.util.spec_from_file_location("a3", ROOT / "scripts/addhealth_offline/run_addhealth_mentor_timing.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_runs_on_synthetic_files(tmp_path):
    rng = np.random.default_rng(0); n = 3000
    aid = np.arange(n) + 100000
    pd.DataFrame({"AID": aid, "BIO_SEX": rng.integers(1, 3, n), "H1GI1Y": rng.integers(76, 83, n), "IYEAR": 95,
                  "H1GI4": rng.integers(0, 2, n), **{f"H1GI6{k}": rng.integers(0, 2, n) for k in "ABCDE"},
                  "PA12": rng.integers(1, 10, n), "PA55": np.where(rng.random(n) < .2, 9996, rng.integers(5, 150, n)),
                  **{f"H1ED1{k}": rng.integers(1, 5, n) for k in "1234"}}).to_csv(tmp_path / "w1.csv", index=False)
    mn1 = rng.integers(0, 2, n)
    pd.DataFrame({"AID": aid, "H3MN1": mn1, "H3MN2": np.where(mn1 == 1, rng.integers(1, 22, n), 97),
                  "H3MN6": np.where(mn1 == 1, rng.integers(0, 24, n), 97), "H3MN8": rng.integers(1, 10, n)}).to_csv(tmp_path / "w3.csv", index=False)
    pd.DataFrame({"AID": aid, "H4ED2": rng.integers(1, 14, n)}).to_csv(tmp_path / "w4.csv", index=False)
    pd.DataFrame({"AID": aid, "CLUSTER2": rng.integers(1, 120, n), "GSWGT4_2": rng.uniform(200, 3000, n)}).to_csv(tmp_path / "wt.csv", index=False)
    m = _mod()
    m.main(["--w1", str(tmp_path / "w1.csv"), "--w3", str(tmp_path / "w3.csv"), "--w4", str(tmp_path / "w4.csv"),
            "--weights", str(tmp_path / "wt.csv"), "--out", str(tmp_path / "out")])
    E = pd.read_csv(tmp_path / "out" / "a3_estimates.csv")
    assert {"primary (ref: onset 14-17)", "S1 unweighted", "S4 cut at 12 (before 12 vs 12-17)"} <= set(E["analysis"])
    assert "GSWGT4_2" in (tmp_path / "out" / "a3_results.txt").read_text()
