#!/usr/bin/env python3
"""Draw the FW ontology as SVG: class hierarchy, one view per branch, and an AMT view.

The pictures are made from the ontology files themselves, so they cannot drift from them.

    python build_hierarchy.py ONTOLOGY.owl [MORE.ttl ...] --out DIR
                              [--draft DRAFT.ttl ...] [--data EXAMPLE.ttl] [--jpg]

ONTOLOGY    files of the current ontology (Turtle, also when the file is called .owl)
--draft     files proposed on top of it: terms and links that are not in the current
            ontology are drawn with a dashed outline
--data      instance data (reified statements with fw:hasDegreeOfConnection, fw:hasType,
            fw:hasMethod and optional fw:derivedFrom) for the AMT view
--jpg       also write a JPG per picture (needs cairosvg and Pillow; the SVG needs neither)

Writes   classes.svg            all classes, no individuals
         branch-<name>.svg      one branch with its individuals (method, fw-type,
                                value-classes, evidence)
         amt-view.svg           concrete edges with their FW values (only with --data)

Needs rdflib only (pyLODE brings it). Output is deterministic.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef

FW = "http://w3id.org/fw_ontology/"
AMT = "http://academic-meta-tool.xyz/vocab#"
SKOS_BROADER = URIRef("http://www.w3.org/2004/02/skos/core#broader")
PREFIXES = {
    FW: "fw:",
    AMT: "amt:",
    "http://www.w3.org/2001/XMLSchema#": "xsd:",
    "http://example.org/samian/": "ex:",
}
BRANCHES = [  # (file name, title, root term)
    ("method", "Method", FW + "Method"),
    ("fw-type", "FW type", FW + "FW_Type"),
    ("value-classes", "Value classes", FW + "FuzzinessWobblinessValue"),
    ("evidence", "Evidence", FW + "Evidence"),
]
CLASS_FILL, INST_FILL, AMBER, GREY = "#9a3412", "#4c1d95", "#fbbf24", "#e2e8f0"
ROW_H, GAP, NODE_H, CHAR_W = 38, 44, 28, 6.6
EDGE = {"sub": "#000000", "type": INST_FILL, "broader": "#7c3aed"}
PRED = {"sub": RDFS.subClassOf, "type": RDF.type, "broader": SKOS_BROADER}
FONT = "Helvetica,Arial,sans-serif"


# ---- helpers --------------------------------------------------------------------------

def curie(u) -> str:
    s = str(u)
    for ns, pf in PREFIXES.items():
        if s.startswith(ns):
            return pf + s[len(ns):]
    return s.rsplit("#", 1)[-1].rsplit("/", 1)[-1] or s


def load(paths) -> Graph:
    g = Graph()
    for p in paths:
        g.parse(str(p), format="turtle")  # .owl files of this repo hold Turtle
    return g


def short(text: str, n: int = 34) -> str:
    return text if len(text) <= n else text[: n - 1] + "…"


def svg_doc(title, body, w, h) -> str:
    defs = "".join(
        f'<marker id="m{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
        f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for k, c in EDGE.items())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" '
            f'height="{h:.0f}"><defs>{defs}</defs><rect width="100%" height="100%" fill="#ffffff"/>'
            f'<text x="{w / 2:.0f}" y="32" text-anchor="middle" font-size="17" font-weight="bold" '
            f'font-family="{FONT}">{escape(title)}</text>' + "".join(body) + "</svg>")


def label(out, x, y, lines, color="#000000", size=12, weight="normal", anchor="middle", halo=False):
    if isinstance(lines, str):
        lines = [lines]
    lh = size + 3
    y0 = y - (len(lines) - 1) * lh / 2 + size / 3
    tsp = "".join(f'<tspan x="{x:.1f}" y="{y0 + i * lh:.1f}">{escape(t)}</tspan>' for i, t in enumerate(lines))
    base = (f'<text text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" font-weight="{weight}"')
    if halo:  # white underlay (no paint-order: not every renderer supports it), then the text on top
        out.append(base + f' fill="#ffffff" stroke="#ffffff" stroke-width="4" stroke-linejoin="round">{tsp}</text>')
    out.append(base + f' fill="{color}">{tsp}</text>')


def rect(out, cx, cy, w, h, lines, fill, color="#000000", dashed=False, size=12, oval=False):
    d = ' stroke-dasharray="6 4"' if dashed else ""
    if oval:
        out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{w / 2:.1f}" ry="{h / 2:.1f}" fill="{fill}" '
                   f'stroke="#000000" stroke-width="1.6"{d}/>')
    else:
        out.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" '
                   f'fill="{fill}" stroke="#000000" stroke-width="1.6"{d}/>')
    label(out, cx, cy, lines, color, size)


def finish(title, out, right, bottom):
    w = max(right, len(title) * 10) + 40
    return svg_doc(title, out, w, bottom + 30)


# ---- trees ----------------------------------------------------------------------------

def is_class(g, n) -> bool:
    return ((n, RDF.type, OWL.Class) in g or (n, RDF.type, RDFS.Class) in g
            or (n, RDFS.subClassOf, None) in g or (None, RDFS.subClassOf, n) in g)


def children(g, node, individuals):
    kids = [(s, "sub") for s in g.subjects(RDFS.subClassOf, node) if isinstance(s, URIRef)]
    if individuals:
        for s in g.subjects(RDF.type, node):
            # an individual with a skos:broader parent hangs below that parent, not below the class
            if isinstance(s, URIRef) and not any(isinstance(o, URIRef) for o in g.objects(s, SKOS_BROADER)):
                kids.append((s, "type"))
        kids += [(s, "broader") for s in g.subjects(SKOS_BROADER, node) if isinstance(s, URIRef)]
    kids.sort(key=lambda k: (k[1] != "sub", curie(k[0])))
    return kids


def build_tree(g, root, individuals):
    kids, ekind, seen, order = {}, {}, {root}, [root]

    def walk(n):
        kids[n] = []
        for c, k in children(g, n, individuals):
            if c in seen:
                continue
            seen.add(c)
            order.append(c)
            kids[n].append(c)
            ekind[c] = k
            walk(c)

    walk(root)
    return order, kids, ekind


def node_w(n) -> float:
    return max(86.0, len(curie(n)) * CHAR_W + 22)


def draw_tree(g, g0, root, x0, y0, out, individuals):
    """Draw one tree; return (right edge, bottom edge, number of rows)."""
    order, kids, ekind = build_tree(g, root, individuals)
    depth = {root: 0}
    for n in order:
        for c in kids[n]:
            depth[c] = depth[n] + 1
    colw = {}
    for n in order:
        colw[depth[n]] = max(colw.get(depth[n], 0), node_w(n))
    colx, x = {}, x0
    for d in sorted(colw):
        colx[d] = x
        x += colw[d] + GAP
    ypos, row = {}, [0]

    def place(n):
        if not kids[n]:
            ypos[n] = y0 + row[0] * ROW_H
            row[0] += 1
        else:
            for c in kids[n]:
                place(c)
            ypos[n] = (ypos[kids[n][0]] + ypos[kids[n][-1]]) / 2

    place(root)
    for n in order:  # edges first, nodes on top
        for c in kids[n]:
            k = ekind[c]
            dash = ' stroke-dasharray="6 4"' if (c, PRED[k], n) not in g0 else ""
            xc, yc = colx[depth[c]], ypos[c]
            xp, yp = colx[depth[n]] + node_w(n), ypos[n]
            xm = xp + (xc - xp) / 2
            out.append(f'<path d="M{xc:.1f},{yc:.1f} H{xm:.1f} V{yp:.1f} H{xp:.1f}" fill="none" '
                       f'stroke="{EDGE[k]}" stroke-width="1.5"{dash} marker-end="url(#m{k})"/>')
    for n in order:
        w = node_w(n)
        rect(out, colx[depth[n]] + w / 2, ypos[n], w, NODE_H, curie(n),
             CLASS_FILL if is_class(g, n) else INST_FILL, "#ffffff",
             dashed=(n, RDF.type, None) not in g0)
    return x - GAP, y0 + max(row[0], 1) * ROW_H, max(row[0], 1)


def legend(y, individuals, draft):
    out, x = [], 30

    def swatch(fill, lab, dashed=False):
        nonlocal x
        d = ' stroke-dasharray="6 4"' if dashed else ""
        out.append(f'<rect x="{x}" y="{y - 12}" width="46" height="20" rx="5" fill="{fill}" stroke="#000" '
                   f'stroke-width="1.6"{d}/>')
        label(out, x + 56, y, lab, size=12, anchor="start")
        x += 56 + len(lab) * CHAR_W + 30

    def arrow(k, lab):
        nonlocal x
        out.append(f'<line x1="{x}" y1="{y - 2}" x2="{x + 40}" y2="{y - 2}" stroke="{EDGE[k]}" '
                   f'stroke-width="1.5" marker-end="url(#m{k})"/>')
        label(out, x + 50, y, lab, size=12, anchor="start")
        x += 50 + len(lab) * CHAR_W + 30

    swatch(CLASS_FILL, "class")
    if individuals:
        swatch(INST_FILL, "individual / term")
    arrow("sub", "rdfs:subClassOf")
    if individuals:
        arrow("type", "rdf:type")
        arrow("broader", "skos:broader")
    if draft:
        swatch("#ffffff", "dashed = proposed, not in the current ontology", dashed=True)
    return out, x


# ---- views ----------------------------------------------------------------------------

def class_roots(g):
    skip = ("http://www.w3.org/",)
    cls = {s for s in g.subjects(RDF.type, OWL.Class) if isinstance(s, URIRef)}
    cls |= {s for s in g.subjects(RDFS.subClassOf, None) if isinstance(s, URIRef)}
    cls |= {o for o in g.objects(None, RDFS.subClassOf) if isinstance(o, URIRef)}
    cls = {c for c in cls if not str(c).startswith(skip)}
    return [c for c in cls if not any(isinstance(o, URIRef) and o in cls for o in g.objects(c, RDFS.subClassOf))]


def property_lines(g, g0):
    lines = []
    for kind in (OWL.ObjectProperty, OWL.DatatypeProperty):
        for p in g.subjects(RDF.type, kind):
            if not isinstance(p, URIRef) or (p, RDF.type, None) in g0:
                continue
            rng = next(iter(g.objects(p, RDFS.range)), None)
            dom = next(iter(g.objects(p, RDFS.domain)), None)
            eq = next(iter(g.objects(p, OWL.equivalentProperty)), None)
            s = curie(p) + (f"  ({curie(dom)})" if dom else "") + "  ->  " + (curie(rng) if rng else "any")
            lines.append(s + (f"   = {curie(eq)}" if eq else ""))
    return sorted(lines)


def view_classes(g, g0, draft):
    roots = class_roots(g)
    size = {r: draw_tree(g, g0, r, 0, 0, [], False) for r in roots}
    roots.sort(key=lambda r: (-size[r][2], curie(r)))
    out = []
    lr, lb, _ = draw_tree(g, g0, roots[0], 30, 80, out, False)
    rx, y, right, bottom = lr + 90, 80, lr, lb
    for r in roots[1:]:
        rr, rb, _ = draw_tree(g, g0, r, rx, y, out, False)
        right, bottom, y = max(right, rr), max(bottom, rb), rb + 24
    props = property_lines(g, g0)
    if props:
        pw = max(len(s) for s in props) * 6.4 + 24
        label(out, rx, y + 14, "New properties", size=14, weight="bold", anchor="start")
        out.append(f'<rect x="{rx}" y="{y + 28}" width="{pw:.0f}" height="{len(props) * 24 + 12}" rx="8" '
                   f'fill="#fff8e1" stroke="#000000" stroke-width="1.4" stroke-dasharray="6 4"/>')
        for i, s in enumerate(props):
            label(out, rx + 12, y + 52 + i * 24, s, size=12, anchor="start")
        right, bottom = max(right, rx + pw), max(bottom, y + 40 + len(props) * 24)
    leg, lright = legend(bottom + 30, False, draft)
    return finish("FW ontology: class hierarchy (classes only)", out + leg, max(right, lright), bottom + 40)


def view_branch(g, g0, title, root, draft):
    out = []
    label(out, 30, 62, title, size=14, weight="bold", anchor="start")
    right, bottom, _ = draw_tree(g, g0, root, 30, 100, out, True)
    leg, lright = legend(bottom + 30, True, draft)
    return finish(f"FW ontology: {title} (classes and individuals)", out + leg, max(right, lright), bottom + 40)


COLS = [("Subject", 150), ("Role", 160), ("Object", 140), ("Degree", 90),
        ("Type", 170), ("Method", 160), ("Evidence (optional)", 250)]
ARCS = [("fw:hasDegreeOfConnection", 3, 40), ("fw:hasType", 4, 62), ("fw:hasMethod", 5, 84), ("fw:derivedFrom", 6, 106)]


def first(g, s, *preds):
    for p in preds:
        v = sorted(g.objects(s, URIRef(p)), key=str)
        if v:
            return v[0]
    return None


def evidence_lines(g, ev):
    lines = [curie(ev)]
    typ = sorted(g.objects(ev, RDF.type), key=str)
    if typ:
        lines.append("a " + curie(typ[0]))
    for prop, fmt in (("sourceString", '"{}"'), ("hasMediaLink", "{}"), ("hasEmbedding", "{}"), ("embeddingModel", "{}")):
        v = first(g, ev, FW + prop)
        if v is not None:
            lines.append(fmt.format(short(str(v) if isinstance(v, Literal) else curie(v) if str(v).startswith(tuple(PREFIXES)) else str(v), 32)))
            break
    return lines


def view_amt(gd):
    stmts = sorted((s for s in gd.subjects(RDF.subject, None) if isinstance(s, URIRef)), key=curie)
    if not stmts:
        sys.exit("ERROR  --data holds no named statement (rdf:subject on an IRI)")
    out, x, centers, lefts = [], 30, [], []
    for name, w in COLS:
        lefts.append(x)
        centers.append(x + w / 2)
        label(out, x + w / 2, 112, name, size=13, weight="bold")
        x += w + 34
    right = x - 34
    pitch, y0 = 190, 270
    for i, s in enumerate(stmts):
        y = y0 + i * pitch
        S, P, O = (gd.value(s, p) for p in (RDF.subject, RDF.predicate, RDF.object))
        deg = first(gd, s, FW + "hasDegreeOfConnection", AMT + "weight")
        typ, met = first(gd, s, FW + "hasType"), first(gd, s, FW + "hasMethod")
        evs = sorted(gd.objects(s, URIRef(FW + "derivedFrom")), key=str)
        rect(out, centers[0], y, 150, 56, curie(S), GREY, oval=True)
        rect(out, centers[1], y, 160, 48, [curie(P), f"({curie(s)})"], AMBER)
        rect(out, centers[2], y, 140, 56, curie(O), GREY, oval=True)
        for a, b, wa, wb in ((0, 1, 150, 160), (1, 2, 160, 140)):
            out.append(f'<line x1="{centers[a] + wa / 2:.1f}" y1="{y}" x2="{centers[b] - wb / 2:.1f}" y2="{y}" '
                       f'stroke="#000" stroke-width="1.5" marker-end="url(#msub)"/>')
        targets = {3: (str(deg) if deg is not None else "-", "#ffffff", "#000000", 40),
                   4: (curie(typ) if typ else "-", INST_FILL, "#ffffff", 40),
                   5: (curie(met) if met else "-", INST_FILL, "#ffffff", 40)}
        for col, (txt, fill, colr, h) in targets.items():
            rect(out, centers[col], y, COLS[col][1], h, txt, fill, colr)
        if evs:
            rect(out, centers[6], y, 250, 68, evidence_lines(gd, evs[0]) + ([f"+{len(evs) - 1} more"] if len(evs) > 1 else []),
                 "#ffffff", size=11)
        for lab, col, a in ARCS:
            if col == 6 and not evs:
                continue
            x1, y1 = centers[1], y - 24
            x2, y2 = centers[col], y - (34 if col == 6 else 20)
            out.append(f'<path d="M{x1:.1f},{y1} C{x1:.1f},{y1 - a} {x2:.1f},{y2 - a} {x2:.1f},{y2}" fill="none" '
                       f'stroke="#000" stroke-width="1.4" marker-end="url(#msub)"/>')
            label(out, (x1 + x2) / 2, y1 - 0.75 * a - 3, lab, size=10.5, halo=True)
    bottom = y0 + (len(stmts) - 1) * pitch + 60
    ly, lx = bottom + 30, 30
    for fill, lab, oval in ((GREY, "resource (subject, object)", True), (AMBER, "role = reified statement", False),
                            (INST_FILL, "FW term (individual)", False), ("#ffffff", "literal / evidence", False)):
        if oval:
            out.append(f'<ellipse cx="{lx + 23}" cy="{ly - 2}" rx="23" ry="11" fill="{fill}" stroke="#000" stroke-width="1.6"/>')
        else:
            out.append(f'<rect x="{lx}" y="{ly - 12}" width="46" height="20" rx="5" fill="{fill}" stroke="#000" stroke-width="1.6"/>')
        label(out, lx + 56, ly, lab, size=12, anchor="start")
        lx += 56 + len(lab) * CHAR_W + 30
    label(out, 30, 62, "One row per edge: Subject, Role, Object and the three FW values; evidence is optional and may be shared.",
          size=12, anchor="start")
    return finish("AMT view: concrete edges with their FW values", out, max(right, lx), bottom + 40)


# ---- main -----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ontology", nargs="+", type=Path)
    ap.add_argument("--draft", nargs="*", default=[], type=Path)
    ap.add_argument("--data", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--jpg", action="store_true")
    a = ap.parse_args()

    g0 = load(a.ontology)
    g = load(a.ontology + a.draft)
    figures = [("classes", view_classes(g, g0, bool(a.draft)))]
    for name, title, root in BRANCHES:
        if (URIRef(root), None, None) in g or (None, None, URIRef(root)) in g:
            figures.append((f"branch-{name}", view_branch(g, g0, title, URIRef(root), bool(a.draft))))
    if a.data:
        figures.append(("amt-view", view_amt(load([a.data]))))

    a.out.mkdir(parents=True, exist_ok=True)
    for name, svg in figures:
        (a.out / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"OK     wrote {a.out / (name + '.svg')}")
        if a.jpg:
            import cairosvg
            from PIL import Image
            png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), scale=1.6)
            Image.open(io.BytesIO(png)).convert("RGB").save(a.out / f"{name}.jpg", quality=92)
            print(f"OK     wrote {a.out / (name + '.jpg')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
