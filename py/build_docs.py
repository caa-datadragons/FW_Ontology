#!/usr/bin/env python3
"""
Build the web documentation of the FW Ontology.

    python py/build_docs.py                 read ontology/nfdi_fw_ontology.owl, write _site/
    python py/build_docs.py --strict        warnings become errors
    python py/build_docs.py --src X --out Y other input / output folder

The source file is called ``.owl`` but holds Turtle, so neither rdflib nor
pyLODE would guess its format from the extension. This script reads it as
Turtle, checks it, and writes into the output folder:

    index.html       the documentation (pyLODE, profile "ontpub", one file, no external requests)
    ontology.ttl     Turtle
    ontology.rdf     RDF/XML
    ontology.jsonld  JSON-LD
    .nojekyll        so that GitHub Pages serves the files as they are

The output folder is not committed; the workflow in .github/workflows/docs.yml
builds it and publishes it on GitHub Pages. What is checked before anything is
written (an error stops the build, a warning is printed as a GitHub annotation):

    error    not exactly one owl:Ontology; its IRI does not end in "/" (a "#" at the
             end breaks pyLODE: "Can't split ...")
    error    the ontology has no dcterms:title, rdfs:label or schema:name (pyLODE refuses)
    warning  a class or property without rdfs:comment or skos:definition
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rdflib import RDF, RDFS, SKOS, Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL

SDO = Namespace("https://schema.org/")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = ROOT / "ontology" / "nfdi_fw_ontology.owl"
DEFAULT_OUT = ROOT / "_site"

TERM_TYPES = (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty)
TITLE_PROPS = (DCTERMS.title, RDFS.label, SDO.name)
DESCRIPTION_PROPS = (RDFS.comment, SKOS.definition, DCTERMS.description)


class Report:
    """Collects errors and warnings; prints them as GitHub annotations when run in an Action."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)
        print(f"::error::{message}" if _in_action() else f"ERROR  {message}")

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        print(f"::warning::{message}" if _in_action() else f"WARN   {message}")

    def ok(self, message: str) -> None:
        print(f"OK     {message}")


def _in_action() -> bool:
    import os

    return os.environ.get("GITHUB_ACTIONS") == "true"


def load(src: Path) -> Graph:
    """Read the source as Turtle (the extension .owl would make rdflib expect RDF/XML)."""
    g = Graph()
    g.parse(src, format="turtle")
    return g


def check(g: Graph, rep: Report) -> URIRef | None:
    """Return the ontology IRI, or None if the file cannot be documented."""
    onts = sorted(set(g.subjects(RDF.type, OWL.Ontology)), key=str)
    if len(onts) != 1:
        rep.error(f"expected exactly one owl:Ontology, found {len(onts)}: {', '.join(map(str, onts)) or '-'}")
        return None
    ont = onts[0]
    if not str(ont).endswith("/"):
        rep.error(
            f"the ontology IRI <{ont}> does not end in '/'. The namespace of the terms is a slash "
            f"namespace, and an IRI ending in '#' cannot be split by pyLODE"
        )
        return None
    if not any(g.value(ont, p) for p in TITLE_PROPS):
        rep.error(f"<{ont}> has no dcterms:title (or rdfs:label, schema:name); pyLODE refuses to build without one")
        return None
    rep.ok(f"ontology <{ont}>, {len(g)} triples")

    terms = sorted({s for t in TERM_TYPES for s in g.subjects(RDF.type, t) if isinstance(s, URIRef)}, key=str)
    for term in terms:
        if not any(g.value(term, p) for p in DESCRIPTION_PROPS):
            rep.warn(f"<{term}> has no rdfs:comment")
    rep.ok(f"{len(terms)} terms (classes and properties)")
    return ont


def build(src: Path, out: Path, strict: bool) -> int:
    rep = Report()
    if not src.is_file():
        rep.error(f"{src} not found")
        return 1
    g = load(src)
    if check(g, rep) is None:
        return 1
    if strict and rep.warnings:
        print(f"{len(rep.warnings)} warning(s) and --strict is set")
        return 1

    out.mkdir(parents=True, exist_ok=True)
    g.serialize(out / "ontology.ttl", format="turtle")
    g.serialize(out / "ontology.rdf", format="pretty-xml")
    g.serialize(out / "ontology.jsonld", format="json-ld", indent=2)
    (out / ".nojekyll").write_text("", encoding="utf-8")

    from pylode import OntPub  # imported late: needs Python 3.11 or newer

    OntPub(ontology=g).make_html(destination=out / "index.html")
    add_downloads(out / "index.html")
    rep.ok(f"wrote {out}: index.html, ontology.ttl, ontology.rdf, ontology.jsonld")
    return 0


def add_downloads(html_file: Path) -> None:
    """Put a line with the download links under the first heading (pyLODE has no place for them)."""
    html = html_file.read_text(encoding="utf-8")
    line = (
        '<p>Download: <a href="ontology.ttl">Turtle</a> &middot; '
        '<a href="ontology.rdf">RDF/XML</a> &middot; <a href="ontology.jsonld">JSON-LD</a></p>'
    )
    marker = "</h1>"
    if marker in html:
        html_file.write_text(html.replace(marker, marker + line, 1), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC, help="the ontology (Turtle, whatever the extension)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output folder (default: _site)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args(argv)
    return build(args.src, args.out, args.strict)


if __name__ == "__main__":
    sys.exit(main())
