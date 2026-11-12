import pandas as pd
import pytest

from turning_point.visualization import coverage_figure, effect_by_age_figure


def test_non_validated_figures_are_bannered():
    eff = pd.DataFrame({"age": [12, 13], "estimate": [0.1, 0.2], "ci_low": [0, 0.1], "ci_high": [0.2, 0.3]})
    fig = effect_by_age_figure(eff, provenance="synthetic-test", ylabel="y")
    assert any("SYNTHETIC" in a.text for a in fig.layout.annotations)
    with pytest.raises(ValueError):
        effect_by_age_figure(eff, provenance="looks-real", ylabel="y")


def test_coverage_figure_builds():
    cov = pd.DataFrame({"dataset": ["A"], "age_start": [12], "age_end": [40]})
    assert len(coverage_figure(cov).data) == 1
