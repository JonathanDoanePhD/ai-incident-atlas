"""The P3 within-family estimator recovers known coefficients on SYNTHETIC sibling data and removes family-level confounding."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
import run_p3_siblings as p3  # noqa: E402


def test_fe_recovers_within_effects_despite_family_confounding():
    rng = np.random.default_rng(3)
    fam = np.repeat(np.arange(3000), 3)
    u = rng.normal(size=3000)[fam]                      # family warmth: raises praise and the outcome
    zC = 0.8 * u + rng.normal(size=fam.size); zD = 0.8 * u + rng.normal(size=fam.size)
    x = rng.normal(size=fam.size)
    y = 0.02 * zC + 0.05 * zD + 0.03 * x + 0.3 * u + rng.normal(scale=0.3, size=fam.size)
    d = pd.DataFrame({"mid": fam, "zC": zC, "zD": zD, "x": x, "ba": y})
    f, dd, G = p3.fe_fit(d, "zC", "zD", ["x"])
    rows = {r["quantity"]: r for r in p3.contrasts(f, "zC", "zD", G - 1)}
    assert G == 3000 and len(dd) == 9000
    assert abs(rows["beta_6_9"]["estimate"] - 0.02) < 0.01 and abs(rows["beta_10_14"]["estimate"] - 0.05) < 0.01
    assert abs(rows["delta_C_minus_D"]["estimate"] + 0.03) < 0.015
    fb, _ = p3.between_fit(dd.assign(c=1.0), "zC", "zD", ["x"])
    assert fb.params["zC"] > 0.1                        # between-family estimate is confounded by u


def test_singletons_are_dropped():
    d = pd.DataFrame({"mid": [1, 1, 2, 3, 3, 3], "zC": [0.1, 0.5, 1.0, -0.2, 0.3, 0.9], "zD": [0.0, 0.2, 0.4, 0.1, -0.5, 0.2],
                      "ba": [0, 1, 1, 0, 1, 1.0]})
    _, dd, G = p3.fe_fit(d, "zC", "zD", [])
    assert G == 2 and set(dd["mid"]) == {1, 3}
