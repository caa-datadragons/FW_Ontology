# PATCH-README — FW_Ontology: web documentation with pyLODE and a GitHub Action

Builds an HTML documentation of the ontology (pyLODE) plus the ontology as Turtle, RDF/XML and JSON-LD, publishes them on
GitHub Pages and prepares the redirections for w3id.org. Applies on top of `e466412` ("Update README.md").

## Contents

Sources only. The build folder `_site/` is made by the workflow and not committed.

| Path | Status | Purpose |
|---|---|---|
| `py/build_docs.py` | new | reads the `.owl` **as Turtle**, checks it, writes `index.html`, `ontology.ttl`, `.rdf`, `.jsonld` |
| `.github/workflows/docs.yml` | new | builds on every change to the ontology; on `main` it publishes on GitHub Pages; a pull request only builds |
| `requirements-docs.txt` | new | exact versions: pyLODE 3.2.0 (3.4.1 to 3.6.0 do not import any more) |
| `deploy/w3id/fw_ontology/.htaccess`, `README.md` | new | content negotiation for `https://w3id.org/fw_ontology/` and every term, for the pull request at perma-id/w3id.org |
| `.gitignore` | new | `_site/` |
| `CHANGELOG.md` | new | the repository had none |
| `ontology/nfdi_fw_ontology.owl` | modified | ontology IRI `.../fw_ontology/#` becomes `.../fw_ontology/`; title, description, licence (CC0), two `rdfs:seeAlso`; **no class or property changed** |
| `README.md` | modified | a section "Documentation" |

## Applying

    unzip -o fw-ontology-docs-patch.zip -d C:\git\FW_Ontology

(or extract with Explorer into the repository folder). Overwritten, not added: `ontology/nfdi_fw_ontology.owl` and `README.md`.

## What to run

Locally (optional; Python 3.11 or newer, pyLODE does not run on 3.10):

    pip install -r requirements-docs.txt
    python py/build_docs.py

Then open `_site/index.html`. On GitHub, one setting once: **Settings, Pages, Build and deployment, Source: "GitHub Actions"**.
After the push the workflow "Documentation" builds and publishes; the page is
https://caa-datadragons.github.io/FW_Ontology/ .

## How to verify

1. `python py/build_docs.py` ends with `OK     wrote _site: index.html, ontology.ttl, ontology.rdf, ontology.jsonld`. It prints three warnings:
   the classes `FuzzinessWobblinessResourceValue`, `UncertainResourceValue` and `VagueResourceValue` have no `rdfs:comment`.
2. `_site/index.html` shows the title, the nine terms (six classes, one object property, two datatype properties) and a line with the download links.
3. The Action run on `main` is green (job "build", then "deploy"); the Pages URL above answers.
4. Without the IRI fix in the ontology the script stops with the message about the `#`, which shows that the check works.

## Verified here

Fresh clone of `e466412` plus this patch, pyLODE 3.2.0 with the pinned requirements in a new environment, under Python 3.12 and 3.13:
the build runs, the three RDF files are isomorphic to the source, `index.html` makes no request to an external server, the page was looked at in Chromium.
Not checked: the GitHub Action itself and the `.htaccess` (no Apache here; the rules follow the pattern of the AMT entry, which passes `check_redirects` 10 of 10).

## Open points for you (in the ontology, not in the patch)

- `owl:Ontology` has no `dcterms:creator`, `dcterms:created` / `dcterms:modified` or `owl:versionInfo`. pyLODE would show them; I did not invent them.
- Three classes have no `rdfs:comment` (see above), and no term has an `rdfs:label`; pyLODE derives the label from the name ("Uncertain Value").
- The file is called `.owl` but holds Turtle. A rename to `.ttl` would be cleaner; the script reads it as Turtle either way.

## Commit

    git add .github .gitignore CHANGELOG.md README.md deploy ontology py requirements-docs.txt

    git commit -m "Build the ontology documentation with pyLODE and publish it on GitHub Pages" -m "The ontology IRI ended in '#', which pyLODE cannot process; it is now the namespace IRI, and the ontology has a title, description and licence." -m "The script reads the .owl file as Turtle, writes HTML, Turtle, RDF/XML and JSON-LD, and the workflow publishes them; the .htaccess for w3id.org is prepared."

    git push
