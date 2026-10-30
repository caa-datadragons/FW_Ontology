# AMT with the FW ontology

The Academic Meta Tool models knowledge as concepts connected by weighted roles. This page shows the AMT
vocabulary, how an edge carries its FW values, and four example edges.

## The AMT vocabulary

![AMT schema: vocabulary, weighted edge and reasoning](img/amt-schema.svg)

The vocabulary (axiom classes, logic operators with their formulas) is read from `data/external/amt.ttl`.
An AMT edge is a reified statement (`rdf:subject`, `rdf:predicate`, `rdf:object`) with `amt:weight`. The
reasoner derives new edges (red) from role chains, inverses and subsumptions, and reports violations of
disjointness.

## The weight rule

The weight of an edge is taken from the string in the source (Thiery, Mees, Tolle and Wigg-Wolf 2021):

    amt_weight = 1 / (n_question + n_possibilities)

- **AND** keeps the full weight for every entity.
- **OR**: the alternatives share the weight equally; `n_possibilities` is their number.
- **?** counts as one more share (`n_question` = 1).
- The result is rounded to two decimals. A string that mixes AND and OR is not covered.

In the draft this rule is the individual `fw:EqualShareRule`, a `fw:RuleBasedMethod` with the formula as a
literal, so that it can be named, described and resolved like any other method.

## The hextuple

With the draft, the weight is written as `fw:hasDegreeOfConnection` (the same property as `amt:weight`),
and the edge gets a type and a method. The source string is kept as evidence.

| Part | Property |
|---|---|
| subject, predicate, object | `rdf:subject`, `rdf:predicate`, `rdf:object` |
| degree | `fw:hasDegreeOfConnection` (equivalent to `amt:weight`) |
| type | `fw:hasType` |
| method | `fw:hasMethod` |
| evidence (optional) | `fw:derivedFrom` |

## Concrete edges

The picture is drawn from `data/fw_amt_example.ttl`. The values are invented; `ex:` stands for the terms of
the archaeological model.

![AMT view: concrete edges with their FW values](img/amt-view.svg)

| Edge | Evidence | Degree | Type | Method |
|---|---|---|---|---|
| carrier1 produced at Lezoux | text "Lezoux or Vichy ?" | 0.33 | fuzziness/wobbliness | equal share rule |
| carrier1 produced at Vichy | the same text | 0.33 | fuzziness/wobbliness | equal share rule |
| carrier2 produced at South Gaul | text "South Gaul?" | 0.50 | uncertainty | equal share rule |
| stamp depicts stamp type X | image (AI detection) | 0.87 | uncertainty | model confidence score |

The first two edges show why the evidence is a node of its own: both alternatives come from one string and
point to the same evidence. With one question mark and two alternatives the rule gives 1 / (1 + 2) = 0.33; with
one entity and a question mark it gives 1 / (1 + 1) = 0.50.

The fourth edge has the same shape with another kind of method: the degree is the score a model reports,
the evidence is the image it was run on.

## For the engine

A reasoner that reads both `amt:weight` and `fw:hasDegreeOfConnection` treats the two as one property
(`owl:equivalentProperty`); without OWL reasoning it has to look for both.
