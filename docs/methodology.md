# Methodology

This document describes how the atlas is built, phase by phase, and the reasoning behind each design choice.
All numbers quoted elsewhere come from generated reports in `reports/`.

## 0. Data acquisition
- Official AIID weekly snapshot (`backup-20261102100724.tar.bz2`), SHA-256 verified (`data/SOURCES.md`).
- License: AIID database collections are CC BY-SA 4.0; report text is excluded from that license. Derived data is
  CC BY-SA 4.0; code is MIT. Report text never leaves the local machine except as ≤ 25-word attributed quotes.

## 1. Ingestion (`src/atlas/ingest`)
- MongoDB BSON dump → SQLite (`data/atlas.sqlite`, git-ignored because it contains report text).
- `raw_document` keeps each source document verbatim (JSON). Clean tables: `incidents`, `reports`, `entities`.
  Bridges: `incident_report`, `incident_entity(role)`, `expert_label(namespace, field, value)`. `provenance` records
  source file, snapshot checksum and load time for every table.
- Placeholders ("nan", "None", "unknown", "--", "") are normalized to NULL at load time.
- 1,284 AIID "variant" records (`is_incident_report = False`) are kept but excluded from report statistics.
- Profile: `reports/data_profile.md`.

## 2. Taxonomy (`config/taxonomy.yaml`, v1.1)
Nine dimensions keep separate constructs separate: sector (hierarchical), technology, failure mode (mechanism),
harm type, severity (0–4, the harm itself — not attention), lifecycle stage, affected population (categories
only), MIT-aligned risk domain/subdomain, and MIT-defined intent and cause. A crosswalk maps MIT, GMF and CSETv1
vocabularies onto ours for evaluation only; expert labels are never overwritten or shown to the coder.

## 3. Evidence-grounded extraction (`src/atlas/extract`, `prompts/`)
- **Plan** (`batches.py`, seed 13): 20-incident stratified pilot → all incidents with CSETv1/GMF expert labels →
  stratified-shuffled remainder; 12 incidents per batch. Stopping early leaves an evaluable, representative sample.
- **Inputs:** title, date, AIID description, visible developers/deployers, and up to 3 report excerpts
  (≤ 2,500 characters each; English, substantive, non-self-referential reports first).
- **Coder:** an LLM following `prompts/extraction_v1.1.md` (Claude Sonnet via Claude Code subagents; no API key was
  available in the build environment, so subagents read batch files and wrote JSON). The pilot compared Haiku and
  Sonnet (`docs/pilot_review.md`).
- **Validation** (`validate.py`): pydantic schema with taxonomy-aware term checks → every quote must appear verbatim
  in the cached full report text after normalization (case, Unicode quotes/dashes, punctuation, whitespace) →
  quotes may not contain private names → failures block loading until repaired: *snap* to the exact span if a
  near-verbatim match exists (rapidfuzz ≥ 92), else *downgrade* the tag to inferred. All repairs are logged in
  `data/enrich/repair_log.jsonl`; statistics in `reports/extraction_validation.md`.

## 4. Evaluation (`src/atlas/analysis/evaluation.py` → `reports/evaluation.md`)
- MIT risk domain (single label): accuracy, macro-F1, Cohen's κ, confusion matrix, majority-class baseline;
  subdomain accuracy; MIT intent/entity.
- GMF technical failure → failure mode, CSETv1 sector, GMF goal → technology (multi-label): sample-averaged
  Jaccard, any-overlap rate, micro/macro-F1, per-label precision/recall.
- Severity vs CSETv1 tangible harm and lives lost (ordinal sanity checks).
- Context: expert-vs-expert agreement among CSETv1 annotators.
- Blind second coding: 30 random incidents (seed 7) re-coded by a different model (Claude Haiku) with no access to
  the primary outputs: Jaccard per dimension, Cohen's κ, quadratic-weighted κ for severity.

## 5. Representations, connections, clusters (`src/atlas/embed`, `src/atlas/graph`)
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (384-d, normalized) of title + AIID description + our
  summaries; cached by text hash.
- Similarity views: semantic (cosine), failure / technology / sector / harm (IDF-weighted Jaccard; failure adds a
  bonus for identical primary failure mode), entity (shared named organizations), blended (weighted sum). Sparse
  symmetric top-6 graphs above per-view minimums. Each edge carries an explanation generated only from shared
  attributes, including the "one in X, one in Y" cross-sector note.
- Clusters: features = embedding ⊕ IDF-weighted one-hot tag blocks; UMAP 10-d (cosine); Ward for k = 6…24; k chosen
  by silhouette (original space) × bootstrap stability (mean ARI on 20 × 80% subsamples); seed ARI across three
  UMAP seeds reported. Labels from over-represented taxonomy terms (share ≥ 25%, lift ≥ 1.5) plus distinctive
  title words (class-based TF-IDF).
- Layout: separate 3-D UMAP, standardized, far outliers compressed logarithmically. Positions are fixed in the app.
- Bridges: betweenness centrality on the blended graph, restricted to nodes linked to ≥ 2 clusters.
- Temporal: tag shares by year; before/after the ChatGPT release (2022-11-30) with two-proportion z-tests labelled
  exploratory; severity vs report count (Spearman ρ, linear fit on log reports).

## 6. App (`app/`)
React + TypeScript + Vite, 3d-force-graph. Static JSON bundle (`app/public/data`): `nodes.json` (compact), `edges.json`
(views packed as `[source, target, weight, explanationIndex]`), lazily loaded `profiles/p{k}.json`. Filters only
restyle the graph; node objects are created once, and visibility is toggled on the cached three.js objects —
verified by `app/scripts/verify.cjs`.
