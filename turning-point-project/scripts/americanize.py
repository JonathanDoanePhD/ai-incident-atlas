"""Convert British to American spelling in project prose (case-preserving, word-boundary).

Not applied to: frozen analysis plans (hash-locked), bibliographic titles and verbatim quotes
(literature_review.md, fulltext_age_moderation.*, references.bib, citation logs), or code identifiers
such as the HTML attribute aria-labelledby.
Usage: python scripts/americanize.py FILE [FILE ...]   (evidence_matrix.csv: only summary columns)
"""
import csv
import io
import re
import sys

MAP = {
    "programme": "program", "programmes": "programs", "analysed": "analyzed", "analyse": "analyze", "analysing": "analyzing",
    "neighbourhood": "neighborhood", "neighbourhoods": "neighborhoods", "labelled": "labeled", "labelling": "labeling",
    "randomised": "randomized", "randomise": "randomize", "randomisation": "randomization", "linearisation": "linearization",
    "linearised": "linearized", "licence": "license", "organisation": "organization", "organisations": "organizations",
    "organise": "organize", "summarised": "summarized", "summarise": "summarize", "standardises": "standardizes",
    "standardisation": "standardization", "standardised": "standardized", "standardise": "standardize",
    "modelling": "modeling", "modelled": "modeled", "favourite": "favorite", "favouring": "favoring", "favoured": "favored",
    "favour": "favor", "enrolment": "enrollment", "enrol": "enroll", "emphasise": "emphasize", "colour": "color",
    "colours": "colors", "catalogued": "cataloged", "behaviour": "behavior", "behaviours": "behaviors", "towards": "toward",
    "centre": "center", "centred": "centered", "parameterisation": "parameterization", "harmonise": "harmonize",
    "harmonisation": "harmonization", "optimise": "optimize", "recognise": "recognize", "prioritise": "prioritize",
    "minimise": "minimize", "characterise": "characterize", "generalise": "generalize", "normalised": "normalized",
    "judgement": "judgment", "hypothesised": "hypothesized", "hypothesise": "hypothesize", "operationalised": "operationalized", "contextualise": "contextualize", "visualise": "visualize", "visualisation": "visualization", "whilst": "while", "amongst": "among", "ageing": "aging", "practise": "practice",
}
PAT = re.compile(r"(?<!\w)(" + "|".join(sorted(MAP, key=len, reverse=True)) + r")(?![\w-])", re.I)


def fix(text):
    def rep(m):
        w = m.group(0)
        r = MAP[w.lower()]
        return r.upper() if w.isupper() else (r[0].upper() + r[1:] if w[0].isupper() else r)
    return PAT.sub(rep, text)


for path in sys.argv[1:]:
    if path.endswith("evidence_matrix.csv"):
        rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
        for r in rows:
            for k in ("key_finding", "limitations", "design_or_method", "population"):
                r[k] = fix(r[k])
        buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
        new = buf.getvalue()
    else:
        new = fix(open(path, encoding="utf-8").read())
    old = open(path, encoding="utf-8").read()
    if new != old:
        open(path, "w", encoding="utf-8").write(new)
        print("updated", path)
