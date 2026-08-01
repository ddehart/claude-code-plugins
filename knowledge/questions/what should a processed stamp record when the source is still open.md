---
genitor: "[[questions]]"
tags: [process, provenance]
---
## question
A `processed:` stamp records a date. That is sufficient for a finished source and misleading for an
append-only one: a session, a thread, a log still being written. The stamp is what makes a re-run resume
instead of redo, so a date-only stamp over a source that has since grown marks new material as handled
while reading as complete. A run over a live session is also inside its own material, so its read
necessarily stops short of itself — the shortfall is structural, not an oversight to be more careful about.
What should the stamp carry — a byte offset, a last-read timestamp, a message index — for a later run to
know where to resume, and where should it live so a run consults it rather than the prose beside it?

## evidence
- [[a processed stamp covered half a still-growing source]]
