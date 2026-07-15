---
genitor: "[[observations]]"
tags: [validation, sunk-cost, refinement]
date: 2026-07-15
supports: ["[[build enforcement against demonstrated need, not anticipated failure]]"]
---
A merge-ready +5,175-line validator PR with 79 passing tests was closed unmerged. The first instinct was
to salvage it by demoting the write-time gate to an on-demand health check; on being asked "what problems
does it solve?", the inventory collapsed — every check was self-revealing, redundant with human approval,
or fixing a problem the validator itself created. Derek named the salvage instinct: "my 'keep it as a
health check' was sunk-cost reasoning — the code being green isn't a reason to carry it."
