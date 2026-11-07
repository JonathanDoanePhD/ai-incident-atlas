# PROGRESS — AI Incident Atlas

**Current phase:** 2/3 — Taxonomy v1.0 drafted; entity-kind pass + extraction pilot running
**Recurring check-in:** trigger `trig_01XDECTpPd8P61iAibcui2NV` (hourly at :17) — delete at end of run.

## Checklist
- [x] P0 Schedule recurring check-in
- [x] P0 Download official snapshot, checksum, SOURCES.md
- [x] P0 License verified (CC BY-SA 4.0 data; report text excluded)
- [x] P1 Ingestion → SQLite (data/atlas.sqlite), reports/data_profile.md, tests (5 pass)
- [x] P2 Taxonomy v1.0 + crosswalks (config/taxonomy.yaml) — revisit after pilot
- [x] P2b Entity kinds: 5934 entities via haiku (1055 private_individual hidden) → data/enrich/entity_kinds.csv (hashed keys)
- [x] P3a Pilot (20; haiku vs sonnet; 120/120 quotes grounded) → docs/pilot_review.md, prompt v1.1, taxonomy v1.1
- [ ] P3b Scaled extraction with Sonnet, 2 batches/agent, 4 concurrent. Done batches = files in data/enrich/raw/. 3 batches/agent. Dispatched so far: pilot, b000–b056 (4 batches/agent; b043/44/46/47 re-dispatched after limit) → dispatched through b064 → next: b065. Second coder complete (30). Check gaps: `python -m atlas.extract.status` (fill batches via `status fill`)
- [~] P4 evaluation module done (src/atlas/analysis/evaluation.py); blind second coding dispatched (haiku; sample in data/enrich/second_sample.json; outputs data/enrich/second/); final run after extraction
- [~] P5 modules done (embed, similarity, cluster, insights); rerun after extraction
- [~] P6 App built (Explore/Catalog/Incident/Insights/About); Playwright verify passes (node objects preserved). TODO: Pages workflow, mobile review, final data
- [ ] P7 README case study, case_study.md, CI, Makefile
- [ ] MORNING_REPORT.md, delete check-in

## Last successful command
`python -m atlas.ingest.load && python -m atlas.ingest.profile && pytest` (5 passed)

## LLM usage (approx.)
- P0: 0
- P2 entity kinds: ~4 haiku agents × ~170k tokens
- P3 pilot: 2 agents (haiku 136k, sonnet 114k tokens)
- P3b estimate: ~75 agents × ~200k ≈ 15M subagent tokens (cap 30M → then stop at representative sample)

## Blocked
- 2026-11-07 00:00–01:00 UTC: hit the 5-hour usage limit; 4 extraction agents + second coder died mid-run (partial outputs kept, nothing lost). Resumed after reset. Decision (docs/decisions.md #6): continue in priority order but cap LLM extraction near ~1,000 incidents if limits recur; uncoded incidents get kNN-*predicted* tags, clearly labelled.
- No ANTHROPIC_API_KEY → extraction via subagents (see docs/decisions.md #4).

## Next action
When pilot outputs exist: `python -m atlas.extract.validate`, review → write docs/pilot_review.md, prompt v1.1, then scale with batches from data/enrich/plan.json (`python -m atlas.extract.batches prepare <batch>`). Merge entity kinds when all 8 out files exist.
