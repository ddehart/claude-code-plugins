---
genitor: "[[patterns]]"
tags: [failure-direction, rationale, strictness]
---

# a fail-safe argument holds only if a miss happens once

"Be strict: a false match is the bad direction, and a miss only costs one extra run" is sound only if the
miss corrects itself. When the missed record is the very thing the next run looks for, the miss recurs on
every run. The safe direction then becomes a loop that never ends and never errors. Before choosing a
failure direction, trace the miss through the next cycle and check that something closes it.

*One witness (2026-11-06). Open.*

## evidence
- [[the claim that a missed review note costs one early review was wrong]]

## related
- [[a list of negating phrasings cannot be complete, so allow what may follow]]
- [[justifying prose drifts from the thing it justifies]]
