"""Multi-view incident similarity with explained edges.

Views
-----
* ``semantic``   — cosine similarity of sentence embeddings (title + description + our summaries).
* ``failure``    — IDF-weighted Jaccard over failure-mode tags (+1 bonus weight for equal primary failure mode).
* ``technology`` — IDF-weighted Jaccard over technology tags.
* ``sector``     — IDF-weighted Jaccard over sector tags.
* ``harm``       — IDF-weighted Jaccard over harm-type tags.
* ``entity``     — IDF-weighted Jaccard over named developer/deployer organizations (generic placeholders and
  private individuals excluded).
* ``blend``      — weighted sum of the above (weights in ``BLEND_WEIGHTS``).

For each view we keep a sparse, symmetric top-k graph (k = 6) above a per-view minimum, and store an
explanation string on every edge, built only from what the two incidents actually share.

"Inferred" tags count as much as "confirmed" ones here: similarity is about content, while the evidence level is
shown on the incident profile. This is documented in docs/methodology.md.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import pandas as pd

from atlas import paths, taxonomy
from atlas.embed.embed import load as load_embeddings
from atlas.ingest.load import connect
from atlas.privacy import SHOWN_AS_ACTOR, entity_kind

TOP_K = 6
VIEWS = ("semantic", "failure", "technology", "sector", "harm", "entity", "blend")
TAG_VIEWS = {"failure": "failure_mode", "technology": "technology", "sector": "sector", "harm": "harm_type"}
MIN_SIM = {"semantic": 0.45, "failure": 0.35, "technology": 0.5, "sector": 0.5, "harm": 0.35, "entity": 0.2,
           "blend": 0.3}
BLEND_WEIGHTS = {"semantic": 0.40, "failure": 0.20, "technology": 0.12, "sector": 0.08, "harm": 0.10, "entity": 0.10}


@dataclass
class Features:
    ids: np.ndarray                      # incident ids, row order
    emb: np.ndarray                      # (n, d) L2-normalized
    tags: dict[str, list[set[str]]]      # dimension -> per-row tag sets
    primary: list[str | None]
    actors: list[set[str]]               # entity ids (developer/deployer orgs)
    actor_names: dict[str, str]
    sector: list[set[str]]
    predicted: list[bool]


def load_features() -> Features:
    con = connect()
    ids, emb = load_embeddings()
    idx = {int(i): k for k, i in enumerate(ids)}
    n = len(ids)
    tags = {dim: [set() for _ in range(n)] for dim in taxonomy.TAG_DIMENSIONS}
    for iid, dim, term in con.execute("SELECT incident_id, dimension, term FROM extraction_tag"):
        if iid in idx and dim in tags:
            tags[dim][idx[iid]].add(term)
    predicted = [False] * n
    primary: list[str | None] = [None] * n
    for iid, pfm in con.execute("SELECT incident_id, primary_failure_mode FROM extraction"):
        if iid in idx:
            primary[idx[iid]] = pfm
    # Uncoded incidents: kNN-predicted tags (atlas.analysis.propagate), so every incident can be connected.
    if con.execute("SELECT name FROM sqlite_master WHERE name='predicted'").fetchone():
        for iid, payload in con.execute("SELECT incident_id, payload FROM predicted"):
            if iid in idx and not any(tags[d][idx[iid]] for d in tags):
                p = json.loads(payload)
                for dim in tags:
                    tags[dim][idx[iid]].update(p.get(dim, []))
                primary[idx[iid]] = p.get("primary_failure_mode")
                predicted[idx[iid]] = True
    actors = [set() for _ in range(n)]
    names: dict[str, str] = {}
    for iid, eid, name in con.execute(
            """SELECT ie.incident_id, e.entity_id, e.name FROM incident_entity ie JOIN entities e USING (entity_id)
               WHERE ie.role IN ('developer','deployer')"""):
        if iid in idx and entity_kind(eid, name) in SHOWN_AS_ACTOR:
            actors[idx[iid]].add(eid)
            names[eid] = name
    return Features(ids, emb, tags, primary, actors, names, tags["sector"], predicted)


def _idf(sets: list[set[str]]) -> dict[str, float]:
    df: dict[str, int] = defaultdict(int)
    for s in sets:
        for t in s:
            df[t] += 1
    n = max(len(sets), 1)
    return {t: math.log((1 + n) / (1 + c)) + 1.0 for t, c in df.items()}


def weighted_jaccard_matrix(sets: list[set[str]]) -> np.ndarray:
    """Dense IDF-weighted Jaccard: sum(idf of shared) / sum(idf of union). Rows with no tags score 0."""
    idf = _idf(sets)
    vocab = sorted(idf)
    col = {t: j for j, t in enumerate(vocab)}
    M = np.zeros((len(sets), len(vocab)), dtype=np.float32)
    for i, s in enumerate(sets):
        for t in s:
            M[i, col[t]] = idf[t]
    inter = np.zeros((len(sets), len(sets)), dtype=np.float32)
    # min(w_i, w_j) == w for binary-weighted rows sharing a term, so intersection = M @ (M>0).T
    B = (M > 0).astype(np.float32)
    inter = M @ B.T
    tot = M.sum(1)
    union = tot[:, None] + tot[None, :] - inter
    with np.errstate(divide="ignore", invalid="ignore"):
        S = np.where(union > 0, inter / union, 0.0)
    np.fill_diagonal(S, 0.0)
    return S.astype(np.float32)


def view_matrices(f: Features) -> dict[str, np.ndarray]:
    mats: dict[str, np.ndarray] = {}
    S = f.emb @ f.emb.T
    np.fill_diagonal(S, 0.0)
    mats["semantic"] = S.astype(np.float32)
    for view, dim in TAG_VIEWS.items():
        mats[view] = weighted_jaccard_matrix(f.tags[dim])
    # small bonus for an identical primary failure mode (the most central mechanism)
    pf = np.array([p or "" for p in f.primary])
    same = (pf[:, None] == pf[None, :]) & (pf[:, None] != "")
    mats["failure"] = np.clip(mats["failure"] * 0.85 + 0.15 * same, 0, 1).astype(np.float32)
    np.fill_diagonal(mats["failure"], 0.0)
    mats["entity"] = weighted_jaccard_matrix(f.actors)
    blend = sum(w * mats[v] for v, w in BLEND_WEIGHTS.items())
    mats["blend"] = blend.astype(np.float32)
    return mats


def topk_edges(S: np.ndarray, k: int, min_sim: float) -> list[tuple[int, int, float]]:
    """Symmetric union of each node's top-k neighbours above ``min_sim``."""
    n = S.shape[0]
    keep: dict[tuple[int, int], float] = {}
    kk = min(k, n - 1)
    part = np.argpartition(-S, kk, axis=1)[:, :kk]
    for i in range(n):
        for j in part[i]:
            s = float(S[i, j])
            if s >= min_sim and i != j:
                a, b = (i, int(j)) if i < j else (int(j), i)
                keep[(a, b)] = s
    return [(a, b, s) for (a, b), s in sorted(keep.items())]


