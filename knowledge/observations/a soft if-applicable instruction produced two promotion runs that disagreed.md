---
genitor: "[[observations]]"
tags: [prose-as-code, skills, drift]
date: 2026-07-15
supports: ["[[ambiguous prose in an LLM-executed skill is a correctness bug]]", "[[the knowledge-commons plugin generates project-owned prose, not a runtime engine]]"]
---
The promote skill said to add a date "if the target's conventions call for one." One real run added it;
another read past it — two executions of the same prose disagreeing. Separately, promote §3's phrase "its
`supports:`" bound naturally to the wrong note, exactly the misread that would break the bidirectional
edge the design rests on. Both were flagged in a change that touched "no executable code" — because a skill
is prose executed by an LLM, and optional or ambiguous wording is a drift source between sessions.
