# FW Ontology: guide

> The extension described here (degree, type, method, evidence) is part of
> `ontology/nfdi_fw_ontology.owl`. The mapping of the source-string form to the type is still a hypothesis
> (see [Model](model.md)).

The FW ontology (prefix `fw:`, namespace `http://w3id.org/fw_ontology/`) has classes for values that are
fuzzy or wobbly: `fw:UncertainValue`, `fw:VagueValue` and `fw:FuzzinessWobblinessValue`. The ontology has what is
needed to attach such a value to a **statement**, for example an edge of the
[Academic Meta Tool (AMT)](http://academic-meta-tool.xyz/): an edge becomes a **hextuple**

    (subject, predicate / role, object, degree of connection, type, method)

plus an optional link to the **evidence** the degree rests on (a source string, an image, an embedding).

This guide explains the ontology in pictures. The reference of every class and property is generated
separately: [reference](../index.html).

## All classes

The picture shows the class hierarchy without individuals.

![Class hierarchy of the FW ontology](img/classes.svg)

## Pages

| Page | Content |
|---|---|
| [Model](model.md) | The new properties, the type, the method hierarchy, the evidence; one picture per branch |
| [AMT with the FW ontology](amt.md) | The AMT vocabulary, the weight rule, and concrete edges with their FW values |

## Files

| File | Purpose |
|---|---|
| `ontology/nfdi_fw_ontology.owl` | The ontology (Turtle in a file called `.owl`); source of the pictures and of the reference |
| `data/fw_amt_example.ttl` | Four invented example statements for the AMT view |
| `data/amt-alignment.ttl` | Proposed triples for `amt.ttl`: the AMT logics as propagation methods (drawn dashed) |
| `data/external/amt.ttl` | Copy of the AMT vocabulary (see `data/external/README.md`) |
| `py/build_hierarchy.py`, `py/build_amt_schema.py` | Draw the pictures from the files above |
| `py/build_guide.py`, `py/build_docs.py` | Build this guide and the pyLODE reference |

## Rebuild

```
python main.py
```

The workflow `.github/workflows/docs.yml` runs the same command and publishes the result on GitHub Pages.
