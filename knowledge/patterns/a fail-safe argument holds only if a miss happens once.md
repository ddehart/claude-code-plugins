---
genitor: "[[patterns]]"
tags: [failure-direction, rationale, strictness]
---

# a fail-safe argument holds only if a miss happens once

"Be strict: a false match is the bad direction, and a miss only costs one extra run" is sound only if the
miss corrects itself. When the missed record is the very thing the next run looks for, the miss recurs on
every run. The safe direction then becomes a loop that never ends and never errors. Before choosing a
failure direction, trace the miss through the next cycle and check that something closes it.

*Two witnesses (2026-11-06, 2026-11-08). Open.*

## evidence
- [[the claim that a missed review note costs one early review was wrong]]
- [[after 0.6.0 a single delta anchor would have skipped forever in about half the live graphs]]

## related
- [[a list of negating phrasings cannot be complete, so allow what may follow]]
- [[justifying prose drifts from the thing it justifies]]
