# PROGRESS — AI Incident Atlas

**Current phase:** 2/3 — Taxonomy v1.0 drafted; entity-kind pass + extraction pilot running
**Recurring check-in:** trigger `trig_01XDECTpPd8P61iAibcui2NV` (hourly at :17) — delete at end of run.

## Checklist
- [x] P0 Schedule recurring check-in
- [x] P0 Download official snapshot, checksum, SOURCES.md
- [x] P0 License verified (CC BY-SA 4.0 data; report text excluded)
- [x] P1 Ingestion → SQLite (data/atlas.sqlite), reports/data_profile.md, tests (5 pass)
- [x] P2 Taxonomy v1.0 + crosswalks (config/taxonomy.yaml) — revisit after pilot
- [ ] P2b Entity kinds (8 haiku batches in data/interim/entities/out_*.tsv; B,D done) → merge to data/enrich/entity_kinds.csv
- [ ] P3 Pilot extraction (20) → prompt v1.1 → scaled extraction
- [ ] P4 Evaluation vs expert labels + blind second coding
- [ ] P5 Embeddings, multi-view graph, clusters, temporal
- [ ] P6 App (React/Vite/3d-force-graph), Pages workflow, Playwright checks
- [ ] P7 README case study, case_study.md, CI, Makefile
- [ ] MORNING_REPORT.md, delete check-in

## Last successful command
`python -m atlas.ingest.load && python -m atlas.ingest.profile && pytest` (5 passed)

## LLM usage (approx.)
- P0: 0
- P2 entity kinds: ~4 haiku agents × ~170k tokens
- P3 pilot: 2 agents (haiku pilot_00, sonnet pilot_01)

## Blocked
- No ANTHROPIC_API_KEY → extraction via subagents (see docs/decisions.md #4).

## Next action
When pilot outputs exist: `python -m atlas.extract.validate`, review → write docs/pilot_review.md, prompt v1.1, then scale with batches from data/enrich/plan.json (`python -m atlas.extract.batches prepare <batch>`). Merge entity kinds when all 8 out files exist.
