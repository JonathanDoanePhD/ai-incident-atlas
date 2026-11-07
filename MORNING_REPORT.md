# Morning report — AI Incident Atlas (final)

**Status: complete.** All 1,783 incidents that have reports are coded with evidence-grounded tags; the site is live.

- **Live demo:** https://jonathandoanephd.github.io/ai-incident-atlas/
- **Branches:** `claude/ai-incident-atlas-pi61mn` (working, currently the repo default) and `main` (identical).
- **Run:** 2026-11-06 20:15 UTC → 2026-11-07, across several sessions with two usage-limit pauses (no work lost).

## What was completed

| Phase | Result | Where |
|---|---|---|
| 0 Data & licensing | Official AIID snapshot 2026-11-02, SHA-256 verified. AIID data CC BY-SA 4.0 (report text excluded) → derived data CC BY-SA 4.0, code MIT | `data/SOURCES.md`, `LICENSE*`, `NOTICE` |
| 1 Ingestion | 1,786 incidents, 8,043 report records, 7,627 entities, 22k expert labels → normalized SQLite with provenance | `src/atlas/ingest`, `reports/data_profile.md` |
| 2 Taxonomy | v1.1, 9 dimensions + crosswalks to MIT / GMF / CSETv1; 5,934 entities classified, 1,055 private individuals hidden | `config/taxonomy.yaml`, `docs/ethics.md` |
| 3 Extraction | Pilot (Haiku vs Sonnet) → prompt v1.1; **1,783 / 1,783 incidents with reports coded** (149 batches) | `prompts/`, `docs/pilot_review.md`, `reports/extraction_validation.md` |
| 4 Evaluation | vs MIT, GMF, CSET experts; blind second coder (n = 30); hand-analysed disagreements | `reports/evaluation.md` |
| 5 Representations | embeddings, 7 explained similarity views, 13 clusters, bridges, temporal analysis | `src/atlas/graph`, `reports/insights.md` |
| 6 App | constellation, catalog, incident profiles, insights, about; live on GitHub Pages | `app/`, `docs/screenshots/` |
| 7 Packaging | README case study, `docs/case_study.md` (1,492 words), methodology, decisions, Makefile, CI + Pages | root, `docs/`, `.github/` |

## Verified, with key numbers

- **Tests:** 25 pytest + 11 vitest pass; CI green; production build OK.
- **Playwright** (desktop 1440×900 and mobile 375×812): no console errors, no horizontal overflow; **all 1,784 node
  objects preserved and positions unchanged across slider and colour changes**. Live site checked in a browser.
- **Grounding:** 7,815 quotes, **99.5% verbatim on first pass**; non-verbatim quotes caught in 2 incidents, 1
  misattribution fixed, 1 snapped, 32 quotes dropped for naming a private person. Final run also caught (via the
  privacy test) and fixed a redaction miss caused by curly vs straight apostrophes.
- **Agreement with experts:** MIT risk domain **84.3%, κ 0.80** (n = 1,495; baseline 37.9%); subdomain 75.6%;
  CSET sector Jaccard **0.71** (CSET annotators agree with each other at 0.70); GMF technology Jaccard 0.81; GMF
  technical failure 0.42 (lower-level causes, lossy crosswalk); 92% of fatal incidents coded *critical*.
- **Blind second coder (n = 30):** risk domain κ 0.87, primary failure mode κ 0.80, severity weighted κ 0.84.
- **Clusters:** k = 13 (silhouette 0.121, bootstrap ARI 0.96, seed ARI 0.90–0.91).
- **Headline findings (exploratory, AIID = reported incidents):** deliberate misuse 12.5% → 54.0% of incidents
  after ChatGPT; robustness failures 44.3% → 13.5%; bias 22.9% → 2.9%; hallucination 1.4% → 12.6%; severity vs
  media attention Spearman ρ = 0.11.
- **Bundle:** 10.4 MB static JSON (initial load ≈ 3.4 MB; profiles lazy-loaded); main JS 74 kB gzip.

## What remains (optional)

- Make `main` the repository's default branch (*Settings → General → Default branch*). The Pages workflow deploys
  from either branch, so nothing breaks either way.
- Ideas listed in the case study: incremental updates from new AIID snapshots; merge entity aliases
  (Facebook/Meta); longer excerpts for long investigations.
- One incident (#141) has no linked report and keeps kNN-predicted tags.

## Blockers encountered

- No `ANTHROPIC_API_KEY` in the environment → LLM coding ran through Claude Code subagents (`docs/decisions.md` #4).
- 5-hour usage limit hit twice; work resumed after each reset from `PROGRESS.md`; no outputs lost.
- GitHub Pages only accepts deploys from the default branch; the workflow now deploys from both branches.
- The hourly resumption check-in has been deleted.
