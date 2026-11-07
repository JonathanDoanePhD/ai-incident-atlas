# Morning report — AI Incident Atlas

Branch: `claude/ai-incident-atlas-pi61mn` (all work committed and pushed). Run: 2026-11-06 20:15 → 2026-11-07 ~02:30 UTC,
including a ~1-hour pause when the 5-hour usage limit was hit (no work lost).

## What was completed

| Phase | Status | Where |
|---|---|---|
| 0 Data & licensing | Official AIID snapshot 2026-11-02, SHA-256 verified; license verified: AIID data is CC BY-SA 4.0, report text excluded. Derived data CC BY-SA 4.0, code MIT. | `data/SOURCES.md`, `LICENSE*`, `NOTICE` |
| 1 Ingestion | 1,786 incidents, 8,043 report records, 7,627 entities, 22k expert labels → normalized SQLite with raw/clean/bridge/provenance tables | `src/atlas/ingest`, `reports/data_profile.md` |
| 2 Taxonomy | v1.1, 9 dimensions + crosswalks to MIT/GMF/CSETv1 (evaluation only); 5,934 entities classified, 1,055 private individuals hidden | `config/taxonomy.yaml`, `docs/ethics.md` |
| 3 Extraction | 20-incident pilot (Haiku vs Sonnet) → prompt v1.1; **1,001 of 1,783 incidents coded** (pilot, all expert-labelled, stratified sample); verbatim quote grounding | `prompts/`, `docs/pilot_review.md`, `reports/extraction_validation.md` |
| 4 Evaluation | vs MIT, GMF, CSETv1 experts; blind second coder (n = 30); hand-analysed disagreements | `reports/evaluation.md` |
| 5 Representations | embeddings, 7 similarity views with per-edge explanations, kNN propagation for 783 uncoded incidents, UMAP+Ward clusters, bridges, temporal analysis | `src/atlas/graph`, `reports/insights.md`, `reports/propagation.md` |
| 6 App | React/TS/Vite + 3d-force-graph: constellation (5 presets, color/size/connection controls, year playback, isolate cluster, explained neighbours), catalog (title-weighted search, sliders + top-3 facets, cards/table, compare), incident profiles (evidence levels, quotes, sources, related + why), insights, about. Dark theme, keyboard accessible, WebGL list fallback, 375 px responsive. | `app/`, `docs/screenshots/` |
| 7 Packaging | README case study, `docs/case_study.md` (1,424 words), methodology, decisions log, Makefile, CI + Pages workflows | root, `docs/`, `.github/workflows/` |

## Verified, with key numbers

- **Tests:** 24 pytest (ingestion, schema, quote grounding & repair, privacy, export rules) and 11 vitest (filters, search, styling) pass; `tsc` clean; production build OK.
- **Playwright** (`app/scripts/verify.cjs`, desktop 1440×900 + mobile 375×812): no console errors, no horizontal overflow on any page; **all 1,784 node objects preserved and positions unchanged across year-slider and colour changes**.
- **Grounding:** 4,763 quotes, 99.5% verbatim on first pass. 2 non-verbatim quotes caught (5 tags downgraded), 1 misattribution fixed, 17 quotes dropped because they named a private person.
- **Agreement with experts:** MIT risk domain **84.4%** (κ 0.80, n = 876, baseline 30.1%); subdomain 75.6%; CSET sector Jaccard **0.71** (CSET annotators agree with each other at 0.70); GMF technology Jaccard 0.81; GMF technical failure Jaccard 0.42 (lower-level causes; lossy crosswalk); 92% of fatal incidents coded *critical*.
- **Blind second coder (Haiku, n = 30):** risk domain κ 0.87, primary failure mode κ 0.80, severity weighted κ 0.84 (100% within one band).
- **kNN-predicted tags** (uncoded incidents): 5-fold CV risk-domain accuracy 65.3% (baseline 30.2%), labelled "predicted" in the UI and excluded from findings.
- **Clusters:** k = 18 (silhouette 0.110, bootstrap ARI 0.89, seed ARI 0.79–0.83). The selection curve is flat for k = 8–19; this is stated as a limitation. An earlier degenerate solution (k = 7, ARI 1.0 = a copy of the risk-domain label) was diagnosed and fixed.
- **Bundle:** 9.7 MB static JSON (profiles lazy-loaded); main JS 74 kB gzip, three.js lazy-loaded.

## What remains (exact next steps)

1. **Code the remaining 782 incidents** (batches b081–b148 in `data/enrich/plan.json`): `make prepare`, have an LLM code each `data/interim/batches/bNNN.json` into `data/enrich/raw/bNNN.json` with `prompts/extraction_v1.1.md`, then `make all` and re-run the Playwright check. The pipeline is resumable and idempotent; `python -m atlas.extract.status` shows gaps.
2. Optional improvements noted in the case study: merge entity aliases (Facebook/Meta) via AIID `entity_relationships`; longer excerpts for long investigations.
3. Author placeholder replaced (Jonathan Doane). `main` created from the working branch; Pages deploys from it.

## One-click actions for the owner

1. **Enable GitHub Pages:** repository *Settings → Pages → Build and deployment → Source: GitHub Actions*.
2. **Merge** `claude/ai-incident-atlas-pi61mn` into `main` (or run the "Deploy app to GitHub Pages" workflow manually via *Actions → Run workflow*). The Pages workflow deploys from `main`.
3. Make the repository public if it isn't already (it is intended to be public).

## Live demo

**Live:** https://jonathandoanephd.github.io/ai-incident-atlas/ (deployed 2026-11-07 ~01:55 UTC; verified with Playwright, no console errors).
Note: GitHub only lets the repository's *default branch* deploy to Pages. The default branch is currently
`claude/ai-incident-atlas-pi61mn`, so the workflow deploys on pushes to it and to `main`. Optional tidy-up: make
`main` the default branch (Settings → General → Default branch).

## Blockers encountered

- No `ANTHROPIC_API_KEY` in the environment → LLM coding ran through Claude Code subagents reading batch files (documented, `docs/decisions.md` #4).
- 5-hour usage limit at ~00:00 UTC stopped five agents mid-run; resumed after reset; partial outputs were kept. Scope was capped near 1,000 coded incidents as a result (`docs/decisions.md` #6).
- The hourly resumption check-in has been deleted.
