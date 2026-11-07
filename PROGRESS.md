# PROGRESS — AI Incident Atlas

**Current phase:** COMPLETE (2026-11-07). See MORNING_REPORT.md. Live: https://jonathandoanephd.github.io/ai-incident-atlas/
**Recurring check-in:** `trig_01CL6Qhn8o7pBksehnkJEPMz` — deleted at completion.

## Checklist
- [x] P0 Snapshot + license · [x] P1 Ingestion · [x] P2 Taxonomy + entity kinds
- [x] P3 Extraction: 149/149 batches, 1,783/1,783 incidents with reports (incident #141 has no report → predicted)
- [x] P4 Evaluation (experts + blind second coder) · [x] P5 Representations · [x] P6 App + Playwright
- [x] P7 Packaging · [x] Deployed (Pages) · [x] MORNING_REPORT.md

## Last successful command
Full pipeline → `node app/scripts/verify.cjs` (objectsPreserved: true, problems: []) → push to branch + main.

## LLM usage (approx., subagent tokens)
Entity kinds ~0.7M (Haiku) · pilot ~0.4M · bulk extraction ~38 Sonnet agents × ~220k ≈ 8.5M · second coder ~0.4M (Haiku).

## Next action (if resuming)
Nothing required. For a new AIID snapshot: update `paths.SNAPSHOT_*`, `make ingest plan prepare`, code new batches, `make all`.
