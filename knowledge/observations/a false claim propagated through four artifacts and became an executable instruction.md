---
genitor: "[[observations]]"
tags: [epistemics, provenance, silent-failure]
date: 2026-08-01
supports: ["[[a claim restated into several artifacts starts reading as corroborated]]"]
---
"The founding transcript is gone" originated in one search scoped to a project glob that could never match
the file. It was then written into the generated process skill's prose, into a decision note, into a spec's
§1.1 as its closing argument for committing raw material to a public repo, and into that spec's §6 as an
instruction to mark the source note `raw: unavailable`. From there it reached a handoff prompt for a
different session already implementing the spec. During the original diagnosis the skill's own restatement
was cited as evidence for the claim — a copy read as independent support. Both halves were false: the
transcript was intact at 2.8 MB, and the source note recorded no pointer that could dangle. Correcting it
took four edits and a version bump; the first pass missed §6, where the claim had stopped being prose and
become a step, and the miss was caught only by a grep run to confirm the commit was clean.

## source
- [[session f64160a1 — the process pipeline correction, specced not built]]
