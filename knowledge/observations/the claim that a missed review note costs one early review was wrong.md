---
genitor: "[[observations]]"
tags: [failure-direction, rationale]
date: 2026-11-06
supports: ["[[a fail-safe argument holds only if a miss happens once]]", "[[justifying prose drifts from the thing it justifies]]"]
---
Strict recognition was justified in the script's docstring, the spec, and the PR. A missed older note, the argument went, "costs one early review, which then writes the current marker." A review showed that holds only when the new marker is recognized. When a qualifier or a section-heading variant hid the marker, the review fired again on every write, with no error. The fix added a step that re-runs the count after writing and confirms the note was seen.
