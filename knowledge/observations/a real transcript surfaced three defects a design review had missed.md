---
genitor: "[[observations]]"
tags: [verification, testing, generator]
date: 2026-07-15
supports: ["[[execution against real data catches what authoring and review miss]]"]
---
Asked whether a freshly generated pipeline was complete, the session tested it against a real ~1.2MB
transcript instead of answering from the design — and surfaced three real defects in the just-written
skill: it called a human-facing skill instead of the headless script, produced an unreadable UUID-keyed
queue, and named a de-duplication safeguard with no actual mechanism (the hazard live in the very first
queue). None were visible to authoring-time review; all three surfaced on the first end-to-end run against
representative input.
