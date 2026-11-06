"""Phase 4 — evaluate extracted labels against AIID expert taxonomies and a blind second coder.

Comparisons (all on incidents carrying both our extraction and the expert label):

1. ``risk_domain`` vs MIT Risk Domain (single-label, 7 classes): accuracy, macro-F1, Cohen's κ, confusion matrix;
   plus subdomain accuracy and MIT Intent / Entity.
2. ``failure_mode`` vs GMF *Known AI Technical Failure*, crosswalked to our terms (multi-label).
3. ``sector`` vs CSETv1 *Sector of Deployment*, compared at the CSET-bucket level (multi-label).
4. ``technology`` vs GMF *Known AI Goal*, crosswalked (multi-label; only mapped goals).
5. ``severity`` vs CSETv1 *Tangible Harm* and *Lives Lost* (ordinal sanity checks).
6. Expert-vs-expert baseline: agreement between CSETv1 annotators on the same fields, for context.
7. Blind second coding (different model, no access to primary outputs): Jaccard per multi-label dimension, Cohen's
   κ for nominal fields, quadratic-weighted κ for severity.

Multi-label metrics: sample-averaged Jaccard, micro and macro F1 over the label space present in the expert data.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix, f1_score
from sklearn.preprocessing import MultiLabelBinarizer

from atlas import paths, taxonomy
from atlas.ingest.load import connect

SEV_RANK = {"s0_none": 0, "s1_minor": 1, "s2_moderate": 2, "s3_severe": 3, "s4_critical": 4}


# ----------------------------------------------------------------------------------------------- loading
def load_ours(source: str = "primary") -> dict[int, dict]:
    suffix = "" if source == "primary" else f"_{source}"
    path = paths.PROCESSED / f"extractions{suffix}.jsonl"
    if not path.exists():
        return {}
    return {r["incident_id"]: r for r in map(json.loads, path.read_text().splitlines())}


def tagset(rec: dict, dim: str) -> set[str]:
    return {t["id"] for t in rec["tags"].get(dim, [])}


def expert(con, ns: str, field: str) -> dict[int, list[str]]:
    out: dict[int, list[str]] = defaultdict(list)
    for iid, v in con.execute("SELECT incident_id, value FROM expert_label WHERE namespace=? AND field=?", (ns, field)):
        out[iid].append(v)
    return dict(out)


# ----------------------------------------------------------------------------------------------- metrics
def multilabel_scores(pairs: list[tuple[set[str], set[str]]], labels: list[str] | None = None) -> dict[str, Any]:
    """pairs = [(expert_set, ours_set)]; returns Jaccard, micro/macro F1, per-label P/R/F1/support."""
    if not pairs:
        return {"n": 0}
    exp, ours = zip(*pairs)
    labels = labels or sorted(set().union(*exp))
    mlb = MultiLabelBinarizer(classes=labels)
    Y = mlb.fit_transform([e & set(labels) for e in exp])
    P = mlb.transform([o & set(labels) for o in ours])
    jac = [len(e & o) / len(e | o) if (e | o) else 1.0 for e, o in zip(exp, ours)]
    per = {}
    for k, lab in enumerate(labels):
        tp = int(((Y[:, k] == 1) & (P[:, k] == 1)).sum())
        fp = int(((Y[:, k] == 0) & (P[:, k] == 1)).sum())
        fn = int(((Y[:, k] == 1) & (P[:, k] == 0)).sum())
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        per[lab] = {"precision": round(p, 3), "recall": round(r, 3),
                    "f1": round(2 * p * r / (p + r), 3) if p + r else 0.0, "support": int(Y[:, k].sum())}
    any_hit = np.mean([bool(e & o) for e, o in zip(exp, ours)])
    return {"n": len(pairs), "jaccard": round(float(np.mean(jac)), 3), "any_overlap": round(float(any_hit), 3),
            "micro_f1": round(float(f1_score(Y, P, average="micro", zero_division=0)), 3),
            "macro_f1": round(float(f1_score(Y, P, average="macro", zero_division=0)), 3),
            "per_label": per}


def single_label_scores(y_true: list[str], y_pred: list[str], labels: list[str]) -> dict[str, Any]:
    if not y_true:
        return {"n": 0}
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return {"n": len(y_true), "accuracy": round(accuracy_score(y_true, y_pred), 3),
            "macro_f1": round(float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)), 3),
            "kappa": round(float(cohen_kappa_score(y_true, y_pred, labels=labels)), 3),
            "labels": labels, "confusion": cm.tolist(),
            "majority_baseline": round(Counter(y_true).most_common(1)[0][1] / len(y_true), 3)}


# ----------------------------------------------------------------------------------------------- comparisons
def eval_mit(con, ours: dict[int, dict]) -> dict[str, Any]:
    dom_lab = {t["id"]: t["mit"] for t in taxonomy.load()["dimensions"]["risk_domain"]["terms"]}
    mit = expert(con, "MIT", "Risk Domain")
    sub = expert(con, "MIT", "Risk Subdomain")
    labels = sorted(set(dom_lab.values()))
    yt, yp, examples = [], [], []
    for iid, rec in ours.items():
        if iid in mit and rec.get("risk_domain"):
            t, p = mit[iid][0], dom_lab[rec["risk_domain"]]
            yt.append(t)
            yp.append(p)
            if t != p:
                examples.append({"incident_id": iid, "expert": t, "ours": p, "summary": rec["summary"]})
    res = {"domain": single_label_scores(yt, yp, labels)}
    st, sp = [], []
    for iid, rec in ours.items():
        if iid in sub and rec.get("risk_subdomain"):
            st.append(sub[iid][0].split(" ")[0].rstrip("."))
            sp.append(rec["risk_subdomain"])
    res["subdomain_accuracy"] = round(float(np.mean([a == b for a, b in zip(st, sp)])), 3) if st else None
    res["subdomain_n"] = len(st)
    # secondary: crosswalk from primary failure mode
    cw = taxonomy.crosswalk("mit_domain_from_primary_failure")
    pairs = [(mit[i][0], cw.get(r["primary_failure_mode"])) for i, r in ours.items()
             if i in mit and r.get("primary_failure_mode") in cw]
    res["via_failure_mode_accuracy"] = round(float(np.mean([a == b for a, b in pairs])), 3) if pairs else None
    for fld, key, cwname in (("Intent", "intent", "mit_intent"), ("Entity", "cause_entity", "mit_entity")):
        e = expert(con, "MIT", fld)
        m = taxonomy.crosswalk(cwname)
        t = [e[i][0] for i, r in ours.items() if i in e and r.get(key)]
        p = [m.get(r[key], "Other") for i, r in ours.items() if i in e and r.get(key)]
        res[fld.lower()] = single_label_scores(t, p, sorted(set(m.values())))
    res["disagreements"] = examples
    return res


def eval_gmf_failure(con, ours):
    cw = taxonomy.crosswalk("gmf_failure")
    gmf = expert(con, "GMF", "Known AI Technical Failure")
    unmapped = Counter(v for vals in gmf.values() for v in vals if v not in cw)
    pairs, ex = [], []
    for iid, vals in gmf.items():
        if iid in ours:
            e = {cw[v] for v in vals if v in cw}
            if e:
                o = tagset(ours[iid], "failure_mode")
                pairs.append((e, o))
                if not (e & o):
                    ex.append({"incident_id": iid, "expert": sorted(e), "ours": sorted(o), "summary": ours[iid]["summary"]})
    res = multilabel_scores(pairs)
    res["unmapped_gmf_values"] = dict(unmapped.most_common(10))
    res["disagreements"] = ex
    return res


def eval_cset_sector(con, ours):
    cw = taxonomy.crosswalk("cset_sector")
    rev = {o: c for c, lst in cw.items() for o in lst}
    cs = expert(con, "CSETv1", "Sector of Deployment")
    pairs, ex = [], []
    for iid, vals in cs.items():
        e = {v for v in vals if v in cw}
        if iid in ours and e:
            o = {rev[t] for t in tagset(ours[iid], "sector") if t in rev}
            pairs.append((e, o))
            if not (e & o):
                ex.append({"incident_id": iid, "expert": sorted(e), "ours": sorted(tagset(ours[iid], "sector")),
                           "summary": ours[iid]["summary"]})
    res = multilabel_scores(pairs)
    res["disagreements"] = ex
    return res


def eval_gmf_technology(con, ours):
    cw = taxonomy.crosswalk("gmf_goal_technology")
    gmf = expert(con, "GMF", "Known AI Goal")
    pairs = []
    for iid, vals in gmf.items():
        e = {cw[v] for v in vals if v in cw}
        if iid in ours and e:
            pairs.append((e, tagset(ours[iid], "technology")))
    return multilabel_scores(pairs)


def eval_severity(con, ours):
    th = expert(con, "CSETv1", "Tangible Harm")
    lives = expert(con, "CSETv1", "Lives Lost")
    rows = []
    for iid, r in ours.items():
        sev = (r.get("severity") or {}).get("id")
        if sev and iid in th:
            rows.append((th[iid][0], SEV_RANK[sev]))
    by = defaultdict(list)
    for k, v in rows:
        by[k].append(v)
    table = {k: {"n": len(v), "mean_severity": round(float(np.mean(v)), 2),
                 "share_s2_plus": round(float(np.mean([x >= 2 for x in v])), 2)} for k, v in by.items()}
    deaths = [(int(float(lives[i][0])) if lives[i][0].replace(".", "", 1).isdigit() else 0, SEV_RANK[(r.get("severity") or {}).get("id", "s0_none")])
              for i, r in ours.items() if i in lives and r.get("severity")]
    fatal = [s for d, s in deaths if d > 0]
    return {"by_cset_tangible_harm": table, "n": len(rows),
            "fatal_incidents_n": len(fatal),
            "fatal_coded_s4_share": round(float(np.mean([s == 4 for s in fatal])), 2) if fatal else None}


def expert_baseline(con) -> dict[str, Any]:
    """Agreement among CSETv1 annotators on the same incidents (context for our numbers)."""
    out = {}
    anns = ["CSETv1_Annotator-1", "CSETv1_Annotator-2", "CSETv1_Annotator-3"]
    for field in ("Sector of Deployment", "Tangible Harm", "AI Harm Level", "Harm Distribution Basis"):
        sets = {a: {i: set(v) for i, v in expert(con, a, field).items()} for a in anns}
        jac, exact = [], []
        for x in range(3):
            for y in range(x + 1, 3):
                for iid in set(sets[anns[x]]) & set(sets[anns[y]]):
                    s1, s2 = sets[anns[x]][iid], sets[anns[y]][iid]
                    jac.append(len(s1 & s2) / len(s1 | s2) if s1 | s2 else 1.0)
                    exact.append(s1 == s2)
        out[field] = {"pairs": len(jac), "jaccard": round(float(np.mean(jac)), 3) if jac else None,
                      "exact_agreement": round(float(np.mean(exact)), 3) if exact else None}
    return out


def eval_second_coder(primary: dict[int, dict], second: dict[int, dict]) -> dict[str, Any]:
    common = sorted(set(primary) & set(second))
    if not common:
        return {"n": 0}
    res: dict[str, Any] = {"n": len(common), "jaccard": {}}
    for dim in taxonomy.TAG_DIMENSIONS:
        j = []
        for i in common:
            a, b = tagset(primary[i], dim), tagset(second[i], dim)
            j.append(len(a & b) / len(a | b) if a | b else 1.0)
        res["jaccard"][dim] = round(float(np.mean(j)), 3)
    for key in ("risk_domain", "primary_failure_mode", "intent", "cause_entity"):
        a = [str(primary[i].get(key)) for i in common]
        b = [str(second[i].get(key)) for i in common]
        res[key] = {"agreement": round(float(np.mean([x == y for x, y in zip(a, b)])), 3),
                    "kappa": round(float(cohen_kappa_score(a, b)), 3)}
    sa = [SEV_RANK.get((primary[i].get("severity") or {}).get("id"), -1) for i in common]
    sb = [SEV_RANK.get((second[i].get("severity") or {}).get("id"), -1) for i in common]
    ok = [(x, y) for x, y in zip(sa, sb) if x >= 0 and y >= 0]
    if ok:
        x, y = zip(*ok)
        res["severity"] = {"n": len(ok), "exact": round(float(np.mean([a == b for a, b in ok])), 3),
                           "within_one": round(float(np.mean([abs(a - b) <= 1 for a, b in ok])), 3),
                           "weighted_kappa": round(float(cohen_kappa_score(x, y, weights="quadratic")), 3)}
    return res


# ----------------------------------------------------------------------------------------------- report
def build() -> dict[str, Any]:
    con = connect()
    ours = load_ours()
    second = load_ours("second")
    res = {"n_extracted": len(ours),
           "mit": eval_mit(con, ours),
           "gmf_failure": eval_gmf_failure(con, ours),
           "cset_sector": eval_cset_sector(con, ours),
           "gmf_technology": eval_gmf_technology(con, ours),
           "severity": eval_severity(con, ours),
           "expert_baseline": expert_baseline(con),
           "second_coder": eval_second_coder(ours, {i: r for i, r in second.items() if i in ours})}
    paths.PROCESSED.mkdir(parents=True, exist_ok=True)
    (paths.PROCESSED / "evaluation.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    write_markdown(res, con)
    return res


def _cm_md(sc: dict) -> str:
    labs = [l.split(" ")[0].rstrip(".") for l in sc["labels"]]
    lines = ["| expert ↓ / ours → | " + " | ".join(labs) + " |", "|---" * (len(labs) + 1) + "|"]
    for lab, row in zip(labs, sc["confusion"]):
        lines.append(f"| **{lab}** | " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def _per_label_md(per: dict) -> str:
    rows = sorted(per.items(), key=lambda kv: -kv[1]["support"])
    out = ["| label | support | precision | recall | F1 |", "|---|---:|---:|---:|---:|"]
    out += [f"| {k} | {v['support']} | {v['precision']:.2f} | {v['recall']:.2f} | {v['f1']:.2f} |" for k, v in rows if v["support"]]
    return "\n".join(out)


def write_markdown(res: dict, con) -> None:
    title = {r[0]: r[1] for r in con.execute("SELECT incident_id, title FROM incidents")}
    m = res["mit"]
    L = ["# Evaluation", "", "_Generated by `python -m atlas.analysis.evaluation` from `data/processed/evaluation.json`._", "",
         f"Extracted incidents evaluated: **{res['n_extracted']}**. Expert labels come from the AIID snapshot "
         "(MIT AI Risk Repository domains, GMF, CSETv1). The coder never saw expert labels.", ""]
    d = m["domain"]
    if d.get("n"):
        L += ["## 1. Risk domain vs MIT (single label, 7 classes)", "",
              f"- n = {d['n']}; accuracy **{d['accuracy']:.1%}** (majority-class baseline {d['majority_baseline']:.1%}); "
              f"macro-F1 **{d['macro_f1']:.2f}**; Cohen's κ **{d['kappa']:.2f}**",
              f"- Subdomain (23 classes) exact accuracy: {m['subdomain_accuracy']:.1%} (n = {m['subdomain_n']})" if m["subdomain_accuracy"] is not None else "",
              f"- Secondary check — MIT domain derived from our *primary failure mode* via crosswalk: {m['via_failure_mode_accuracy']:.1%} "
              "(lower, as expected: a mechanism is not a risk category)." if m["via_failure_mode_accuracy"] is not None else "",
              f"- MIT *Intent*: accuracy {m['intent']['accuracy']:.1%}, κ {m['intent']['kappa']:.2f}; "
              f"MIT *Entity*: accuracy {m['entity']['accuracy']:.1%}, κ {m['entity']['kappa']:.2f}" if m['intent'].get('n') else "",
              "", "Confusion matrix (rows = expert, columns = ours; domains 1–7):", "", _cm_md(d), ""]
    for key, name, note in (("gmf_failure", "2. Failure mode vs GMF *Known AI Technical Failure* (crosswalked)",
                             "GMF failures are low-level technical causes; the crosswalk is many-to-one and some GMF values are unmapped (listed below)."),
                            ("cset_sector", "3. Sector vs CSETv1 *Sector of Deployment* (CSET buckets)", ""),
                            ("gmf_technology", "4. Technology vs GMF *Known AI Goal* (crosswalked)", "")):
        r = res[key]
        if not r.get("n"):
            continue
        L += [f"## {name}", "", f"- n = {r['n']}; sample-averaged Jaccard **{r['jaccard']:.2f}**; at least one shared label "
              f"**{r['any_overlap']:.1%}**; micro-F1 {r['micro_f1']:.2f}; macro-F1 {r['macro_f1']:.2f}", ""]
        if note:
            L += [note, ""]
        L += [_per_label_md(r["per_label"]), ""]
        if key == "gmf_failure":
            L += ["Most frequent unmapped GMF values: " + ", ".join(f"{k} ({v})" for k, v in r["unmapped_gmf_values"].items()), ""]
    s = res["severity"]
    if s["n"]:
        L += ["## 5. Severity vs CSETv1 harm (ordinal sanity check)", "",
              "CSET does not grade magnitude, so we check that our severity is ordered consistently with CSET's "
              "tangible-harm categories.", "", "| CSET tangible harm | n | mean severity (0–4) | share ≥ s2 |", "|---|---:|---:|---:|"]
        for k, v in sorted(s["by_cset_tangible_harm"].items(), key=lambda kv: kv[1]["mean_severity"]):
            L.append(f"| {k} | {v['n']} | {v['mean_severity']:.2f} | {v['share_s2_plus']:.0%} |")
        if s["fatal_incidents_n"]:
            L += ["", f"Incidents where CSET records ≥ 1 life lost: {s['fatal_incidents_n']}; coded `s4_critical` by us: "
                      f"{s['fatal_coded_s4_share']:.0%}."]
        L.append("")
    b = res["expert_baseline"]
    L += ["## 6. Context: how much do expert annotators agree with each other?", "",
          "Pairwise agreement between CSETv1 annotators on the same incidents (from the per-annotator namespaces).", "",
          "| field | annotator pairs | mean Jaccard | exact set agreement |", "|---|---:|---:|---:|"]
    for k, v in b.items():
        if v["pairs"]:
            L.append(f"| {k} | {v['pairs']} | {v['jaccard']:.2f} | {v['exact_agreement']:.0%} |")
    L.append("")
    sc = res["second_coder"]
    if sc.get("n"):
        L += ["## 7. Blind second coding", "",
              f"A different model (Claude Haiku) re-coded a random sample of **{sc['n']}** incidents with the same "
              "prompt and inputs, without access to the primary outputs.", "",
              "| dimension | mean Jaccard |", "|---|---:|"] + [f"| {k} | {v:.2f} |" for k, v in sc["jaccard"].items()]
        L += ["", "| field | agreement | Cohen's κ |", "|---|---:|---:|"]
        for k in ("risk_domain", "primary_failure_mode", "intent", "cause_entity"):
            L.append(f"| {k} | {sc[k]['agreement']:.0%} | {sc[k]['kappa']:.2f} |")
        if "severity" in sc:
            v = sc["severity"]
            L += ["", f"Severity: exact {v['exact']:.0%}, within one band {v['within_one']:.0%}, "
                      f"quadratic-weighted κ **{v['weighted_kappa']:.2f}** (n = {v['n']})."]
        L.append("")
    L += ["## 8. Analyzed disagreements", "",
          "A sample of cases where our coding and the expert label do not overlap, with a short reading of why.", ""]
    for key, name in (("mit", "MIT risk domain"), ("gmf_failure", "GMF failure"), ("cset_sector", "CSET sector")):
        ex = (res[key]["disagreements"] if key != "mit" else m["disagreements"])[:6]
        if ex:
            L += [f"### {name}", ""]
            for e in ex:
                L.append(f"- **#{e['incident_id']}** {title.get(e['incident_id'], '')} — expert: `{e['expert']}`; ours: `{e['ours']}`")
            L.append("")
    L += ["<!-- ANALYSIS -->", ""]
    path = paths.REPORTS / "evaluation.md"
    # keep any hand-written analysis below the marker across regenerations
    tail = ""
    if path.exists() and "<!-- ANALYSIS -->" in path.read_text():
        tail = path.read_text().split("<!-- ANALYSIS -->", 1)[1].lstrip("\n")
    path.write_text("\n".join(x for x in L if x is not None) + tail)


if __name__ == "__main__":
    r = build()
    print(json.dumps({k: (v if k in ("n_extracted",) else "…") for k, v in r.items()}))
    print(json.dumps(r["mit"]["domain"], indent=0)[:600])
