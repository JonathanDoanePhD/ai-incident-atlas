"""Central filesystem locations. Everything is relative to the repository root."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
SNAPSHOT_FILE = RAW / "backup-20261102100724.tar.bz2"
SNAPSHOT_URL = "https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/backup-20261102100724.tar.bz2"
SNAPSHOT_SHA256 = "9a40b34e307d119e01907689e08595510bb4e4f03cca258efb3112b0fa10b6e5"
SNAPSHOT_DIR = RAW / "snapshot" / "mongodump_full_snapshot"
PROCESSED = DATA / "processed"
ENRICH = DATA / "enrich"
DB_PATH = DATA / "atlas.sqlite"
CONFIG = ROOT / "config"
PROMPTS = ROOT / "prompts"
REPORTS = ROOT / "reports"
APP_DATA = ROOT / "app" / "public" / "data"
