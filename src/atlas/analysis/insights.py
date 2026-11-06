"""Descriptive analyses behind the Insights page and the README findings.

All statistics are descriptive. Significance tests are labelled **exploratory**: incidents in AIID are a
convenience sample of publicly reported events, so shifts in the mix reflect both real-world change and changes in
what gets reported and submitted.

Outputs ``data/processed/insights.json`` and ``reports/insights.md``.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from scipy import stats

from atlas import paths, taxonomy
from atlas.ingest.load import connect
from atlas.privacy import SHOWN_AS_ACTOR, entity_kind

GENAI_CUTOFF = "2022-11-30"  # public release of ChatGPT
SEV = {"s0_none": 0, "s1_minor": 1, "s2_moderate": 2, "s3_severe": 3, "s4_critical": 4}


def frame() -> tuple[pd.DataFrame, pd.DataFrame]:
    con = connect()
    inc = pd.read_sql_query(
        """SELECT i.incident_id, i.date, i.year, i.n_reports, x.severity, x.risk_domain, x.primary_failure_mode
           FROM incidents i JOIN extraction x USING (incident_id) WHERE i.is_duplicate_of IS NULL""", con)
    inc["sev"] = inc.severity.map(SEV)
    inc["era"] = np.where(inc.date >= GENAI_CUTOFF, "post", "pre")
    tags = pd.read_sql_query("SELECT incident_id, dimension, term, evidence FROM extraction_tag", con)
    return inc, tags


def share_by_year(inc, tags, dim, min_year=2014) -> dict:
    t = tags[tags.dimension == dim].merge(inc[["incident_id", "year"]])
    t = t[t.year >= min_year]
    tot = inc[inc.year >= min_year].groupby("year").size()
    piv = t.groupby(["year", "term"]).incident_id.nunique().unstack(fill_value=0)
    share = piv.div(tot, axis=0).fillna(0).round(4)
    return {"years": [int(y) for y in share.index], "n": [int(tot.get(y, 0)) for y in share.index],
            "series": {c: share[c].tolist() for c in share.columns}}


def era_shift(inc, tags, dim) -> list[dict]:
    """Share of incidents with each term before vs after the ChatGPT release; two-proportion z-test (exploratory)."""
    n_pre, n_post = (inc.era == "pre").sum(), (inc.era == "post").sum()
    t = tags[tags.dimension == dim].merge(inc[["incident_id", "era"]]).drop_duplicates(["incident_id", "term"])
    out = []
    labels = taxonomy.labels(dim) if dim != "risk_domain" else taxonomy.labels("risk_domain")
    for term, g in t.groupby("term"):
        a, b = (g.era == "pre").sum(), (g.era == "post").sum()
        p1, p2 = a / n_pre, b / n_post
        p = (a + b) / (n_pre + n_post)
        se = math.sqrt(p * (1 - p) * (1 / n_pre + 1 / n_post)) or 1e-9
        z = (p2 - p1) / se
        out.append({"term": term, "label": labels.get(term, term), "pre_share": round(p1, 4), "post_share": round(p2, 4),
                    "change_pp": round(100 * (p2 - p1), 1), "z": round(z, 2),
                    "p_exploratory": float(f"{2 * (1 - stats.norm.cdf(abs(z))):.2g}")})
    return sorted(out, key=lambda r: -abs(r["change_pp"]))


def cooccurrence_lift(inc, tags, dim_a, dim_b, min_n=10) -> list[dict]:
    a = tags[tags.dimension == dim_a][["incident_id", "term"]].drop_duplicates()
    b = tags[tags.dimension == dim_b][["incident_id", "term"]].drop_duplicates()
    n = inc.incident_id.nunique()
    m = a.merge(b, on="incident_id", suffixes=("_a", "_b"))
    ca, cb = a.term.value_counts(), b.term.value_counts()
    la, lb = taxonomy.labels(dim_a), taxonomy.labels(dim_b)
    out = []
    for (ta, tb), g in m.groupby(["term_a", "term_b"]):
        k = g.incident_id.nunique()
        if k >= min_n:
            lift = k * n / (ca[ta] * cb[tb])
            out.append({"a": ta, "a_label": la.get(ta, ta), "b": tb, "b_label": lb.get(tb, tb), "n": int(k),
                        "lift": round(lift, 2), "share_of_a": round(k / ca[ta], 3)})
    return sorted(out, key=lambda r: -r["lift"])


def cross_sector_failures(inc, tags) -> list[dict]:
    """'Same failure, different sector': failure modes ranked by how evenly they spread across sectors (entropy)."""
    f = tags[tags.dimension == "failure_mode"][["incident_id", "term"]].drop_duplicates()
    s = tags[tags.dimension == "sector"][["incident_id", "term"]].drop_duplicates()
    m = f.merge(s, on="incident_id", suffixes=("_f", "_s"))
    lf, ls = taxonomy.labels("failure_mode"), taxonomy.labels("sector")
    out = []
    for term, g in m.groupby("term_f"):
        c = g.groupby("term_s").incident_id.nunique()
        p = c / c.sum()
        h = float(-(p * np.log2(p)).sum())
        out.append({"term": term, "label": lf[term], "incidents": int(g.incident_id.nunique()), "sectors": int(len(c)),
                    "entropy_bits": round(h, 2), "normalized_entropy": round(h / math.log2(len(ls)), 2),
                    "top_sectors": [{"sector": k, "label": ls[k], "n": int(v)} for k, v in c.sort_values(ascending=False).head(4).items()]})
    return sorted(out, key=lambda r: -r["normalized_entropy"])


def recurring_actors(inc, tags, top=20) -> list[dict]:
    con = connect()
    rows = con.execute("""SELECT ie.incident_id, ie.role, e.entity_id, e.name FROM incident_entity ie
                          JOIN entities e USING (entity_id) WHERE ie.role IN ('developer','deployer')""").fetchall()
    ok = set(inc.incident_id)
    by = defaultdict(lambda: {"developer": set(), "deployer": set()})
    names = {}
    for iid, role, eid, name in rows:
        if iid in ok and entity_kind(eid, name) in SHOWN_AS_ACTOR:
            by[eid][role].add(iid)
            names[eid] = name
    fm = tags[tags.dimension == "failure_mode"].groupby("incident_id").term.apply(set).to_dict()
    sev = inc.set_index("incident_id").sev.to_dict()
    lf = taxonomy.labels("failure_mode")
    out = []
    for eid, d in by.items():
        allv = d["developer"] | d["deployer"]
        c = Counter(t for i in allv for t in fm.get(i, ()))
        sv = [sev[i] for i in allv if not pd.isna(sev.get(i))]
        out.append({"entity_id": eid, "name": names[eid], "incidents": len(allv), "as_developer": len(d["developer"]),
                    "as_deployer": len(d["deployer"]),
                    "top_failure_modes": [{"term": t, "label": lf[t], "n": n} for t, n in c.most_common(3)],
                    "mean_severity": round(float(np.mean(sv)), 2) if sv else None,
                    "years": sorted({int(y) for y in inc[inc.incident_id.isin(allv)].year})})
    return sorted(out, key=lambda r: -r["incidents"])[:top]


def severity_vs_attention(inc) -> dict:
    d = inc.dropna(subset=["sev"])
    x = np.log1p(d.n_reports.to_numpy())
    y = d.sev.to_numpy()
    rho, p = stats.spearmanr(d.n_reports, d.sev)
    slope, intercept = np.polyfit(x, y, 1)
    by = d.groupby("sev").n_reports.agg(["count", "median", "mean"]).round(2).reset_index()
    return {"spearman_rho": round(float(rho), 3), "p_exploratory": float(f"{p:.2g}"), "n": int(len(d)),
            "fit": {"x": "log(1 + reports)", "slope": round(float(slope), 3), "intercept": round(float(intercept), 3)},
            "points": [[int(a), int(b)] for a, b in zip(d.n_reports, d.sev)],
            "by_severity": by.to_dict(orient="records")}


def yearly_counts(inc) -> dict:
    c = inc[inc.year >= 2010].groupby("year").size()
    yrs = c.index.to_numpy()
    # log-linear growth fit over complete years 2014–2025
    m = (yrs >= 2014) & (yrs <= 2025)
    slope, intercept = np.polyfit(yrs[m], np.log(c.to_numpy()[m]), 1)
    return {"years": yrs.tolist(), "counts": c.tolist(), "growth_fit": {
        "years": "2014-2025", "annual_growth": round(float(math.exp(slope) - 1), 3),
        "slope": float(slope), "intercept": float(intercept)}}


def build() -> dict:
    inc, tags = frame()
    rd = inc[["incident_id", "risk_domain"]].dropna().rename(columns={"risk_domain": "term"}).assign(dimension="risk_domain")
    tags_rd = pd.concat([tags, rd.assign(evidence="coded")], ignore_index=True)
    res = {
        "n": int(len(inc)), "genai_cutoff": GENAI_CUTOFF,
        "n_pre": int((inc.era == "pre").sum()), "n_post": int((inc.era == "post").sum()),
        "yearly": yearly_counts(inc),
        "by_year": {d: share_by_year(inc, tags_rd, d) for d in ("risk_domain", "failure_mode", "technology", "harm_type")},
        "era_shift": {d: era_shift(inc, tags_rd, d) for d in ("risk_domain", "failure_mode", "technology", "harm_type")},
        "harm_x_technology": cooccurrence_lift(inc, tags, "technology", "harm_type"),
        "failure_x_technology": cooccurrence_lift(inc, tags, "technology", "failure_mode"),
        "cross_sector_failures": cross_sector_failures(inc, tags),
        "recurring_actors": recurring_actors(inc, tags),
        "severity_vs_attention": severity_vs_attention(inc),
        "severity_by_technology": severity_by(inc, tags, "technology"),
        "evidence_mix": tags.evidence.value_counts().to_dict(),
    }
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    (paths.PROCESSED / "insights.json").write_text(json.dumps(res, indent=1))
    write_markdown(res)
    return res


def severity_by(inc, tags, dim) -> list[dict]:
    t = tags[tags.dimension == dim][["incident_id", "term"]].drop_duplicates().merge(inc[["incident_id", "sev"]]).dropna()
    lab = taxonomy.labels(dim)
    g = t.groupby("term").sev.agg(["count", "mean"]).reset_index()
    g["share_s3_plus"] = t.assign(hi=t.sev >= 3).groupby("term").hi.mean().values
    return [{"term": r.term, "label": lab[r.term], "n": int(r["count"]), "mean_severity": round(float(r["mean"]), 2),
             "share_s3_plus": round(float(r.share_s3_plus), 3)} for _, r in g.sort_values("mean", ascending=False).iterrows()
            if r["count"] >= 10]


def write_markdown(r: dict) -> None:
    L = ["# Insights (descriptive)", "", "_Generated by `python -m atlas.analysis.insights`. AIID is a convenience sample of "
         "publicly reported incidents; trends mix real change with reporting and curation effects. p-values are exploratory._", "",
         f"Incidents analysed: **{r['n']}** ({r['n_pre']} before and {r['n_post']} after {r['genai_cutoff']}, the public "
         "release of ChatGPT).", "",
         f"## Growth\n\nIncidents per incident-year grew by about **{r['yearly']['growth_fit']['annual_growth']:.0%} per year** "
         "(log-linear fit, complete years 2014–2025).", ""]
    for dim in ("risk_domain", "failure_mode", "technology", "harm_type"):
        L += [f"## Shift after generative AI — {dim}", "", "| term | pre | post | change (pp) | p (exploratory) |", "|---|---:|---:|---:|---:|"]
        for x in r["era_shift"][dim][:8]:
            L.append(f"| {x['label']} | {x['pre_share']:.1%} | {x['post_share']:.1%} | {x['change_pp']:+.1f} | {x['p_exploratory']:.2g} |")
        L.append("")
    L += ["## Same failure, different sector", "", "Failure modes ranked by how evenly they spread across sectors "
          "(normalized Shannon entropy; 1 = perfectly even).", "", "| failure mode | incidents | sectors | normalized entropy | top sectors |", "|---|---:|---:|---:|---|"]
    for x in r["cross_sector_failures"]:
        L.append(f"| {x['label']} | {x['incidents']} | {x['sectors']} | {x['normalized_entropy']:.2f} | " +
                 ", ".join(f"{s['label']} ({s['n']})" for s in x["top_sectors"][:3]) + " |")
    L += ["", "## Harm × technology (highest lift, n ≥ 10)", "", "| technology | harm | n | lift |", "|---|---|---:|---:|"]
    for x in r["harm_x_technology"][:12]:
        L.append(f"| {x['a_label']} | {x['b_label']} | {x['n']} | {x['lift']:.2f} |")
    L += ["", "## Recurring developers and deployers", "", "| organization | incidents | as developer | as deployer | top failure modes | mean severity |", "|---|---:|---:|---:|---|---:|"]
    for x in r["recurring_actors"][:15]:
        L.append(f"| {x['name']} | {x['incidents']} | {x['as_developer']} | {x['as_deployer']} | " +
                 ", ".join(f"{t['label']} ({t['n']})" for t in x["top_failure_modes"]) + f" | {x['mean_severity'] if x['mean_severity'] is not None else '–'} |")
    s = r["severity_vs_attention"]
    L += ["", "## Severity ≠ media attention", "", f"Spearman ρ between number of reports and coded severity: **{s['spearman_rho']:.2f}** "
          f"(n = {s['n']}, p = {s['p_exploratory']:.2g}, exploratory). Linear fit: severity ≈ {s['fit']['intercept']:.2f} + "
          f"{s['fit']['slope']:.2f} · log(1 + reports).", "", "| severity | incidents | median reports | mean reports |", "|---:|---:|---:|---:|"]
    for x in s["by_severity"]:
        L.append(f"| {int(x['sev'])} | {int(x['count'])} | {x['median']} | {x['mean']} |")
    L += ["", "## Severity by technology (n ≥ 10)", "", "| technology | n | mean severity | share ≥ s3 |", "|---|---:|---:|---:|"]
    for x in r["severity_by_technology"]:
        L.append(f"| {x['label']} | {x['n']} | {x['mean_severity']:.2f} | {x['share_s3_plus']:.0%} |")
    (paths.REPORTS / "insights.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    out = build()
    print(json.dumps({"n": out["n"], "growth": out["yearly"]["growth_fit"]}, indent=1))
