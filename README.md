# Fuzzy/Wobbly Ontology (fwO)

In order to model: uncertain, vague or fuzzy/wobbly data the NFDI4O TWG FuzzyWobblySW generated a set of classes an properties for RDF modelling.

NFDI4Objects TWG - Community-Standards for modelling fuzziness & wobbliness in research data using Semantic Web technologies and formalisms (FuzzyWobblySW)
... you can find a more detailed description of the TWG work under: https://zenodo.org/records/14893827

Basic definitions for vageness, uncertainty and their combination:
... more details under: https://zenodo.org/records/19877825 

Definition: Vagueness
“Vagueness refers to a lack of precision in a statement, especially when it comes to
categories, terms, or boundaries that are inherently gradational or context-dependent;
greater vagueness implies less precision, and vice versa. Vagueness is an indicator of how
far a statement is assertive. Such an indicator would normally be qualitative, a quantitative
indicator should be explicitly justified.” (FuzzyWobblySW TWG)

Defintion: Uncertainty
“Uncertainty refers to the limited confidence with which a particular interpretation,
identification, or attribution can be made due to incomplete, ambiguous, or indirect
evidence. Uncertainty arises when conclusions cannot be established with full certainty, such
as when data of objects, features, etc. is assigned a specific interpretation like authority,
period, place, or function, etc.” (FuzzyWobblySW TWG)

Defintion: fuzziness/wobbliness
“Fuzziness/wobbliness is an umbrella term combining uncertainty and vagueness where
they can not be distinguished from each other in statements or data entries. It also covers
any unclear situation, like ambiguous mapping of instances, properties or classes between
ontologies or unreproducible statements, e.g. from literature.” (FuzzyWobblySW TWG)


## Documentation

The ontology is documented as a web page, built from `ontology/nfdi_fw_ontology.owl` by the workflow
`Documentation` (pyLODE) on every change and published on GitHub Pages:

- <https://caa-datadragons.github.io/FW_Ontology/> the documentation (HTML)
- `ontology.ttl`, `ontology.rdf`, `ontology.jsonld` the same ontology in Turtle, RDF/XML and JSON-LD

The namespace is `http://w3id.org/fw_ontology/`; with `https://w3id.org/fw_ontology/` (and a term such as
`https://w3id.org/fw_ontology/UncertainValue`) a browser gets the documentation, and a client that asks for Turtle,
RDF/XML or JSON-LD gets the file. The rules for w3id are in `deploy/w3id/fw_ontology/`.

Build it locally (Python 3.11 or newer; the file is called `.owl` but holds Turtle, and the script knows that):

```
pip install -r requirements-docs.txt
python py/build_docs.py
```

The result is in `_site/`. The script stops with a message if the ontology cannot be documented (for example an
ontology IRI that ends in `#`, or a missing `dcterms:title`) and warns about every term without `rdfs:comment`;
`--strict` turns the warnings into errors.
