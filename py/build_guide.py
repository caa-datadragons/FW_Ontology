#!/usr/bin/env python3
"""Build the guide: the pages in docs/*.md as HTML, with figures drawn from the ontology files.

    python py/build_guide.py                 write _site/guide/
    python py/build_guide.py --out DIR       other output folder

The guide explains the ontology; the reference (every class and property) is the pyLODE page
built by py/build_docs.py. This script

  1. draws the figures with py/build_hierarchy.py and py/build_amt_schema.py. Their sources are the
     current ontology, the draft extension and the example data, so a figure cannot drift from them,
  2. renders each docs/*.md to a self-contained HTML page (one style block, no script, no external
     request) with a small navigation, and copies the figures next to the pages.

The pages are listed in PAGES, in that order. Output is deterministic: no clock, sorted input.
Needs the ``markdown`` package (in requirements-docs.txt) and rdflib.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import markdown

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / "py"

ONTOLOGY = ROOT / "ontology" / "nfdi_fw_ontology.owl"
DRAFT = ROOT / "ontology" / "draft" / "fw_extension_draft.ttl"
DATA = ROOT / "data" / "fw_amt_example.ttl"
AMT = ROOT / "data" / "external" / "amt.ttl"

PAGES = [  # (file in docs/, title in the navigation)
    ("index", "Overview"),
    ("model", "Model"),
    ("amt", "AMT with the FW ontology"),
]

CSS = """
:root{--fg:#1a1a1a;--muted:#555;--line:#d0d7de;--bg:#fff;--code:#f6f8fa;--link:#0b5cad}
@media (prefers-color-scheme:dark){:root{--fg:#e6e6e6;--muted:#aaa;--line:#3a3f45;--bg:#14171a;--code:#1d2126;--link:#6cb0f5}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,Segoe UI,Helvetica,Arial,sans-serif}
header{border-bottom:1px solid var(--line);padding:.8rem 1rem}
nav a{margin-right:1.1rem;color:var(--link);text-decoration:none}nav a.here{font-weight:700;color:var(--fg)}
main{max-width:62rem;margin:0 auto;padding:1rem}
a{color:var(--link)}img{max-width:100%;height:auto;background:#fff;border:1px solid var(--line);border-radius:6px}
table{border-collapse:collapse;margin:1rem 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:.35rem .6rem;text-align:left;vertical-align:top}
code,pre{background:var(--code);border-radius:4px;font:14px ui-monospace,Consolas,monospace}
code{padding:.1rem .3rem}pre{padding:.8rem;overflow-x:auto}pre code{padding:0;background:none}
blockquote{margin:1rem 0;padding:.1rem 1rem;border-left:4px solid var(--line);color:var(--muted)}
footer{border-top:1px solid var(--line);padding:1rem;color:var(--muted);font-size:14px;text-align:center}
"""

FIGURES = ["classes", "branch-method", "branch-fw-type", "branch-value-classes", "branch-evidence", "amt-view", "amt-schema"]


def run(args: list[str]) -> None:
    done = subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding="utf-8")
    sys.stdout.write(done.stdout)
    if done.returncode != 0:
        sys.stderr.write(done.stderr)
        raise SystemExit(f"ERROR  {' '.join(Path(a).name for a in args)} failed")


def draw_figures(img: Path) -> None:
    img.mkdir(parents=True, exist_ok=True)
    run([str(PY / "build_hierarchy.py"), str(ONTOLOGY), "--draft", str(DRAFT), "--data", str(DATA), "--out", str(img)])
    run([str(PY / "build_amt_schema.py"), str(AMT), "--out", str(img)])
    missing = [f for f in FIGURES if not (img / f"{f}.svg").is_file()]
    if missing:
        raise SystemExit(f"ERROR  figures not written: {', '.join(missing)}")


def page(name: str, title: str, body: str) -> str:
    nav = "".join(
        f'<a href="{n}.html"{" class=here" if n == name else ""}>{escape(t)}</a>' for n, t in PAGES
    )
    nav += '<a href="../index.html">Reference</a><a href="../draft/index.html">Reference with draft</a>'
    return (
        f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{escape(title)} - FW Ontology</title><style>{CSS}</style></head>"
        f"<body><header><nav>{nav}</nav></header><main>\n{body}\n</main>"
        f'<footer>FW Ontology guide, generated from the files in the repository '
        f'<a href="https://github.com/caa-datadragons/FW_Ontology">caa-datadragons/FW_Ontology</a></footer>'
        f"</body></html>\n"
    )


def build(out: Path) -> int:
    docs = ROOT / "docs"
    draw_figures(out / "img")
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    for name, title in PAGES:
        src = docs / f"{name}.md"
        if not src.is_file():
            raise SystemExit(f"ERROR  {src} not found")
        md.reset()
        text = src.read_text(encoding="utf-8")
        # links between the pages are written as .md in the sources and as .html in the output
        text = re.sub(r"\]\(([a-z]+)\.md(#[^)]*)?\)", r"](\1.html\2)", text)
        (out / f"{name}.html").write_text(page(name, title, md.convert(text)), encoding="utf-8")
        print(f"OK     wrote {out / (name + '.html')}")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=ROOT / "_site" / "guide", help="output folder (default: _site/guide)")
    return build(ap.parse_args(argv).out)


if __name__ == "__main__":
    sys.exit(main())
