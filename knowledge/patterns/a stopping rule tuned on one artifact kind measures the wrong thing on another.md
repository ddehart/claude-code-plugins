---
genitor: "[[patterns]]"
tags: [review, method, verification]
---

## so what
Before applying a stop-reviewing heuristic, check what its yield signal *meant* where it was calibrated.
Defect-yield-per-pass measures reviewer productivity on a static artifact and coverage of an input space
on an executable one, and a rule tuned on the first will stop you too early on the second.

The tells can all be true and still uninformative. Ask instead: is the remaining defect density
unmeasured, or merely unmeasured *by this reviewer*?

## evidence
- [[a stopping rule tuned on prose review misfired on executable code]]
