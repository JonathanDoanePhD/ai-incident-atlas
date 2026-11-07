"""Predict taxonomy tags for incidents the LLM did not code, from their nearest coded neighbours.

Why: LLM extraction covers a representative prefix of the database (see docs/decisions.md #6). To keep the
constellation complete without pretending, uncoded incidents get *predicted* tags:

* features: sentence embeddings of **title + AIID description only** (the same inputs exist for every incident,
  so cross-validation is honest — coded incidents' own summaries are NOT used here);
* model: cosine kNN (k = 15) with similarity-weighted votes. Single-label fields (risk domain, primary failure
  mode, intent, cause) take the weighted mode; multi-label fields include a term when its weighted vote share
  ≥ ``THRESH``; severity takes the weighted median;
* evaluation: 5-fold cross-validation on coded incidents → ``reports/propagation.md``.

Predicted tags are stored with evidence = "predicted", never mixed into the evidence-grounded analyses.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict

import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import KFold

from atlas import paths, taxonomy
from atlas.ingest.load import connect

K = 15
THRESH = 0.4
SINGLE = ("risk_domain", "primary_failure_mode", "intent", "cause_entity")
SEV = {"s0_none": 0, "s1_minor": 1, "s2_moderate": 2, "s3_severe": 3, "s4_critical": 4}
SEV_INV = {v: k for k, v in SEV.items()}
BASE = paths.DATA / "interim" / "embeddings_base.npz"


def base_embeddings() -> tuple[np.ndarray, np.ndarray]:
    """Embeddings of title + AIID description (identical inputs for coded and uncoded incidents)."""
    con = connect()
    rows = con.execute("SELECT incident_id, title, description FROM incidents WHERE is_duplicate_of IS NULL ORDER BY incident_id").fetchall()
    ids = np.array([r[0] for r in rows])
    if BASE.exists():
        z = np.load(BASE)
        if np.array_equal(z["ids"], ids):
            return ids, z["X"]
    from sentence_transformers import SentenceTransformer

    from atlas.embed.embed import MODEL_NAME

    m = SentenceTransformer(MODEL_NAME, device="cpu")
    X = m.encode([f"{r[1] or ''}. {r[2] or ''}" for r in rows], batch_size=64, normalize_embeddings=True,
                 show_progress_bar=False).astype(np.float32)
    BASE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(BASE, ids=ids, X=X)
    return ids, X


def load_labels() -> dict[int, dict]:
    out = {}
    for line in (paths.PROCESSED / "extractions.jsonl").read_text().splitlines():
        r = json.loads(line)
        rec = {d: {t["id"] for t in r["tags"].get(d, [])} for d in taxonomy.TAG_DIMENSIONS}
        for k in SINGLE:
            rec[k] = r.get(k)
        rec["severity"] = SEV.get((r.get("severity") or {}).get("id"))
        out[r["incident_id"]] = rec
    return out


def predict(S: np.ndarray, train: list[dict]) -> list[dict]:
    """S: (n_query, n_train) cosine similarities. Returns one prediction dict per query row."""
    preds = []
    kk = min(K, S.shape[1])
    for row in S:
        nn = np.argpartition(-row, kk - 1)[:kk]
        w = np.clip(row[nn], 0, None) + 1e-6
        p: dict = {"confidence": round(float(w.mean()), 3)}
        for d in taxonomy.TAG_DIMENSIONS:
            votes: dict[str, float] = defaultdict(float)
            for j, wj in zip(nn, w):
                for t in train[j][d]:
                    votes[t] += wj
            p[d] = sorted(t for t, v in votes.items() if v / w.sum() >= THRESH)
        for k in SINGLE:
            votes = defaultdict(float)
            for j, wj in zip(nn, w):
                if train[j][k] is not None:
                    votes[train[j][k]] += wj
            p[k] = max(votes, key=votes.get) if votes else None
        sv = [(train[j]["severity"], wj) for j, wj in zip(nn, w) if train[j]["severity"] is not None]
        if sv:
            sv.sort()
            cum, half = 0.0, sum(x[1] for x in sv) / 2
            for v, wj in sv:
                cum += wj
                if cum >= half:
                    p["severity"] = v
                    break
        else:
            p["severity"] = None
        preds.append(p)
    return preds


def cross_validate(ids: np.ndarray, X: np.ndarray, labels: dict[int, dict]) -> dict:
    coded = np.array([i for i in ids if int(i) in labels])
    idx = {int(i): k for k, i in enumerate(ids)}
    Xc = X[[idx[int(i)] for i in coded]]
    res: dict = {"n": int(len(coded)), "k": K, "threshold": THRESH, "single": {}, "multi": {}}
    y_true: dict = defaultdict(list)
    y_pred: dict = defaultdict(list)
    for tr, te in KFold(5, shuffle=True, random_state=0).split(coded):
        train = [labels[int(coded[j])] for j in tr]
        P = predict(Xc[te] @ Xc[tr].T, train)
        for j, p in zip(te, P):
            t = labels[int(coded[j])]
            for k in (*SINGLE, "severity"):
                if t[k] is not None and p[k] is not None:
                    y_true[k].append(str(t[k]))
                    y_pred[k].append(str(p[k]))
            for d in taxonomy.TAG_DIMENSIONS:
                y_true[d].append(t[d])
                y_pred[d].append(set(p[d]))
    for k in (*SINGLE, "severity"):
        maj = Counter(y_true[k]).most_common(1)[0][1] / len(y_true[k])
        out = {"accuracy": round(accuracy_score(y_true[k], y_pred[k]), 3),
               "macro_f1": round(f1_score(y_true[k], y_pred[k], average="macro", zero_division=0), 3),
               "majority_baseline": round(maj, 3)}
        if k == "severity":
            out["within_one"] = round(float(np.mean([abs(int(a) - int(b)) <= 1 for a, b in zip(y_true[k], y_pred[k])])), 3)
        res["single"][k] = out
    for d in taxonomy.TAG_DIMENSIONS:
        jac = [len(a & b) / len(a | b) if a | b else 1.0 for a, b in zip(y_true[d], y_pred[d])]
        prec = [len(a & b) / len(b) for a, b in zip(y_true[d], y_pred[d]) if b]
        res["multi"][d] = {"jaccard": round(float(np.mean(jac)), 3),
                           "precision": round(float(np.mean(prec)), 3) if prec else None,
                           "empty_prediction_share": round(float(np.mean([not b for b in y_pred[d]])), 3)}
    return res


def build() -> dict:
    ids, X = base_embeddings()
    labels = load_labels()
    cv = cross_validate(ids, X, labels)
    coded = [int(i) for i in ids if int(i) in labels]
    idx = {int(i): k for k, i in enumerate(ids)}
    unc = [int(i) for i in ids if int(i) not in labels]
    Xc = X[[idx[i] for i in coded]]
    P = predict(X[[idx[i] for i in unc]] @ Xc.T, [labels[i] for i in coded]) if unc else []
    con = connect()
    con.executescript("DROP TABLE IF EXISTS predicted; CREATE TABLE predicted (incident_id INTEGER PRIMARY KEY, payload TEXT);")
    with open(paths.PROCESSED / "predicted.jsonl", "w") as f:
        for i, p in zip(unc, P):
            p = {**p, "incident_id": i, "severity": SEV_INV.get(p["severity"]) if p["severity"] is not None else None}
            f.write(json.dumps(p) + "\n")
            con.execute("INSERT INTO predicted VALUES (?,?)", (i, json.dumps(p)))
    con.commit()
    (paths.PROCESSED / "propagation_cv.json").write_text(json.dumps(cv, indent=1))
    write_markdown(cv, len(unc))
    return {"coded": len(coded), "predicted": len(unc), "cv_risk_domain": cv["single"]["risk_domain"]}


def write_markdown(cv: dict, n_pred: int) -> None:
    L = ["# Tag propagation to uncoded incidents (kNN)", "",
         "_Generated by `python -m atlas.analysis.propagate`._", "",
         f"Incidents not coded by the LLM ({n_pred}) receive **predicted** tags from their {cv['k']} most similar coded "
         "incidents (cosine similarity of title + AIID description embeddings; similarity-weighted votes; a multi-label "
         f"term is kept when its vote share ≥ {cv['threshold']}). Predicted tags are labelled as such in the app and are "
         "excluded from the evidence-based statistics.", "",
         f"## 5-fold cross-validation on {cv['n']} coded incidents", "",
         "| field | accuracy | macro-F1 | majority baseline |", "|---|---:|---:|---:|"]
    for k, v in cv["single"].items():
        extra = f" (within one band: {v['within_one']:.0%})" if "within_one" in v else ""
        L.append(f"| {k} | {v['accuracy']:.1%}{extra} | {v['macro_f1']:.2f} | {v['majority_baseline']:.1%} |")
    L += ["", "| multi-label dimension | mean Jaccard | precision | share with no predicted tag |", "|---|---:|---:|---:|"]
    for d, v in cv["multi"].items():
        L.append(f"| {d} | {v['jaccard']:.2f} | {v['precision'] if v['precision'] is not None else '–'} | {v['empty_prediction_share']:.0%} |")
    L += ["", "Predictions are a convenience for navigation, not evidence: they are noticeably less accurate than "
          "the LLM coding evaluated in `reports/evaluation.md`."]
    (paths.REPORTS / "propagation.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
