---
genitor: "[[observations]]"
tags: [testing, prose-as-instructions]
date: 2026-11-06
supports: ["[[ambiguous prose in an LLM-executed skill is a correctness bug]]", "[[prose conventions plus human approval can replace a validator]]", "[[session-chronicle counts entries since the newest deep review, in tested code]]"]
---
session-chronicle's Step 6a told a model how to count entries since an anchor, and the anchor was wrong: any dated note reset it. The bug sat in prose, so nothing could show it failing. The fix moved the count into a script and tested it, after rejecting an eval because "an eval would test one model's reading of the prose, not the rule." This runs against the human-approval pattern, which it also supports: nobody approves a chronicle write, so the prose had no human gate to stand in for a validator.