def _fmt(terms: list[str], labels: dict[str, str], n: int = 2) -> str:
    names = [labels.get(t, t).split(" (")[0] for t in terms[:n]]
    names = [x[0].lower() + x[1:] if x and not x[:2].isupper() else x for x in names]
    return " and ".join(names) if len(names) <= 2 else ", ".join(names[:-1]) + " and " + names[-1]


def explain(f: Features, i: int, j: int, view: str, sim: float) -> str:
    """Human-readable reason two incidents are connected, using only shared attributes."""
    lab = {d: taxonomy.labels(d) for d in taxonomy.TAG_DIMENSIONS}
    shared = {d: sorted(f.tags[d][i] & f.tags[d][j]) for d in taxonomy.TAG_DIMENSIONS}
    parts: list[str] = []
    if view in ("failure", "blend") and shared["failure_mode"]:
        parts.append(f"same failure mode: {_fmt(shared['failure_mode'], lab['failure_mode'])}")
    if view in ("technology", "blend", "failure") and shared["technology"]:
        parts.append(f"both use {_fmt(shared['technology'], lab['technology'])}")
    if view in ("harm", "blend") and shared["harm_type"]:
        parts.append(f"shared harm: {_fmt(shared['harm_type'], lab['harm_type'])}")
    if view == "sector" and shared["sector"]:
        parts.append(f"same sector: {_fmt(shared['sector'], lab['sector'])}")
    if view in ("entity", "blend"):
        common = sorted(f.actors[i] & f.actors[j])
        if common:
            parts.append("same developer/deployer: " + ", ".join(f.actor_names[c] for c in common[:2]))
    if view == "semantic" or not parts:
        parts.insert(0, f"similar descriptions (cosine {float(f.emb[i] @ f.emb[j]):.2f})")
    # "Same failure, different sector" — the atlas's core question.
    si, sj = f.sector[i] - f.sector[j], f.sector[j] - f.sector[i]
    if view in ("failure", "blend", "technology") and si and sj and not (f.sector[i] & f.sector[j]):
        a = lab["sector"].get(sorted(si)[0], "")
        b = lab["sector"].get(sorted(sj)[0], "")
        parts.append(f"one in {a.lower()}, one in {b.lower()}")
    s = "; ".join(parts)
    if view != "semantic" and view != "entity" and (f.predicted[i] or f.predicted[j]):
        s += " (tags partly predicted)"
    return s[0].upper() + s[1:]


def build() -> dict:
    f = load_features()
    mats = view_matrices(f)
    out: dict[str, list] = {}
    stats = {}
    for view in VIEWS:
        edges = topk_edges(mats[view], TOP_K, MIN_SIM[view])
        out[view] = [{"source": int(f.ids[a]), "target": int(f.ids[b]), "weight": round(s, 4),
                      "explanation": explain(f, a, b, view, s)} for a, b, s in edges]
        deg = np.zeros(len(f.ids))
        for a, b, _ in edges:
            deg[a] += 1
            deg[b] += 1
        stats[view] = {"edges": len(edges), "isolated_nodes": int((deg == 0).sum()),
                       "mean_degree": round(float(deg.mean()), 2)}
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    (paths.PROCESSED / "edges.json").write_text(json.dumps(out))
    (paths.PROCESSED / "edges_stats.json").write_text(json.dumps(stats, indent=1))
    np.save(paths.DATA / "interim" / "blend_matrix.npy", mats["blend"])
    return stats


def related(f: Features, mats: dict[str, np.ndarray], i: int, n: int = 8) -> list[tuple[int, float, str]]:
    S = mats["blend"][i]
    order = np.argsort(-S)[:n]
    return [(int(f.ids[j]), float(S[j]), explain(f, i, int(j), "blend", float(S[j]))) for j in order if S[j] > 0]


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
    _ = pd  # pandas kept for interactive use
