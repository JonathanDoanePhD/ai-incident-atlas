"""Render [@key] citations to APA-style author-year text and a reference list from docs/references.bib.

Usage: python scripts/render_manuscript.py manuscripts/working_paper_v1.src.md manuscripts/working_paper_v1.md
Fails if a cited key is missing from the bibliography.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_bib(text):
    entries = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", text, flags=re.S):
        typ, key, body = m.group(1).lower(), m.group(2).strip(), m.group(3)
        fields = {}
        for f in re.finditer(r"(\w+)\s*=\s*\{(.*?)\},?\s*$", body, flags=re.M | re.S):
            fields[f.group(1).lower()] = re.sub(r"[{}]", "", f.group(2)).strip()
        fields["_type"] = typ
        entries[key] = fields
    return entries


def surname(a):
    a = a.strip()
    return a.split(",")[0].strip() if "," in a else a.split()[-1]


def initials(a):
    a = a.strip()
    given = a.split(",", 1)[1] if "," in a else " ".join(a.split()[:-1])
    return " ".join(p[0] + "." for p in re.split(r"[\s-]+", given.strip()) if p)


def authors_list(e):
    return [x for x in re.split(r"\s+and\s+", e.get("author", "")) if x.strip()]


def intext(e):
    au = authors_list(e)
    s = [surname(a) for a in au]
    yr = e.get("year", "n.d.")
    if len(s) == 1:
        n = s[0]
    elif len(s) == 2:
        n = f"{s[0]} & {s[1]}"
    else:
        n = f"{s[0]} et al."
    return f"{n}, {yr}"


def reference(e):
    au = authors_list(e)
    names = [f"{surname(a)}, {initials(a)}".strip().rstrip(",") for a in au]
    if len(names) > 20:
        names = names[:19] + ["…", names[-1]]
    if len(names) > 1:
        auth = ", ".join(names[:-1]) + ", & " + names[-1]
    else:
        auth = names[0] if names else "Anonymous"
    title = e.get("title", "").rstrip(".").rstrip("*").rstrip()
    if e["_type"] in ("book", "techreport") or (not e.get("journal") and (e.get("publisher") or e.get("institution"))):
        s = f"{', '.join(names[:-1]) + ', & ' + names[-1] if len(names) > 1 else (names[0] if names else 'Anonymous')} ({e.get('year', 'n.d.')}). *{title}*. {e.get('publisher') or e.get('institution', '')}."
        return s + (f" https://doi.org/{e['doi']}" if e.get("doi") else "")
    venue = e.get("journal") or e.get("booktitle") or e.get("publisher", "")
    vol = e.get("volume", "")
    num = e.get("number", "")
    pages = e.get("pages", "").replace("--", "–")
    s = f"{auth} ({e.get('year', 'n.d.')}). {title}. *{venue}*"
    if vol:
        s += f", *{vol}*" + (f"({num})" if num else "")
    if pages:
        s += f", {pages}"
    s += "."
    if e.get("doi"):
        s += f" https://doi.org/{e['doi']}"
    return s


def main(src, dst):
    bib = parse_bib((ROOT / "docs" / "references.bib").read_text(encoding="utf-8"))
    text = Path(src).read_text(encoding="utf-8")
    cited = []

    def repl(m):
        keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        missing = [k for k in keys if k not in bib]
        if missing:
            raise SystemExit(f"Missing from references.bib: {missing}")
        for k in keys:
            if k not in cited:
                cited.append(k)
        return "(" + "; ".join(intext(bib[k]) for k in keys) + ")"

    text = re.sub(r"\[(@[^\]]+)\]", repl, text)
    # APA: order by the full author-surname sequence, then year
    refs = sorted(cited, key=lambda k: ([surname(a).lower() for a in authors_list(bib[k])] or [k], bib[k].get("year", "")))
    text = text.replace("{{REFERENCES}}", "\n\n".join(reference(bib[k]) for k in refs))
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    Path(dst).write_text(text, encoding="utf-8")
    print(f"{dst}: {len(cited)} references")


if __name__ == "__main__":
    main(*sys.argv[1:3])
