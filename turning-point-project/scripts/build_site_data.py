"""Build website/data/site.js from the documents in docs/ so the site cannot drift from them.

Every citation key used in the site content below must exist in docs/references.bib; the build
fails otherwise (and tests/test_site.py checks it). Dataset text comes from the audit CSVs;
the only hand-entered dataset fields are approximate age ranges for the coverage chart (grade-
to-age conversions are ours and are labeled approximate on the site).
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "website" / "data" / "site.js"


def bib_keys() -> set[str]:
    return set(re.findall(r"@\w+\{([^,]+),", (DOCS / "references.bib").read_text()))


def rows(name: str) -> list[dict]:
    with open(DOCS / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def short_authors(a: str) -> str:
    names = [x.strip().split(",")[0] for x in a.split(";") if x.strip()]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} & {names[1]}"
    return f"{names[0]} et al."


def clip(s: str, n: int = 420) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


# ----------------------------------------------------------------------------- datasets
# (key in CSV 'dataset' column prefix) -> short label, approx ages, public?, verified?, role
DATASET_META = [
    ("NLSY97", "NLSY97", (12, 44), True, "Paper 1 (primary)"),
    ("HSLS:09", "HSLS:09", (14, 26), True, "Companion study (grade 9 vs 11)"),
    ("ELS:2002", "ELS:2002", (15, 26), True, "Replication option (grade 10 vs 12)"),
    ("Add Health", "Add Health", (12, 45), False, "Excluded: AI-use policy"),
    ("PSID", "PSID-CDS/TAS", (0, 39), True, "Candidate replication (needs registration)"),
    ("NLSY79 Children", "NLSY79 CYA", (0, 50), True, "Paper 2 (ages 6–9 vs 10–14)"),
    ("Future of Families", "FFCWS", (0, 22), True, "Replication (ages 9, 15, 22)"),
    ("NICHD", "SECCYD", (0, 15), False, "No adult outcome found"),
    ("ECLS-K (", "ECLS-K", (5, 14), True, "No adult outcome"),
    ("ECLS-K:2011", "ECLS-K:2011", (5, 11), True, "No adult outcome"),
    ("Millennium", "MCS (UK)", (0, 23), True, "International alternative"),
    ("Next Steps", "Next Steps (UK)", (14, 32), True, "International alternative"),
]


def build_datasets() -> list[dict]:
    out = []
    adol = rows("dataset_comparison.csv")
    early = rows("dataset_comparison_early_childhood.csv")
    for prefix, short, ages, public, role in DATASET_META:
        a = next((r for r in adol if r["dataset"].startswith(prefix)), None)
        e = next((r for r in early if r["dataset"].startswith(prefix)), None)
        if a:
            d = dict(name=a["full_name"] or a["dataset"], steward=role, population=clip(a["population"], 260),
                     n=clip(a["baseline_sample_size"], 120), waves=clip(a["measurement_waves"], 160),
                     support=clip(a["domain_supportive_adults"], 360) + " Repeated at comparable ages: " +
                     clip(a["repeated_support_at_comparable_ages"], 260),
                     outcome=clip(a["outcome_attainment"], 200), access=clip(a["access_level"] + ". " + a["access_terms"], 300),
                     limitations=clip(a["major_limitations"], 700), verified=a["verification_status"].lower().startswith("verified"),
                     doc_url=(a["documentation_urls"].split()[0] if a["documentation_urls"] else ""))
        elif e:
            d = dict(name=e["dataset"], steward=role, population=clip(e["population"], 260), n=clip(e["baseline_n"], 120),
                     waves=clip(e["waves"], 160), support=clip(e["adult_support_measures"], 360) +
                     " Repeated comparably: " + clip(e["repeated_comparable_support"], 200),
                     outcome=clip(e["adult_education_outcome"], 200), access=clip(e["access"], 300),
                     limitations=clip(e["major_limitations"], 700),
                     verified=e["verification_status"].lower().startswith("verified"),
                     doc_url=(e["documentation_url"].split()[0] if e["documentation_url"] else ""))
        else:
            raise KeyError(f"dataset {prefix!r} not found in audit CSVs")
        d.update(short=short, ages=list(ages), public=public)
        if short == "Add Health":
            d["access"] = ("Public-use and restricted files exist, but Add Health's AI and LLM Use Policy forbids processing its "
                           "data with AI tools such as Claude (public-use included). Excluded from this project's workflow.")
        out.append(d)
    return out


# ----------------------------------------------------------------------------- content
CONCEPTS = [
    dict(id="A", title="Developmental sensitivity", question="Is a stage especially responsive to the same input?",
         evidence="Variation in the age at exposure that is unrelated to the young person, e.g. age-at-move designs or trials by age."),
    dict(id="B", title="Decision significance", question="Does a transition or choice have unusually large downstream consequences?",
         evidence="Longitudinal data around transitions, with designs that handle who makes which choice."),
    dict(id="C", title="Intervention opportunity", question="Is intervening at this stage practical, reachable and cost-effective?",
         evidence="Program delivery, take-up, costs and trial effects by age. Surveys cannot answer it."),
    dict(id="D", title="Observed trajectory change", question="Did a measured trajectory actually bend?",
         evidence="Dense repeated measures of the same construct. Describes change; does not explain it."),
]

STATUS = [
    dict(title="Literature review", state="done", text="87 works verified against Crossref; full texts of 10 key works checked for age effects."),
    dict(title="Dataset audit", state="done", text="12 longitudinal studies audited from official documentation; 150 variables cataloged."),
    dict(title="Analysis plan", state="done", text="Paper 1 plan (NLSY97) frozen by a timestamped commit before the data were opened."),
    dict(title="Findings", state="prog", text="Four analyses, three cohorts, ages 6–17: no reliable sign that earlier support carries more long-run weight; duration looks more important than timing."),
]

E, H, U, X = "evidence", "hypothesis", "uncertain", "blocked"
STAGES = [
    dict(hid="H1", name="Middle childhood", ages=[8, 11],
         hypothesis="Experiences around ages 8–11 are especially important for academic confidence, relationships and early self-concept.",
         evidence=[
             dict(label=E, cite="chetty2016", text="In the Moving to Opportunity experiment, moving to a lower-poverty area before age 13 raised college attendance and earnings; moving as an adolescent did not."),
             dict(label=E, cite="chetty2018", text="Across movers, outcomes improved roughly linearly with each childhood year spent in a better area: evidence of accumulated exposure rather than one window (working-paper abstract; verify against the published article)."),
             dict(label=E, cite="cunha2007", text="Skill-formation models: skills built earlier raise the payoff of later investment (dynamic complementarity)."),
         ],
         open=[dict(label=U, text="Neighborhood exposure is not the same as a supportive adult relationship; whether the same age pattern holds for relationships is untested."),
               dict(label=X, text="Adolescent-start cohorts (NLSY97, HSLS:09, ELS:2002) cannot observe these ages.")],
         feasibility="Best public option: PSID-CDS 2002 vs 2007 identical 'how close' items, for a small overlapping subsample (paper 2)."),
    dict(hid="H2", name="Early adolescence", ages=[12, 15],
         hypothesis="Experiences around ages 12–15 are especially consequential for identity, belonging, agency and engagement.",
         evidence=[
             dict(label=U, cite="fuhrmann2015", text="A review of adolescent sensitive periods concluded that concrete evidence for them is mostly lacking."),
             dict(label=E, cite="benner2009", text="Adolescents doing well before the high-school transition showed disruptions in psychological functioning and grades across it, and many continued to struggle."),
             dict(label=E, cite="yeager2019", text="A brief online growth-mindset intervention improved grades among lower-achieving students in a national experiment (grade of delivery to be confirmed from the full text)."),
             dict(label=E, cite="yeager2018", text="Interventions that work for children often fail with middle adolescents unless they fit adolescents' need for status and respect."),
         ],
         open=[dict(label=U, text="No study compares the same supportive relationship begun in grade 9 with the same relationship begun at another age."),
               dict(label=U, text="Paper 1 found no clear difference between ages 12 and 16 in the association of parental support with attainment. See Findings.")],
         feasibility="NLSY97 round 1 covers ages 12–16 with one identically worded parental-support item."),
    dict(hid="H3", name="Late adolescence", ages=[16, 18],
         hypothesis="Experiences around ages 16–18 are especially consequential for persistence, career decisions and postsecondary pathways.",
         evidence=[
             dict(label=E, cite="roorda2011", text="In a meta-analysis, associations of teacher–student relationships with engagement and achievement were stronger in higher grades overall, though negative relationships mattered more in primary school (correlational)."),
             dict(label=E, cite="fruiht2013", text="In Add Health, mentors who became important after high school were associated with the most attainment; teacher mentors were the strongest predictors (retrospective, observational)."),
             dict(label=E, cite="heller2017", text="Becoming a Man, a school-based program for adolescent boys, raised graduation rates in a randomized trial; the authors found no positive evidence that a generic mentoring effect explained it."),
         ],
         open=[dict(label=U, text="Associations closer in time to the outcome may be larger for reasons unrelated to sensitivity (proximity, selection).")],
         feasibility="NLSY97 (to age 16 at round 1), HSLS:09 grade 11 and ELS:2002 grade 12 observe these ages."),
    dict(hid="H4", name="Emerging adulthood", ages=[18, 24],
         hypothesis="Experiences around ages 18–24 can substantially alter trajectories through education, work and independence.",
         evidence=[dict(label=E, cite="fruiht2013", text="The same Add Health study found post-high-school mentors associated with the highest attainment."),
                   dict(label=E, cite="cunha2010", text="For noncognitive skills, later investment can substitute for earlier investment more readily than for cognitive skills.")],
         open=[dict(label=X, text="No audited public dataset this project may analyze repeats a measure of adult support through ages 18–24.")],
         feasibility="NLSY97 and TAS observe these ages, but comparable support measures are sparse."),
    dict(hid="H6/H7", name="Duration and transitions", ages=[12, 18],
         hypothesis="Consistency and duration of support (H6), and support around institutional transitions (H7), may matter more than chronological age.",
         evidence=[dict(label=E, cite="grossman2002", text="In a mentoring trial, matches lasting a year or more showed the most benefit, and early terminations were associated with declines."),
                   dict(label=E, cite="neild2008", text="Ninth-grade outcomes add to the prediction of dropout beyond earlier characteristics (predictive, not causal)."),
                   dict(label=E, cite="mishra2009", text="The life-course structured approach compares critical-period, sensitive-period and accumulation models against a saturated model.")],
         open=[dict(label=U, cite="smith2015", text="These model comparisons lose power when exposures at different ages are highly correlated, as support usually is."),
               dict(label=U, text="Our HSLS:09 study found grade-9 math-teacher support no more predictive of a BA than grade-11 support (difference within ±3 points). See Findings.")],
         feasibility="NLSY79 CYA (biennial HOME items) and NLSY97 1997–2000 repeated items allow accumulation models."),
]

FRAMEWORK = {
    "nodes": [
        dict(id="ses", label="Structural\nconditions", x=20, y=30, domain="Domain 8", paperRole="Confounder (adjusted)",
             description="Income, neighborhood poverty, school resources and discrimination shape both access to supportive adults and educational opportunity.",
             constructs=["household income-to-poverty ratio", "neighborhood poverty", "school resources", "discrimination"]),
        dict(id="fam", label="Family\nenvironment", x=20, y=150, domain="Domain 3", paperRole="Confounder (adjusted) and moderator (exploratory)",
             description="Household structure, stability and economic hardship are treated as contexts, not deficits.",
             constructs=["household structure", "economic hardship", "family stability", "caregiver involvement"]),
        dict(id="prior", label="Prior achievement\n& engagement", x=20, y=270, domain="Domains 4 & 6", paperRole="Confounder; weakly measured at NLSY97 baseline",
             description="More engaged or higher-achieving young people may attract and keep supportive adults (reverse causation).",
             constructs=["prior grades/test scores", "attendance", "health"], caution="The main unresolved confounder in paper 1; handled by sensitivity analyses."),
        dict(id="u", label="Unmeasured traits\n(temperament etc.)", x=20, y=380, domain="Not measured", paperRole="Unmeasured confounder",
             description="Sociability, temperament and motivation can influence both support and outcomes. E-values quantify how strong such confounding would need to be.",
             constructs=["temperament", "sociability", "motivation"]),
        dict(id="support", label="Adult support\nat age a", x=285, y=150, role="exposure", domain="Domain 2", paperRole="Exposure (parental support in paper 1)",
             description="Who provides support, how much, when it starts and how long it lasts are distinct dimensions. Paper 1 can study only parental support at one time point.",
             constructs=["parent supportiveness", "teacher connectedness", "natural mentors", "counsellor contact"]),
        dict(id="age", label="Age / stage\nat measurement", x=285, y=30, domain="Timing", paperRole="Moderator",
             description="In one cohort, age at report is entangled with birth year, grade and calendar period.",
             constructs=["age", "grade", "school transition"], caution="Age differences in association are not evidence of developmental sensitivity on their own."),
        dict(id="identity", label="Identity\n& agency", x=285, y=290, domain="Domain 1", paperRole="Mediator (not adjusted in total-effect models)",
             description="Self-efficacy, expectations and future orientation may carry part of support's association with attainment.",
             constructs=["self-efficacy", "educational expectations", "locus of control", "future orientation"]),
        dict(id="engage", label="Later engagement\n& course-taking", x=285, y=380, domain="Domains 4 & 7", paperRole="Mediator",
             description="Belonging, persistence, course selection and postsecondary planning after the support measure.",
             constructs=["school belonging", "persistence", "course selection", "postsecondary planning"]),
        dict(id="y", label="Educational\nattainment", x=550, y=200, role="outcome", domain="Outcome", paperRole="Primary outcome (highest grade completed)",
             description="Measured around age 40 in NLSY97. Secondary outcomes: BA attainment, employment, earnings, well-being.",
             constructs=["highest grade completed", "degree attained", "employment", "earnings"]),
    ],
    "edges": [
        *[dict(**{"from": f, "to": "support"}, kind="confound") for f in ("ses", "fam", "prior", "u")],
        *[dict(**{"from": f, "to": "y"}, kind="confound") for f in ("ses", "fam", "prior", "u")],
        dict(**{"from": "age", "to": "support"}, kind="causal"),
        dict(**{"from": "support", "to": "y"}, kind="causal"),
        dict(**{"from": "support", "to": "identity"}, kind="causal"),
        dict(**{"from": "support", "to": "engage"}, kind="causal"),
        dict(**{"from": "identity", "to": "y"}, kind="causal"),
        dict(**{"from": "engage", "to": "y"}, kind="causal"),
    ],
}

METHODS = [
    dict(title="Survey-weighted models", text="Design-based variance by Taylor linearization (NLSY97 strata and PSUs) or replicate weights (HSLS:09), validated against reference estimators and by simulation."),
    dict(title="Timing model", text="Support × age interaction; the age-16 vs age-12 contrast is tested for difference and for equivalence against a smallest effect size of interest."),
    dict(title="Missing data", text="Survey missing codes are kept by reason; multiple imputation (m = 40) pooled by Rubin's rules; complete-case sensitivity analysis."),
    dict(title="Multiplicity", text="One primary and one secondary confirmatory test (Holm). Everything else is labeled exploratory."),
    dict(title="Sensitivity", text="Age as categories, selection into co-residence, grade adjustment, alternative exposure codings, E-values for unmeasured confounding."),
    dict(title="Ethics", text="De-identified secondary data only; no microdata in the repository; small-cell suppression; no individual-level prediction or labeling."),
]

FINDINGS_STEPS = [
    dict(title="Plan frozen", state="done", text="File hashes committed before respondent-level data were opened."),
    dict(title="Extract validated", state="done", text="24 variables; counts match the official codebook exactly."),
    dict(title="Primary analysis", state="done", text="40 imputations, design-based variance, independent jackknife check."),
    dict(title="Paper 2", state="done", text="Ages 6–9 vs 10–14 with NLSY79 Children and Young Adults (mother-reported praise and closeness)."),
    dict(title="Accumulation", state="done", text="NLSY97 four-year support histories: duration fits as well as timing."),
    dict(title="Next: replication", state="todo", text="PSID child supplement (needs free registration) and Add Health by a human analyst, if desired."),
    dict(title="Grade 9 vs 11", state="done", text="HSLS:09 companion study run from its own frozen plan."),
    dict(title="Working paper", state="done", text="Version 2 brings all four analyses together (see Publications)."),
]

PUBLICATIONS = [
    dict(title="Statistical analysis plan (paper 1)", text="Design, variables, model, missing data, SESOI, multiplicity and sensitivity analyses.", status="Draft v0.2", statusKind="hypothesis", link="../docs/statistical_analysis_plan.md", linkText="Read the plan"),
    dict(title="Frozen analysis plan record", text="Plan frozen by a timestamped commit with file hashes (not registered on OSF).", status="Frozen", statusKind="evidence", link="../docs/PLAN_FREEZE.md", linkText="See the freeze record"),
    dict(title="Full-text check: age in mentoring meta-analyses", text="Ten open full texts read; no meta-analysis found significant age moderation.", status="v1", statusKind="evidence", link="../docs/fulltext_age_moderation.md", linkText="Read the check"),
    dict(title="Literature review and evidence matrix", text="Abstract-level critical review of 87 verified works on turning points, mentoring, transitions and timing.", status="v0.1", statusKind="evidence", link="../docs/literature_review.md", linkText="Read the review"),
    dict(title="Dataset feasibility audits", text="Adolescent-start and early-childhood cohorts compared on age coverage, measures, design and access.", status="v0.1", statusKind="evidence", link="../docs/dataset_audit.md", linkText="Read the audit"),
    dict(title="Results report (grade 9 vs 11)", text="HSLS:09 math-teacher support in grade 9 vs grade 11 and bachelor's attainment.", status="v1", statusKind="evidence", link="../docs/results_b2_hsls.md", linkText="Read the results"),
    dict(title="Results report (paper 1)", text="Primary estimates, sensitivity analyses, verification and deviations from the plan.", status="v1", statusKind="evidence", link="../docs/results_paper1.md", linkText="Read the results"),
    dict(title="Working paper v2: evidence from three U.S. cohorts", text="All four analyses (NLSY97, HSLS:09, NLSY79 Children and Young Adults, accumulation). Not peer reviewed.", status="v2", statusKind="evidence", link="../manuscripts/working_paper_v2.md", linkText="Read the paper"),
    dict(title="Results report (paper 2)", text="Maternal praise and closeness at ages 6–9 vs 10–14 and bachelor's attainment.", status="v1", statusKind="evidence", link="../docs/results_p2_cya.md", linkText="Read the results"),
    dict(title="Conference presentation", text="Planned after the working paper.", status="Not started", statusKind="uncertain"),
]

RECOMMENDATION = ("<strong>Design choice for paper 1:</strong> NLSY97 asks the same parental-support question of youths aged 12–16 "
                  "in the same year and follows attainment to about age 40. It cannot study nonparental mentors. HSLS:09 supports a "
                  "grade-9 vs grade-11 companion study, and PSID-CDS/TAS is the best public option for comparing ages 8–11 with 12–15. "
                  "Add Health is excluded because its terms forbid AI-assisted processing. Ages on the chart are approximate; "
                  "grade-to-age conversions are ours.")


NODE_PATTERNS = {
    "support": r"support|close|teacher|mentor|counsel|warm|adult",
    "identity": r"expect|aspir|efficacy|control|mastery|self",
    "engage": r"engag|belong|course|enroll",
    "fam": r"famil|household|structure|parent ed",
    "ses": r"income|pover|ses|neighbo",
    "prior": r"achiev|test score|assessment|prior",
    "y": r"attain|degree|completion|employ|earn|wage",
    "age": r"^age",
}


def measured_in() -> dict[str, list[str]]:
    """Datasets with at least one audited variable whose construct matches each framework node."""
    out: dict[str, set[str]] = {k: set() for k in NODE_PATTERNS}
    for f in ("variable_dictionary_adolescent.csv", "variable_dictionary_early_childhood.csv"):
        for r in rows(f):
            if r["verification_status"].lower().startswith("unverified"):
                continue
            c = r["construct"].lower()
            for node, pat in NODE_PATTERNS.items():
                if re.search(pat, c):
                    name = r["dataset"] + (" (docs only)" if r["dataset"].startswith("Add Health") else "")
                    out[node].add(name)
    return {k: sorted(v) for k, v in out.items()}


def build() -> dict:
    keys = bib_keys()
    m_in = measured_in()
    for n in FRAMEWORK["nodes"]:
        n["measuredIn"] = m_in.get(n["id"], [])
    ev_rows = rows("evidence_matrix.csv")
    evidence = [dict(citation_key=r["citation_key"], authors_short=short_authors(r["authors"]), year=r["year"], title=r["title"],
                     journal=r["journal"], doi=r["doi"], study_type=r["study_type"], population=clip(r["population"], 160),
                     design_or_method=clip(r["design_or_method"], 160), key_finding=clip(r["key_finding"], 420),
                     age_or_timing_relevant=r["age_or_timing_relevant"], limitations=clip(r["limitations"], 200),
                     evidence_level_read=r["evidence_level_read"]) for r in ev_rows]
    year_of = {r["citation_key"]: (short_authors(r["authors"]), r["year"]) for r in ev_rows}
    missing = []
    for s in STAGES:
        for item in s["evidence"] + s["open"]:
            k = item.get("cite")
            if k:
                if k not in keys or k not in year_of:
                    missing.append(k)
                else:
                    item["cite"] = f"{year_of[k][0]}, {year_of[k][1]}"
    if missing:
        raise SystemExit(f"Site cites keys missing from references.bib/evidence_matrix: {sorted(set(missing))}")
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        commit = ""
    return dict(concepts=CONCEPTS, status=STATUS, stages=STAGES, datasets=build_datasets(), framework=FRAMEWORK,
                evidence=evidence, methods=METHODS, findingsSteps=FINDINGS_STEPS, publications=PUBLICATIONS,
                recommendation=RECOMMENDATION, build=dict(date=date.today().isoformat(), commit=commit))


def main() -> None:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("/* generated by scripts/build_site_data.py - do not edit */\nwindow.SITE_DATA = " +
                   json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(data['evidence'])} works, {len(data['datasets'])} datasets")


if __name__ == "__main__":
    main()
