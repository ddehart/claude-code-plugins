---
genitor: "[[observations]]"
tags: [release, drift-by-design, refinement]
date: 2026-07-15
supports: ["[[execution against real data catches what authoring and review miss]]", "[[promotion is scheduled into the process pipeline, never left to memory]]"]
---
The shipped plugin drove releases 0.1.0 → 0.1.7 in a single day, every bump traced to a real defect or gap
surfaced by an actual run: atlas-naming interview question, commons-discovery search-before-give-up,
human-readable queue entries, overlapping-tiers double-counting, map-frontmatter conformance, CI-trigger
exclusions, and the promote commit-and-push contract. This is the same evidence-first bar that killed the
validator, now applied to the plugin's own evolution — "a much better first day than the validator ever
had," and the drift-by-design loop working at the plugin layer.
