---
genitor: "[[patterns]]"
tags: [maps, silent-failure, verification]
---

# an index omission silently disables the check that reads it

A map is one entry short. The check that reads it still runs, still completes, and still reports clean —
blind to exactly the entry that was missing. A screen over a complete index and a screen over an incomplete
one produce identically shaped output, so the failure is undetectable from the consuming side.

Maps are written by hand at the end of a run, after the interesting work, and nothing reconciles the
directory against them. That makes the omission likely and its detection accidental.

The general form is wider than maps: any absent record that a later check treats as a complete enumeration.
A source note with no transcript pointer is the same defect — it is what let this graph conclude a file was
lost, because there was nothing recorded to check against.

*Two witnesses (2026-07-28, 2026-08-01). Open.*

## evidence
- [[a claims map missing three entries disabled the screen that reads it]]
- [[a source note that recorded no pointer let the graph believe a file was gone]]

## related
- [[a plausible story arrests the investigation before the mechanism is found]]
- [[a test suite stayed green with an entire scan path deleted]]
- [[named readers went silent while unnamed re-spawns with identical briefs all reported]]
