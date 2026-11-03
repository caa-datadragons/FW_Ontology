# Model

The extension answers one question: how does a statement say *how much* it holds, *what kind of* fuzziness
that is, and *how* the number was obtained?

## New properties

| Property | Range | Meaning |
|---|---|---|
| `fw:hasDegreeOfConnection` | `xsd:decimal` | Degree [0-1] to which a statement holds. `owl:equivalentProperty` of `amt:weight`. The degree can describe anything between 0 and 1; `fw:hasConfidence` (an assessment by a contributor or a system) is a sub-property of it, not the other way round. |
| `fw:hasType` | `fw:FW_Type` | The kind of fuzziness/wobbliness: vagueness, uncertainty, or both together; or certainty for a statement without any of them. |
| `fw:hasMethod` | `fw:Method` | The method by which the degree was obtained. |
| `fw:formula` | `xsd:string` | The calculation rule of a method as text. |
| `fw:implementedBy` | IRI | Resolvable IRI of the code that implements a method. |
| `fw:derivedFrom` | any | Optional link to the evidence (sub-property of `prov:wasDerivedFrom`). |

## Type

`fw:hasType` points to a term of the class `fw:FW_Type`. The terms are individuals, so that the property
points to a term and not to a class.

![Branch: type](img/branch-fw-type.svg)

`fw:FuzzinessWobbliness` is the umbrella term, used when vagueness and uncertainty cannot be told apart.

`fw:Certainty` stands beside `fw:Vagueness` and `fw:Uncertainty`, not below the umbrella: a certain statement is
neither vague nor uncertain. It goes with a degree of 1.0 and exists so that certain statements can be told from
statements whose type is not given (AMT.engine reads a missing type as `fw:Vagueness`) and so that they take part in
reasoning. When a statement is derived from several others, AMT.engine ignores `fw:Certainty` as long as another type is
present; different types give `fw:FuzzinessWobbliness`.

**Type or value class?** The type (`fw:Vagueness`) says what kind of fuzziness a statement has and is the value of
`fw:hasType`. The value class (`fw:VagueValue`) is the container in which a value is stored, for example in AFE. Each
value class points to its type with `rdfs:seeAlso`; `fw:UncertainValue` holds exactly one value, several candidates are a
`fw:VagueValue` or a `fw:FuzzinessWobblinessValue`.

`fw:UncertainValue` and `fw:VagueValue` are subclasses of `fw:FuzzinessWobblinessValue`, so that the value
classes follow the same umbrella as the type terms. This is the only change to what the ontology said before;
everything else is addition.

![Branch: value classes](img/branch-value-classes.svg)

## Method

A method is a procedure that produces or combines degrees. The hierarchy separates the methods that obtain a
degree for one statement (*assignment*) from those that combine degrees along a chain (*propagation*).
Concrete methods are individuals with a label, a comment and a formula, so they resolve by their IRI.
The list is open: a new method is a new individual, not a change of the ontology.

![Branch: method](img/branch-method.svg)

The AMT logics (Goedel, product, Lukasiewicz, Einstein product, geometric mean, Hamacher product) are
propagation methods. Typing them belongs in `amt.ttl`; `data/amt-alignment.ttl` holds the proposed triples,
which is why the logics are drawn with a dashed outline.

## Evidence

The optional link from a statement to what its degree rests on. Several statements may share one evidence
node, which keeps them together: the alternatives of an OR share the string they came from.

![Branch: evidence](img/branch-evidence.svg)

An embedding is given by a link to the vector and by the model that produced it; the vector itself is not
written into the graph.

## Open points

- The mapping of the source-string form to the type (`?` to uncertainty, OR to vagueness, both to
  fuzziness/wobbliness) is a hypothesis and has to be confirmed with the domain experts.
- `fw:implementedBy` stays empty until the code that implements the weight rule is published.
- The IRIs of the methods resolve only when the w3id entry is live (see `deploy/w3id/fw_ontology/`).
