"""Sentence embeddings for every incident.

Text per incident = AIID title + AIID description + (our validated plain-language and technical summaries when
available). Embeddings are cached per text hash so re-runs only encode changed incidents.

Model: ``sentence-transformers/all-MiniLM-L6-v2`` (384-d, L2-normalized), pinned by revision in the output metadata.
"""

from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd

from atlas import paths
from atlas.ingest.load import connect

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
OUT = paths.PROCESSED / "embeddings.npz"
CACHE = paths.DATA / "interim" / "embedding_cache.npz"


def incident_texts() -> pd.DataFrame:
    con = connect()
    inc = pd.read_sql_query("SELECT incident_id, title, description FROM incidents WHERE is_duplicate_of IS NULL", con)
    try:
        ex = pd.read_sql_query("SELECT incident_id, summary, technical_summary FROM extraction", con)
        inc = inc.merge(ex, how="left")
    except Exception:  # extraction table not built yet
        inc["summary"] = None
        inc["technical_summary"] = None
    parts = inc[["title", "description", "summary", "technical_summary"]].fillna("")
    inc["text"] = parts.apply(lambda r: " ".join(x.strip() for x in r if x.strip()), axis=1)
    inc["hash"] = inc.text.map(lambda t: hashlib.sha1(t.encode()).hexdigest())
    return inc[["incident_id", "text", "hash"]]


def build() -> dict:
    from sentence_transformers import SentenceTransformer

    df = incident_texts()
    cache: dict[str, np.ndarray] = {}
    if CACHE.exists():
        z = np.load(CACHE)
        cache = dict(zip(z["hashes"].tolist(), z["vectors"]))
    todo = df[~df.hash.isin(cache)]
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    if len(todo):
        vecs = model.encode(todo.text.tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=False)
        cache.update(zip(todo.hash, vecs))
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(CACHE, hashes=np.array(list(cache)), vectors=np.stack(list(cache.values())))
    X = np.stack([cache[h] for h in df.hash]).astype(np.float32)
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, incident_ids=df.incident_id.to_numpy(), vectors=X)
    meta = {"model": MODEL_NAME, "dim": int(X.shape[1]), "n": int(len(df)), "normalized": True,
            "sentence_transformers": __import__("sentence_transformers").__version__,
            "encoded_this_run": int(len(todo))}
    (paths.PROCESSED / "embeddings_meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def load() -> tuple[np.ndarray, np.ndarray]:
    z = np.load(OUT)
    return z["incident_ids"], z["vectors"]


if __name__ == "__main__":
    print(build())
