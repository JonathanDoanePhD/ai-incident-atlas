"""Build a single-file, self-contained copy of the website for a private preview.

Inlines the stylesheet, scripts, data files and images (as data: URIs), and points relative links to project documents at
the repository branch on GitHub. Writes only the output path given; publishing is a separate, explicit step.

Usage: python scripts/build_preview.py <output.html>
"""
import base64
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "website"
REPO = "https://github.com/JonathanDoanePhD/ai-incident-atlas/blob/claude/hopeful-meitner-7n06qq/turning-point-project/"


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or ("image/webp" if path.suffix == ".webp" else "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def main(out: str) -> None:
    html = (WEB / "index.html").read_text()
    html = html.replace('<link rel="stylesheet" href="assets/style.css">', "<style>\n" + (WEB / "assets/style.css").read_text() + "\n</style>")
    for src in ("data/site.js", "data/findings.js", "assets/app.js", "assets/hero.js"):
        tag = f'<script src="{src}"></script>'
        assert tag in html, tag
        html = html.replace(tag, "<script>\n" + (WEB / src).read_text() + "\n</script>")
    html = re.sub(r'(src|href)="(assets/img/[^"]+)"', lambda m: f'{m.group(1)}="{data_uri(WEB / m.group(2))}"', html)
    html = re.sub(r'(["\'])\.\./((?:docs|manuscripts|crosscheck|outputs|scripts)/)', lambda m: m.group(1) + REPO + m.group(2), html)
    if '<meta name="claude:viewport-fit-sides"' not in html:
        html = html.replace('<meta name="viewport"', '<meta name="claude:viewport-fit-sides" content="cover">\n<meta name="viewport"', 1)
    leftovers = re.findall(r'(?:src|href)="(?!https?:|data:|#|mailto:|\$\{)[^"]+"', html)
    assert not leftovers, leftovers
    Path(out).write_text(html)
    print(f"wrote {out} ({len(html):,} bytes)")


if __name__ == "__main__":
    main(sys.argv[1])
