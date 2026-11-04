# PATCH-README — FW_Ontology: a question mark halves the weight; fw:FrequencyShare

Applies on top of `85af65b` ("Add fw:Certainty and fw:AFEAssignment, make confidence a kind of degree").
Decided with Allard Mees and Florian Thiery on 2026-11-04 (Mini-AMT Memos 0.7.0 and 0.8.0).

## Contents

| Path | Status | Purpose |
|---|---|---|
| `ontology/nfdi_fw_ontology.owl` | modified | `fw:EqualShareRule`: comment and `fw:formula` `(1 / n_possibilities) * (1/2 if n_question else 1)`; new individual `fw:FrequencyShare` (a `fw:ProbabilityMethod`); example in the comment of `fw:formula` |
| `data/fw_amt_example.ttl` | modified | `Lezoux or Vichy ?` gives 0.25 (was 0.33) |
| `docs/amt.md` | modified | weight rule, examples and the table follow |
| `CHANGELOG.md` | modified | entries under Unreleased (Changed, Added) |

No class or property changed. `PATCH-README.md` of the earlier patch is replaced by this file (delete it before the commit if you do not want it in the repository).

## Run (repository root, Windows, one line)

```
tar -xf fw-ontology-patch-equalshare.zip && python main.py --only guide && git status --short
```

## Check

- `git status --short` lists the four files above (and `PATCH-README.md`).
- The ontology and the example still parse; `python main.py --only guide` runs through (`--only ontology` needs pyLODE as before).
- In the built guide the AMT view shows 0.25 for "Lezoux or Vichy ?".

## Commit

```
git add -A && git commit -m "Question mark halves the weight in fw:EqualShareRule; add fw:FrequencyShare" && git push
```
