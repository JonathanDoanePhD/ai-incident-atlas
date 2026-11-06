# PROGRESS — AI Incident Atlas

**Current phase:** 0 — Data acquisition & licensing (done) → 1 Ingestion
**Recurring check-in:** trigger `trig_01XDECTpPd8P61iAibcui2NV` (hourly at :17) — delete at end of run.

## Checklist
- [x] P0 Schedule recurring check-in
- [x] P0 Download official snapshot, checksum, SOURCES.md
- [x] P0 License verified (CC BY-SA 4.0 data; report text excluded)
- [ ] P1 Ingestion → SQLite, data_profile.md, tests
- [ ] P2 Taxonomy + crosswalks
- [ ] P3 Pilot extraction (20) → prompt v1.1 → scaled extraction
- [ ] P4 Evaluation vs expert labels + blind second coding
- [ ] P5 Embeddings, multi-view graph, clusters, temporal
- [ ] P6 App (React/Vite/3d-force-graph), Pages workflow, Playwright checks
- [ ] P7 README case study, case_study.md, CI, Makefile
- [ ] MORNING_REPORT.md, delete check-in

## Last successful command
Snapshot downloaded and extracted to `data/raw/snapshot/`.

## LLM usage (approx.)
- P0: 0

## Blocked
- No ANTHROPIC_API_KEY → extraction via subagents (see docs/decisions.md #4).

## Next action
Write `src/atlas/ingest` loader → `data/atlas.sqlite`; profile report.
