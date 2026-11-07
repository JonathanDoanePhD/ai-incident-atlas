# PROGRESS — AI Incident Atlas

**Current phase:** CONTINUATION (owner asked to code all remaining incidents). Live site deployed from `main`.
**Recurring check-in:** trigger `trig_01CL6Qhn8o7pBksehnkJEPMz` (hourly at :51) — delete when complete.
**Extraction dispatch:** 2026-11-07 06:05 UTC (after 2nd usage-limit stop): dispatched b098,b099,b100,b102 | b103,b104,b106,b107 | b108–b111 | b112–b115 + b116–b131 → next: b132 (then up to b146; plan has 149 batches = 2 pilot + b000–b146). Use `python -m atlas.extract.status` to see pending.
**Publishing:** after each pipeline rerun push to BOTH `claude/ai-incident-atlas-pi61mn` and `main` (`git push origin claude/ai-incident-atlas-pi61mn:main`) — main triggers the Pages deploy.

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
Dispatch next batches (see 'Extraction dispatch' above). When `python -m atlas.extract.status` shows 149/149: run full pipeline (validate, validate second, embed, propagate, similarity, cluster, insights, evaluation, export), app build + verify, update README/case study/MORNING_REPORT numbers, push branch + main, delete check-in.
