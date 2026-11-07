"""Clusters, 3-D layout, bridge incidents and the entity network.

Feature space
-------------
Each incident is represented by the concatenation of
* its sentence embedding (384-d, L2-normalized), weight ``W_EMB``; and
* L2-normalized, IDF-weighted one-hot vectors of its failure-mode, technology, harm-type and risk-domain tags,
  each block with weight ``W_TAG``.
This keeps clusters interpretable by taxonomy terms while letting language similarity separate sub-themes.

Procedure
---------
1. UMAP to 10-d (cosine, ``n_neighbors=15``, ``min_dist=0.0``), seed 42.
2. Ward agglomerative clustering for k in ``K_RANGE``.
3. For each k: silhouette in the *original* feature space (cosine), and bootstrap stability = mean ARI between the
   full-data labels and labels from Ward refit on 80% subsamples (``N_BOOT`` resamples), restricted to the
   resampled points.
4. Choose k maximizing silhouette × stability (ties → smaller k). Report seed ARI: Ward on UMAP embeddings from
   other seeds vs the chosen solution.
5. Label each cluster by over-represented taxonomy terms (lift ≥ 1.5, support ≥ 25% within cluster).

Also computes a 3-D UMAP layout for the constellation (positions are fixed in the app, so filtering never moves
nodes), betweenness-based **bridge incidents** on the blended similarity graph, and an organization ↔ cluster
**entity network**.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict

import networkx as nx
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score, silhouette_score

from atlas import paths, taxonomy
from atlas.graph.similarity import Features, load_features

W_EMB, W_TAG = 1.0, 0.6
TAG_BLOCKS = ("failure_mode", "technology", "harm_type")
K_RANGE = range(6, 25)
N_BOOT = 20
SEED = 42


def feature_matrix(f: Features, risk_domain: list[str | None]) -> np.ndarray:
    blocks = [W_EMB * f.emb]
    sets_by_block = [f.tags[d] for d in TAG_BLOCKS] + [[{r} if r else set() for r in risk_domain]]
    for sets in sets_by_block:
        vocab = sorted(set().union(*sets))
        if not vocab:
            continue
        col = {t: j for j, t in enumerate(vocab)}
        df = Counter(t for s in sets for t in s)
        n = len(sets)
        M = np.zeros((n, len(vocab)), dtype=np.float32)
        for i, s in enumerate(sets):
            for t in s:
                M[i, col[t]] = math.log((1 + n) / (1 + df[t])) + 1
        norms = np.linalg.norm(M, axis=1, keepdims=True)
        M = np.divide(M, norms, out=np.zeros_like(M), where=norms > 0)
        blocks.append(W_TAG * M)
    return np.hstack(blocks).astype(np.float32)


def umap_embed(X: np.ndarray, dim: int, seed: int, n_neighbors: int = 15, min_dist: float = 0.0) -> np.ndarray:
    import umap

    return umap.UMAP(n_components=dim, n_neighbors=n_neighbors, min_dist=min_dist, metric="cosine",
                     random_state=seed, n_jobs=1).fit_transform(X)


def ward(Z: np.ndarray, k: int) -> np.ndarray:
    return AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Z)


def choose_k(X: np.ndarray, Z: np.ndarray) -> tuple[int, list[dict]]:
    rng = np.random.default_rng(SEED)
    n = len(Z)
    subs = [np.sort(rng.choice(n, int(0.8 * n), replace=False)) for _ in range(N_BOOT)]
    table = []
    for k in K_RANGE:
        lab = ward(Z, k)
        sil = float(silhouette_score(X, lab, metric="cosine"))
        aris = [adjusted_rand_score(lab[s], ward(Z[s], k)) for s in subs]
        stab = float(np.mean(aris))
        table.append({"k": k, "silhouette": round(sil, 4), "bootstrap_ari": round(stab, 4),
                      "bootstrap_ari_sd": round(float(np.std(aris)), 4), "score": round(max(sil, 0) * stab, 5)})
    best = max(table, key=lambda r: (r["score"], -r["k"]))
    return best["k"], table


def label_clusters(f: Features, labels: np.ndarray, risk_domain: list[str | None]) -> list[dict]:
    lab = {d: taxonomy.labels(d) for d in (*taxonomy.TAG_DIMENSIONS, "risk_domain")}
    n = len(labels)
    dims = ("failure_mode", "technology", "harm_type", "sector", "risk_domain")
    sets = {d: f.tags[d] for d in dims if d != "risk_domain"}
    sets["risk_domain"] = [{r} if r else set() for r in risk_domain]
    glob = {d: Counter(t for s in sets[d] for t in s) for d in dims}
    out = []
    for c in sorted(set(labels)):
        idx = np.where(labels == c)[0]
        terms = []
        for d in dims:
            cnt = Counter(t for i in idx for t in sets[d][i])
            for t, k in cnt.items():
                share = k / len(idx)
                lift = share / (glob[d][t] / n)
                if share >= 0.25 and lift >= 1.5:
                    terms.append({"dimension": d, "term": t, "label": lab[d].get(t, t), "share": round(share, 3),
                                  "lift": round(lift, 2)})
        terms.sort(key=lambda x: -(x["share"] * math.log(x["lift"] + 1e-9)))
        # Top terms by dimension for a readable name: technology + failure mode (+ harm if needed)
        def top(dim):
            ts = [x for x in terms if x["dimension"] == dim]
            if ts:
                return ts[0]["label"]
            cnt = Counter(t for i in idx for t in sets[dim][i])
            return lab[dim].get(cnt.most_common(1)[0][0], "") if cnt else ""
        tech, fail, harm = top("technology"), top("failure_mode"), top("harm_type")
        name = " · ".join(x.split(" (")[0] for x in (tech, fail) if x) or harm
        out.append({"cluster": int(c), "size": int(len(idx)), "name": name, "over_represented": terms[:8]})
    return out


def title_keywords(titles: list[str], labels: np.ndarray, top: int = 4) -> dict[int, list[str]]:
    """Distinctive words per cluster from AIID titles (class-based TF-IDF), used as a readable subtitle."""
    from sklearn.feature_extraction.text import CountVectorizer

    docs = [" ".join(t for t, l in zip(titles, labels) if l == c) for c in sorted(set(labels))]
    cv = CountVectorizer(stop_words="english", min_df=2, token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z-]{2,}\b",
                         ngram_range=(1, 1))
    X = cv.fit_transform(docs).toarray().astype(float)
    tf = X / X.sum(1, keepdims=True).clip(min=1)
    idf = np.log(1 + X.sum() / X.sum(0).clip(min=1))
    score = tf * idf
    vocab = np.array(cv.get_feature_names_out())
    generic = {"allegedly", "reportedly", "purported", "purportedly", "alleged", "ai", "ai-generated", "used",
               "using", "incident", "reported", "use", "uses"}
    out = {}
    for k, c in enumerate(sorted(set(labels))):
        words = [w for w in vocab[np.argsort(-score[k])] if w not in generic]
        out[int(c)] = words[:top]
    return out


def compress_outliers(xyz: np.ndarray, r0: float = 2.5) -> np.ndarray:
    """Pull far outliers in (radius > r0 σ) logarithmically so the constellation stays compact."""
    r = np.linalg.norm(xyz, axis=1, keepdims=True)
    scale = np.where(r > r0, (r0 + np.log1p(r - r0)) / np.maximum(r, 1e-9), 1.0)
    return xyz * scale


def bridges(f: Features, labels: np.ndarray, top: int = 25) -> list[dict]:
    edges = json.loads((paths.PROCESSED / "edges.json").read_text())["blend"]
    G = nx.Graph()
    G.add_nodes_from(int(i) for i in f.ids)
    for e in edges:
        G.add_edge(e["source"], e["target"], weight=e["weight"], dist=1.0 - e["weight"])
    bc = nx.betweenness_centrality(G, weight="dist", k=min(400, len(G)), seed=SEED)
    cl = {int(i): int(c) for i, c in zip(f.ids, labels)}
    out = []
    for node, b in sorted(bc.items(), key=lambda kv: -kv[1]):
        nbr_clusters = Counter(cl[m] for m in G.neighbors(node))
        other = sum(v for c, v in nbr_clusters.items() if c != cl[node])
        if other >= 2 and len(nbr_clusters) >= 2:
            out.append({"incident_id": node, "betweenness": round(b, 5), "cluster": cl[node],
                        "neighbor_clusters": dict(nbr_clusters)})
        if len(out) >= top:
            break
    return out


def entity_network(f: Features, labels: np.ndarray, min_incidents: int = 4) -> dict:
    count = Counter(e for s in f.actors for e in s)
    keep = {e for e, c in count.items() if c >= min_incidents}
    links = defaultdict(int)
    for s, c in zip(f.actors, labels):
        for e in s & keep:
            links[(e, int(c))] += 1
    return {"entities": [{"id": e, "name": f.actor_names[e], "incidents": count[e]} for e in sorted(keep, key=lambda e: -count[e])],
            "links": [{"entity": e, "cluster": c, "incidents": n} for (e, c), n in sorted(links.items())]}


def build() -> dict:
    from atlas.ingest.load import connect

    f = load_features()
    con = connect()
    rd = dict(con.execute("SELECT incident_id, risk_domain FROM extraction").fetchall())
    if con.execute("SELECT name FROM sqlite_master WHERE name='predicted'").fetchone():
        for iid, payload in con.execute("SELECT incident_id, payload FROM predicted"):
            rd.setdefault(iid, json.loads(payload).get("risk_domain"))
    risk_domain = [rd.get(int(i)) for i in f.ids]
    X = feature_matrix(f, risk_domain)
    Z = umap_embed(X, 10, SEED)
    k, table = choose_k(X, Z)
    labels = ward(Z, k)
    seed_aris = [round(adjusted_rand_score(labels, ward(umap_embed(X, 10, s), k)), 4) for s in (7, 99, 2024)]
    layout = umap_embed(X, 3, SEED, n_neighbors=20, min_dist=0.15)
    layout = compress_outliers((layout - layout.mean(0)) / layout.std(0))
    clusters = label_clusters(f, labels, risk_domain)
    titles = dict(con.execute("SELECT incident_id, title FROM incidents").fetchall())
    kw = title_keywords([titles[int(i)] or "" for i in f.ids], labels)
    for c in clusters:
        c["keywords"] = kw[c["cluster"]]
        if not c["name"]:
            c["name"] = "Titles: " + ", ".join(kw[c["cluster"]][:3])
    res = {"k": k, "selection": table, "seed_ari": seed_aris,
           "chosen": next(r for r in table if r["k"] == k),
           "params": {"w_emb": W_EMB, "w_tag": W_TAG, "tag_blocks": list(TAG_BLOCKS) + ["risk_domain"],
                      "umap": {"n_components": 10, "n_neighbors": 15, "min_dist": 0.0, "metric": "cosine"},
                      "n_boot": N_BOOT, "subsample": 0.8},
           "clusters": clusters}
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    (paths.PROCESSED / "clusters.json").write_text(json.dumps(res, indent=1))
    np.savez_compressed(paths.PROCESSED / "layout.npz", incident_ids=f.ids, labels=labels, xyz=layout.astype(np.float32))
    (paths.PROCESSED / "bridges.json").write_text(json.dumps(bridges(f, labels), indent=1))
    (paths.PROCESSED / "entity_network.json").write_text(json.dumps(entity_network(f, labels), indent=1))
    return {"k": k, "chosen": res["chosen"], "seed_ari": seed_aris}


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
