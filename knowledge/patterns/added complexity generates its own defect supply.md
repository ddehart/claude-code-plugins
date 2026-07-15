---
genitor: "[[patterns]]"
tags: [validation, review, anti-pattern]
---

# added complexity generates its own defect supply

Machinery added to catch failures reliably produces new failures in itself, and a verification loop that
keeps "finding real defects" is often just the apparatus debugging itself. The tell: the defects a round
surfaces are overwhelmingly in machinery that a *previous* round of the same loop added, and each catch is
mis-scored as "the method working." A non-declining defect yield across audit passes measures the process,
not the artifact — it is a signal to stop hardening and cut, not to keep auditing. (Corroborated across
two artifacts in-session: the validator that only ever caught bugs in itself, and a spec-audit loop that
grew 363→990 lines while producing zero code.)

*One witness (2026-07-15). Open.*

## evidence
- [[the validator only ever caught defects in itself, its spec, and its fixtures]]
- [[a neutral build-it cold read measured the spec where an adversarial loop inflated it]]

## related
- [[build enforcement against demonstrated need, not anticipated failure]]
- [[execution against real data catches what authoring and review miss]]
