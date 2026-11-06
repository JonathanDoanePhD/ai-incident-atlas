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
