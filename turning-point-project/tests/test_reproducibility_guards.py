"""Guards added after the 2026-11-13 audit."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_imputation_rng_is_seeded_explicitly():
    # statsmodels MICEData ignores np.random.seed; the seed must be passed as rng=
    for f in ("scripts/run_paper1.py", "scripts/run_b2_hsls.py", "scripts/run_p2_cya.py"):
        src = (ROOT / f).read_text()
        assert "MICEData(" in src and "rng=seed" in src, f


def test_no_preregistration_claims_in_public_text():
    for f in ("website/index.html", "website/assets/app.js", "manuscripts/working_paper_v3.src.md", "README.md"):
        t = (ROOT / f).read_text().lower()
        assert "preregistration-first" not in t and "pre-registered" not in t, f
        assert "statistically equivalent to no difference" not in t, f
