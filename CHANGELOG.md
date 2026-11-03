# Changelog

All notable changes to the FW Ontology repository are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `fw:Certainty`, a term of `fw:FW_Type` beside `fw:Vagueness` and `fw:Uncertainty` (not below `fw:FuzzinessWobbliness`):
  a certain statement, degree 1.0. *Why:* A certain statement can be told from one whose type is not given, and takes part in reasoning.
- `fw:AFEAssignment`, an assignment method: the degree is entered by the person recording the data in AFE or assigned by AFE
  from the flag the person sets. Kept apart from `fw:EqualShareRule`, which reads the source strings of the Samian data.
- `rdfs:seeAlso` from each value class to its type (`fw:VagueValue` to `fw:Vagueness`, and so on), and a note on type versus value class.
- A fifth example statement in `data/fw_amt_example.ttl`: a certain statement.
- Extension of the ontology for statements such as AMT edges: `fw:hasDegreeOfConnection` (equivalent to
  `amt:weight`), `fw:hasType` with `fw:FW_Type`, `fw:hasMethod` with a method hierarchy and
  `fw:formula`, `fw:implementedBy`, and optional evidence (`fw:derivedFrom`, text, media and embedding evidence), so that an AMT edge
  becomes a hextuple. `fw:UncertainValue` and `fw:VagueValue` are now subclasses of `fw:FuzzinessWobblinessValue`.
- Guide pages in `docs/` (overview, model, AMT with the FW ontology) with figures drawn from the ontology files:
  `py/build_hierarchy.py` (class hierarchy, one view per branch, AMT view of concrete edges),
  `py/build_amt_schema.py` (AMT vocabulary, weighted edge, reasoning), `py/build_guide.py` (pages).
- `data/fw_amt_example.ttl` (four invented example statements), `data/amt-alignment.ttl` (proposed triples for
  `amt.ttl`: the AMT logics as propagation methods) and `data/external/amt.ttl` (copy of the AMT
  vocabulary from amt-engine, commit 987dd8d, CC BY 4.0).
- `main.py` builds everything (`--list`, `--only`, `--from`, `--skip`, `--dry-run`, `--strict`); `PRIMER.md` is
  the work plan (German).
- `py/build_docs.py`: `--extra` and `--banner` document the ontology together with further Turtle files.
- Web documentation of the ontology: `py/build_docs.py` reads `ontology/nfdi_fw_ontology.owl` (Turtle in a file
  called `.owl`), checks it and writes `index.html` (pyLODE) and `ontology.ttl`, `ontology.rdf`, `ontology.jsonld`
  to `_site/`. The workflow `.github/workflows/docs.yml` builds it on every change to the ontology and publishes it
  on GitHub Pages; a pull request only checks that the build works.
- `requirements-docs.txt` with exact versions (pyLODE 3.2.0; the releases 3.4.1 to 3.6.0 do not import any more).
- `deploy/w3id/fw_ontology/`: the `.htaccess` and a README for the entry at w3id.org (content negotiation for the
  ontology and for each term).
- `.gitignore` for the build folder.

### Changed

- `fw:hasConfidence` is now a sub-property of `fw:hasDegreeOfConnection` (a confidence is one kind of degree); the comments of both say
  so and mark the relation as work in progress. They were `rdfs:seeAlso` of each other and "not the same".
- `fw:hasType` and `fw:FW_Type`: the comments say that AMT.engine reads a missing type as `fw:Vagueness`, how a derived statement gets its type,
  and that `fw:Certainty` is written together with degree 1.0. `fw:UncertainValue` holds exactly one value.
- `py/build_hierarchy.py`: the AMT view draws no box and no arrow for a type or a method that a statement does not carry.
- The workflow runs `python main.py` and publishes the reference (`/`) and the guide (`/guide/`); it also runs when
  `docs/`, `data/` or `py/` change. The guide is white, in the colours of the CAA DataDragons logo.
- `ontology/nfdi_fw_ontology.owl`: the prefix `nfdi_fw:` is now `fw:`. The namespace IRI is unchanged and the
  graph is identical (checked with an isomorphism test).
- `ontology/nfdi_fw_ontology.owl`: the ontology IRI is `http://w3id.org/fw_ontology/` (it was
  `http://w3id.org/fw_ontology/#`, which pyLODE cannot process and which does not match the namespace of the
  terms). The ontology has a `dcterms:title`, `dcterms:description`, `dcterms:license` (CC0, as in `LICENSE`) and
  `rdfs:seeAlso` the two Zenodo records named in the README. No class or property is changed.
- `README.md`: a section "Documentation".
