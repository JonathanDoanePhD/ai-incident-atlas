# Decision log

Each entry: date — decision — rationale.

1. 2026-11-06 — **Use the official weekly snapshot (2026-11-02) rather than the GraphQL API.** Snapshots are the
   route the AIID research page recommends for bulk work, are versioned and checksummable, and include expert
   classifications and taxonomy definitions.
2. 2026-11-06 — **Data CC BY-SA 4.0, code MIT.** Required by the AIID license for derived data; code is our own.
3. 2026-11-06 — **Report text never committed.** The AIID terms exclude report text from the CC license; it stays in
   git-ignored `data/raw/` and the SQLite DB (also git-ignored).
4. 2026-11-06 — **No Anthropic API key is available in the run environment.** LLM extraction is run through Claude
   Code subagents that read prepared batch files and write JSON outputs, which a deterministic validator then checks.
   The pipeline also supports an API-based runner (`atlas.extract.api_runner`) for anyone reproducing with a key.
5. 2026-11-06 — **Resumption check-in scheduled hourly** (cron cannot express 75 minutes).
6. 2026-11-07 — **Scope LLM extraction to a representative prefix if usage limits recur.** The plan orders the
   pilot, then every incident with CSET/GMF expert labels (complete), then a stratified-shuffled remainder, so any
   prefix is representative and fully evaluable. Incidents not coded by the LLM receive *predicted* tags from a
   kNN model over title+description embeddings, evaluated by 5-fold cross-validation on coded incidents, labelled
   "predicted" in the app, and excluded from the evidence-based statistics on the Insights page.
7. 2026-11-07 — **Bulk extraction model: Sonnet; blind second coder: Haiku** (pilot evidence, docs/pilot_review.md).
8. 2026-11-07 — **Owner asked to complete coding of all incidents.** Extraction resumed in plan order after the
   1,001-incident interim release (which remains described in the case study) and finished all 149 batches. kNN
   propagation now covers only the one incident without reports.
9. 2026-11-07 — **Pages deploys from the default branch.** The `github-pages` environment only accepts the default
   branch (the working branch); the workflow deploys on pushes to it and to `main`.
10. 2026-11-07 — **Bundle cap:** profile source lists trimmed to the cited reports plus up to 6 others (full list on
    AIID) to keep the bundle ≈ 10 MB.
