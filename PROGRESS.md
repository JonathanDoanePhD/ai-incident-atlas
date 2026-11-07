# PROGRESS — AI Incident Atlas

**Current phase:** COMPLETE (run ended 2026-11-07). See MORNING_REPORT.md.
**Recurring check-in:** trigger `trig_01XDECTpPd8P61iAibcui2NV` — deleted at end of run.

## Checklist
- [x] P0 Official snapshot (2026-11-02) downloaded, SHA-256 verified, license verified (CC BY-SA 4.0; report text excluded)
- [x] P1 Ingestion → SQLite (`data/atlas.sqlite`, git-ignored), `reports/data_profile.md`
- [x] P2 Taxonomy v1.1 + crosswalks (MIT, GMF, CSETv1); entity kinds (5,934 entities; 1,055 private individuals hidden)
- [x] P3 Pilot (20; Haiku vs Sonnet) → prompt v1.1; scaled extraction: **1,001 / 1,783 incidents** coded (plan prefix + fill_00)
- [x] P4 Evaluation vs MIT/GMF/CSET + blind second coder (n=30) → `reports/evaluation.md` (with hand analysis)
- [x] P5 Embeddings, 7 similarity views w/ explanations, kNN propagation (783 predicted), clusters (k=18), insights
- [x] P6 App (constellation / catalog / profile / insights / about), bundle 9.7 MB, Playwright verify passes
- [x] P7 README case study, docs/case_study.md, CI + Pages workflows, Makefile, tests (24 pytest, 11 vitest)
- [x] MORNING_REPORT.md

## Last successful command
`make`-equivalent full pipeline → `node app/scripts/verify.cjs` (objectsPreserved: true, problems: [])

## LLM usage (approx., subagent tokens)
- Entity kinds: 4 × ~170k (Haiku)
- Pilot: 136k (Haiku) + 114k (Sonnet); v1.1 pilot redo 146k
- Bulk extraction: ~27 Sonnet agents × ~200–240k ≈ 6M
- Second coder: ~2 × 180k (Haiku)
- Total ≈ 7M subagent tokens (estimate was ~15M for the full corpus; scope capped at ~1,000 after a usage-limit stop)

## Blocked / notes
- 2026-11-07 00:00–01:00 UTC: 5-hour usage limit stopped 5 agents; resumed after reset, no work lost.
- GitHub Pages must be enabled by the owner (Settings → Pages → Source: GitHub Actions); deploy runs on `main`.

## Next action (if resuming)
Code remaining batches b081–b148: `python -m atlas.extract.batches prepare`, code into `data/enrich/raw/`, then `make all`.
