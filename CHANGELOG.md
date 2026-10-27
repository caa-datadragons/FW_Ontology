# Changelog

All notable changes to the FW Ontology repository are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Web documentation of the ontology: `py/build_docs.py` reads `ontology/nfdi_fw_ontology.owl` (Turtle in a file
  called `.owl`), checks it and writes `index.html` (pyLODE) and `ontology.ttl`, `ontology.rdf`, `ontology.jsonld`
  to `_site/`. The workflow `.github/workflows/docs.yml` builds it on every change to the ontology and publishes it
  on GitHub Pages; a pull request only checks that the build works.
- `requirements-docs.txt` with exact versions (pyLODE 3.2.0; the releases 3.4.1 to 3.6.0 do not import any more).
- `deploy/w3id/fw_ontology/`: the `.htaccess` and a README for the entry at w3id.org (content negotiation for the
  ontology and for each term).
- `.gitignore` for the build folder.

### Changed

- `ontology/nfdi_fw_ontology.owl`: the ontology IRI is `http://w3id.org/fw_ontology/` (it was
  `http://w3id.org/fw_ontology/#`, which pyLODE cannot process and which does not match the namespace of the
  terms). The ontology has a `dcterms:title`, `dcterms:description`, `dcterms:license` (CC0, as in `LICENSE`) and
  `rdfs:seeAlso` the two Zenodo records named in the README. No class or property is changed.
- `README.md`: a section "Documentation".
