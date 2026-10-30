#!/usr/bin/env python3
"""General AMT schema as SVG: the vocabulary of amt.ttl, the weighted edge, and what the reasoner derives.

    python build_amt_schema.py AMT.ttl --out DIR [--jpg]

The vocabulary part (axiom classes, logic operators with their formulas) is read from the
ontology file, so it follows amt.ttl. The edge and the four reasoning patterns are schematic
and follow the reasoning rules written in amt.ttl (RoleChainRule, InverseRule, SubsumptionRule,
DisjointRule, SelfDisjointRule). Derived edges and violations are drawn in red.

Needs rdflib; build_hierarchy.py must lie next to this script. JPG needs cairosvg and Pillow.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from rdflib import RDF, URIRef

import build_hierarchy as bh
from build_hierarchy import AMBER, CHAR_W, CLASS_FILL, GREY, INST_FILL, curie, draw_tree, label, load, rect

AMT = "http://academic-meta-tool.xyz/vocab#"
RED = "#c00000"
bh.EDGE["reason"] = RED  # adds the red arrow head to the marker definitions


def arrow(out, d, red=False, dashed=False):
    k, col = ("reason", RED) if red else ("sub", "#000000")
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.8" marker-end="url(#m{k})"{dash}/>')


def tag(out, x, y, text, red=False, size=11, weight="normal"):
    label(out, x, y, text, color=RED if red else "#000000", size=size, weight=weight, halo=True)


def heading(out, x, y, text):
    label(out, x, y, text, size=14, weight="bold", anchor="start")


def operators(g):
    """Logic operators with their formula, read from the ontology."""
    rows = []
    for op in sorted(g.subjects(RDF.type, URIRef(AMT + "Logic")), key=curie):
        f = next(iter(g.objects(op, URIRef(AMT + "formula"))), None)
        if f is not None:
            rows.append(f"{curie(op).replace('amt:', '')}   {f}")
    return rows


# ---- the four reasoning patterns -----------------------------------------------------------

PW, PH = 330, 196


def frame(out, x0, y0, title, sub):
    out.append(f'<rect x="{x0}" y="{y0}" width="{PW}" height="{PH}" rx="10" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2"/>')
    label(out, x0 + PW / 2, y0 + 22, title, size=13, weight="bold")
    label(out, x0 + PW / 2, y0 + 40, sub, size=11, color="#444444")


def node(out, x, y, text):
    rect(out, x, y, 56, 34, text, GREY, oval=True)


def pattern_chain(out, x0, y0):
    frame(out, x0, y0, "amt:RoleChainAxiom", "r1 followed by r2 implies the consequent role")
    cy, a, b, c = y0 + 100, x0 + 50, x0 + 165, x0 + 280
    for x, t in ((a, "a"), (b, "b"), (c, "c")):
        node(out, x, cy, t)
    arrow(out, f"M{a + 28},{cy} L{b - 28},{cy}")
    tag(out, (a + b) / 2, cy - 12, "r1 · w1")
    arrow(out, f"M{b + 28},{cy} L{c - 28},{cy}")
    tag(out, (b + c) / 2, cy - 12, "r2 · w2")
    arrow(out, f"M{a},{cy + 17} Q{b},{cy + 85} {c},{cy + 17}", red=True)
    tag(out, b, cy + 66, "consequent · w = logic(w1, w2)", red=True)


def pattern_inverse(out, x0, y0):
    frame(out, x0, y0, "amt:InverseAxiom", "the inverse role holds the other way round")
    cy, a, b = y0 + 100, x0 + 80, x0 + 250
    node(out, a, cy, "a")
    node(out, b, cy, "b")
    arrow(out, f"M{a + 28},{cy} L{b - 28},{cy}")
    tag(out, (a + b) / 2, cy - 12, "r · w")
    arrow(out, f"M{b},{cy + 17} Q{(a + b) / 2},{cy + 85} {a},{cy + 17}", red=True)
    tag(out, (a + b) / 2, cy + 66, "inverse(r) · w", red=True)


def pattern_sub(out, x0, y0):
    frame(out, x0, y0, "amt:SubsumptionAxiom", "a finer role implies the coarser one")
    cy, a, b = y0 + 100, x0 + 80, x0 + 250
    node(out, a, cy, "a")
    node(out, b, cy, "b")
    arrow(out, f"M{a + 28},{cy} L{b - 28},{cy}")
    tag(out, (a + b) / 2, cy - 12, "subRole · w")
    arrow(out, f"M{a},{cy + 17} Q{(a + b) / 2},{cy + 85} {b},{cy + 17}", red=True)
    tag(out, (a + b) / 2, cy + 66, "superRole · w", red=True)


def pattern_disjoint(out, x0, y0):
    frame(out, x0, y0, "amt:DisjointAxiom", "two disjoint roles must not hold between the same pair")
    cy, a, b = y0 + 100, x0 + 80, x0 + 250
    node(out, a, cy, "a")
    node(out, b, cy, "b")
    arrow(out, f"M{a + 18},{cy - 14} Q{(a + b) / 2},{cy - 66} {b - 18},{cy - 14}")
    tag(out, (a + b) / 2, cy - 48, "role1 · w > 0")
    arrow(out, f"M{a + 18},{cy + 14} Q{(a + b) / 2},{cy + 66} {b - 18},{cy + 14}")
    tag(out, (a + b) / 2, cy + 52, "role2 · w > 0")
    tag(out, (a + b) / 2, cy + 3, "✕ violation", red=True, size=13, weight="bold")
    tag(out, x0 + PW / 2, y0 + PH - 14, "same for a –r→ a with amt:SelfDisjointAxiom", red=True, size=10.5)


# ---- figure --------------------------------------------------------------------------------

def figure(g) -> str:
    out: list[str] = []
    heading(out, 30, 66, "Vocabulary (read from amt.ttl)")
    top = 100
    r1, b1, _ = draw_tree(g, g, URIRef(AMT + "Axiom"), 30, top, out, False)
    _, b1a, _ = draw_tree(g, g, URIRef(AMT + "Concept"), 30, b1 + 8, out, False)
    _, b1b, _ = draw_tree(g, g, URIRef(AMT + "Role"), 30, b1a - 6, out, False)
    x2 = r1 + 90
    r2, b2, _ = draw_tree(g, g, URIRef(AMT + "Logic"), x2, top, out, True)
    rows = operators(g)
    bx = r2 + 70
    bw = max(len(s) for s in rows) * 6.2 + 28 if rows else 200
    label(out, bx, top - 14, "Operators (amt:formula)", size=13, weight="bold", anchor="start")
    out.append(f'<rect x="{bx}" y="{top}" width="{bw:.0f}" height="{len(rows) * 24 + 14}" rx="8" fill="#ffffff" '
               f'stroke="#000000" stroke-width="1.4"/>')
    for i, s in enumerate(rows):
        label(out, bx + 12, top + 20 + i * 24, s, size=11.5, anchor="start")
    right = bx + bw
    section = max(b1b, b2, top + len(rows) * 24 + 14) + 40

    # weighted edge
    heading(out, 30, section, "The weighted edge")
    ye = section + 100
    rect(out, 150, ye, 190, 60, ["Node a", "amt:instanceOf Concept"], GREY, oval=True, size=11)
    rect(out, 430, ye, 200, 52, ["Role", "(rdf:predicate)"], AMBER)
    rect(out, 710, ye, 190, 60, ["Node b", "amt:instanceOf Concept"], GREY, oval=True, size=11)
    rect(out, 1000, ye, 150, 52, ["xsd:decimal", "0 … 1"], "#ffffff")
    arrow(out, f"M{150 + 95},{ye} L{430 - 100},{ye}")
    arrow(out, f"M{430 + 100},{ye} L{710 - 95},{ye}")
    arrow(out, f"M430,{ye - 26} Q715,{ye - 90} {1000 - 20},{ye - 26}")
    tag(out, 715, ye - 62, "amt:weight")
    label(out, 30, ye + 56, "An edge is a reified statement (rdf:subject, rdf:predicate, rdf:object) with amt:weight. "
          "The reasoner adds inferred edges and marks them as inferred.", size=11, color="#444444", anchor="start")

    # reasoning
    heading(out, 30, ye + 96, "What the reasoner derives (red)")
    py = ye + 112
    for i, fn in enumerate((pattern_chain, pattern_inverse, pattern_sub, pattern_disjoint)):
        fn(out, 30 + i * (PW + 24), py)
    right = max(right, 30 + 4 * PW + 3 * 24)
    bottom = py + PH

    # legend
    ly, lx = bottom + 40, 30
    for fill, lab, oval in ((GREY, "resource (node)", True), (CLASS_FILL, "class", False),
                            (INST_FILL, "individual / term", False), (AMBER, "role", False)):
        if oval:
            out.append(f'<ellipse cx="{lx + 23}" cy="{ly - 2}" rx="23" ry="11" fill="{fill}" stroke="#000" stroke-width="1.6"/>')
        else:
            out.append(f'<rect x="{lx}" y="{ly - 12}" width="46" height="20" rx="5" fill="{fill}" stroke="#000" stroke-width="1.6"/>')
        label(out, lx + 56, ly, lab, size=12, anchor="start")
        lx += 56 + len(lab) * CHAR_W + 30
    out.append(f'<line x1="{lx}" y1="{ly - 2}" x2="{lx + 40}" y2="{ly - 2}" stroke="{RED}" stroke-width="1.8" marker-end="url(#mreason)"/>')
    label(out, lx + 50, ly, "derived by the reasoner / violation", size=12, anchor="start")
    right = max(right, lx + 50 + 230)
    return bh.finish("AMT schema: vocabulary, weighted edge and reasoning", out, right, ly + 10)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ontology", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--jpg", action="store_true")
    a = ap.parse_args()
    svg = figure(load([a.ontology]))
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "amt-schema.svg").write_text(svg, encoding="utf-8")
    print(f"OK     wrote {a.out / 'amt-schema.svg'}")
    if a.jpg:
        import cairosvg
        from PIL import Image
        png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), scale=1.6)
        Image.open(io.BytesIO(png)).convert("RGB").save(a.out / "amt-schema.jpg", quality=92)
        print(f"OK     wrote {a.out / 'amt-schema.jpg'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
