---
genitor: "[[patterns]]"
tags: [architecture, validation, scope]
---

# build enforcement against demonstrated need, not anticipated failure

Enforcement machinery earns its place only against errors that are **silent, compounding, or frequent** —
not against failures that reveal themselves and are cheap to fix on notice. Building it ahead of a
demonstrated failure is "prematurely solving a problem you don't have": the guard hardens against an
unattended, adversarial executor the actual workflow never contains, and its worst-case escaped error
("a note is slightly wrong until the next run reads it") is trivial. Defer such machinery to an evidence
trigger, not a schedule — and drop policy distinctions (tiers, postures, modes) until a concrete case
demands them.

*One witness (2026-07-15). Open.*

## evidence
- [[validation earns its keep only when errors are silent, compounding, or frequent]]
- [[dropping the personal-professional promotion split removed a problem not yet encountered]]
- [[a green tested validator PR was closed because it solved nothing real]]

## related
- [[prose conventions plus human approval can replace a validator]]
- [[added complexity generates its own defect supply]]
