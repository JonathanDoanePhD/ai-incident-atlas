# Data sources

## AI Incident Database (AIID) — weekly full snapshot

| Field | Value |
|---|---|
| Publisher | Responsible AI Collaborative (RAIC), https://incidentdatabase.ai |
| Access route | Official snapshot listing: https://incidentdatabase.ai/research/snapshots/ |
| File | `backup-20261102100724.tar.bz2` |
| URL | https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/backup-20261102100724.tar.bz2 |
| Snapshot timestamp | 2026-11-02 10:07:24 (UTC, from filename) |
| Downloaded | 2026-11-06 |
| Size | 120,635,874 bytes |
| SHA-256 | `9a40b34e307d119e01907689e08595510bb4e4f03cca258efb3112b0fa10b6e5` |

Contents (`mongodump_full_snapshot/`): CSV exports (`incidents.csv`, `reports.csv`, `classifications_*.csv`,
`duplicates.csv`, `submissions.csv`, `quickadd.csv`) and a MongoDB dump (`aiidprod/*.bson`), including `entities`,
`entity_relationships`, `incident_links` and `taxa` (taxonomy definitions).

Reproduce: `make data` downloads the file, verifies the checksum and extracts into `data/raw/` (git-ignored).

## License and terms (verified 2026-11-06)

- `license.txt` inside the snapshot: *"Report contents are subject to their own intellectual property rights. Unless
  otherwise noted, the database is shared under (CC BY-SA 4.0)."*
- https://incidentdatabase.ai/terms-of-use/ lists the CC BY-SA collections: `incidents`, `quickadd`, `duplicates`,
  `taxa`, `classifications`, `entities`, `entity_relationships`. It states that `submissions`, the **report `text`
  field**, and media (images/video) are **not** covered by the Creative Commons license.

### How this project complies

- **Derived data** (everything under `data/processed/` and the app's JSON bundle) is a derivative of CC BY-SA 4.0
  material and is released under **CC BY-SA 4.0**, with attribution to the AIID / RAIC. See `NOTICE` and
  `LICENSE-DATA`.
- **Code** is MIT-licensed (`LICENSE`). The split is documented in the README.
- **Report full text** is used only locally for analysis and evidence-grounding. It is never committed to the
  repository and never published in full. The public app shows only short (≤ 25 words) attributed excerpts with a
  link to the original publisher, plus our own summaries.
- Report images are not downloaded or republished.
- Private individuals named in AIID entity lists (e.g., harmed parties) are filtered out of the public bundle; see
  `docs/ethics.md`.
