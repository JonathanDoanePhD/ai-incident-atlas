# Pilot review — extraction prompt v1 → v1.1, taxonomy v1.0 → v1.1

**Pilot design.** 20 incidents, stratified round-robin over 7 incident-year bins (≤2016 … 2026) × 3 report-count
bins (1, 2–4, 5+), with MIT risk domains spread evenly (`atlas.extract.batches.plan`, seed 13). Ten were coded by a
small model (Claude Haiku) and ten by a mid-size model (Claude Sonnet) with the same prompt, so the pilot also
informs model choice. Raw v1 outputs are kept in `data/enrich/pilot_v1/`.

## What worked
- **Grounding:** 120/120 quotes (60 per model) matched the cached report text verbatim on the first pass, after
  whitespace/punctuation normalization; no repairs were needed.
- **Evidence levels used sensibly:** ~70% confirmed / 30% inferred. Both models used `inferred` when the excerpt did
  not state a fact (e.g. incident 85, whose only linked "report" is an AIID index page).
- **Privacy:** no private names appeared in summaries. The Haiku coder noticed a private plaintiff listed as a
  deployer in AIID and replaced them with the company. One false-positive redaction surfaced a bug in our
  private-name matcher (a group-shaped entity name triggered surname matching on "Housing"); fixed with a
  personal-name-shape test and a regression test.

## What changed and why
| Issue observed | Example | Change |
|---|---|---|
| Mapping our *primary failure mode* (a mechanism) to MIT *risk domain* is lossy | #388 facial recognition misidentifying Black and poor residents: mechanism = robustness, MIT = Discrimination; #815: opacity vs MIT Discrimination | Added `risk_domain`/`risk_subdomain` dimensions aligned with the MIT Domain Taxonomy, coded directly (expert labels never shown to the coder). The failure-mode crosswalk is kept as a secondary analysis. |
| Our `intent` meant "malicious", MIT's means "expected outcome of pursuing a goal" | #203 Uber pay algorithm: we said unintentional, MIT says Intentional | Adopted MIT definitions for `intent` and `cause_entity`; `unclear` → `other`. |
| `other_unspecified` technology overused | #203 pay algorithm, #1546 earthquake early-warning | Guidance: pricing/pay/optimization → `ad_targeting_pricing`; forecasting/detection → `predictive_scoring`. |
| Sector for internal corporate tools | #1471 Meta internal agent coded `social_media` | Guidance: internal tools → `employment`. |
| AIID self-reference pages chosen as excerpts | #85 | Batch preparer ranks incidentdatabase.ai/github.com sources last. |
| Harm/severity consistency | — | Rule: `no_harm_near_miss` ⇔ `s0_none`. |

## Model choice for bulk extraction
| | Haiku (pilot_00) | Sonnet (pilot_01) |
|---|---|---|
| Records valid / quotes grounded | 10/10, 60/60 | 10/10, 60/60 |
| Tags per incident | 8.3 | 7.9 |
| Wall time / tokens (incl. agent overhead) | 202 s / 136k | 130 s / 114k |
| Qualitative | correct but terser technical summaries | richer mechanisms, careful ambiguity notes |

Sonnet was both faster and cheaper per batch in this environment, with better qualitative coding, so it is used
for bulk extraction. Haiku is used as the independent **blind second coder** in Phase 4 (a different model, as
required).

## Cost control for scale-up
Each agent reads the prompt once and processes two 12-incident batches with one Read and one Write per batch.
Batches run in priority order (pilot → incidents with CSETv1/GMF expert labels → stratified remainder), so stopping
early still leaves a representative, evaluable sample.
