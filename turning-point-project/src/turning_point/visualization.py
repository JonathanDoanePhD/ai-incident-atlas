"""Plotly figures with mandatory provenance labels.

Every figure function takes ``provenance``: "validated" (from a reviewed, reproducible
analysis of real data), "synthetic-test" (software testing only) or "illustrative"
(conceptual, no data). Anything other than "validated" gets a visible banner, so a
synthetic or conceptual chart cannot be mistaken for an empirical result.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

BLUE = "#1f5fa8"
ORANGE = "#e07a1f"
BANNERS = {"synthetic-test": "SYNTHETIC DATA - SOFTWARE TEST ONLY - NOT A RESEARCH FINDING",
           "illustrative": "ILLUSTRATIVE - NO DATA - NOT A RESEARCH FINDING"}


def _stamp(fig: go.Figure, provenance: str) -> go.Figure:
    if provenance not in ("validated", *BANNERS):
        raise ValueError("provenance must be 'validated', 'synthetic-test' or 'illustrative'")
    if provenance in BANNERS:
        fig.add_annotation(text=BANNERS[provenance], xref="paper", yref="paper", x=0.5, y=1.08,
                           showarrow=False, font=dict(color="#b00020", size=12))
    fig.update_layout(template="simple_white", font=dict(family="Inter, Source Sans Pro, Arial", size=14),
                      margin=dict(t=90, l=70, r=30, b=60))
    return fig


def effect_by_age_figure(effects: pd.DataFrame, *, provenance: str, ylabel: str,
                         title: str = "Association of adult support with the outcome, by age") -> go.Figure:
    """Line + uncertainty band from ``AgeModerationResult.effect_by_age``."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(effects["age"]) + list(effects["age"])[::-1],
                             y=list(effects["ci_high"]) + list(effects["ci_low"])[::-1],
                             fill="toself", fillcolor="rgba(31,95,168,0.18)", line=dict(width=0),
                             hoverinfo="skip", name="95% CI"))
    fig.add_trace(go.Scatter(x=effects["age"], y=effects["estimate"], mode="lines", line=dict(color=BLUE, width=3),
                             name="Estimate",
                             hovertemplate="Age %{x:.1f}<br>Estimate %{y:.3f}<extra></extra>"))
    fig.add_hline(y=0, line=dict(color="#666", dash="dot"))
    fig.update_layout(title=title, xaxis_title="Age at measurement of support (years)", yaxis_title=ylabel)
    return _stamp(fig, provenance)


def coverage_figure(coverage: pd.DataFrame, *, provenance: str = "validated") -> go.Figure:
    """Gantt-style dataset age coverage. Columns: dataset, age_start, age_end, label."""
    fig = go.Figure()
    for i, r in coverage.reset_index(drop=True).iterrows():
        fig.add_trace(go.Bar(y=[r["dataset"]], x=[r["age_end"] - r["age_start"]], base=[r["age_start"]],
                             orientation="h", marker_color=BLUE if i % 2 == 0 else ORANGE,
                             hovertemplate=f"{r['dataset']}: ages {r['age_start']}-{r['age_end']}<br>{r.get('label', '')}<extra></extra>",
                             showlegend=False))
    fig.update_layout(xaxis_title="Age (years)", barmode="overlay", title="Age coverage of candidate datasets")
    return _stamp(fig, provenance)
