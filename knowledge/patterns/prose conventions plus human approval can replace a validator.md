---
genitor: "[[patterns]]"
tags: [architecture, validation, human-in-the-loop]
---

# prose conventions plus human approval can replace a validator

When every write to a system passes through a plan a human reads and approves, an executable write-time
validator mostly guards against an implementer who doesn't exist. The structural rules that keep the
artifact coherent survive as sentences of convention — applied by the LLM reading its instructions and by
the human reading the proposed plan — rather than as code. In this graph the single load-bearing rule
(every evidence note must support at least one attractor) is one sentence of prose, not a validation
module. If real drift ever appears, a small check script can earn its way in that day.

*One witness (2026-07-15). Open.*

## evidence
- [[reverting the validator left graph health on approval plus conventions]]
- [[the validator only ever caught defects in itself, its spec, and its fixtures]]

## related
- [[build enforcement against demonstrated need, not anticipated failure]]
- [[knowledge-commons ships at the weight of the system it generalizes]]
