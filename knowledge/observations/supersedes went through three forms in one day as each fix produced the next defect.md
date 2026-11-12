---
genitor: "[[observations]]"
tags: [graph-patch, review]
date: 2026-11-08
supports: ["[[each fix round manufactures the next round's defects]]"]
---
A code review found that a delta's partial supersession was recorded only in a YAML comment, which the patcher had no rule to read. The fix added a `supersedes` field meaning "apply the old delta as the successor amends it". Two cleanup reviewers then found that the fix made the patcher merge two instructions and derive its own pass-fail test at runtime. The re-fix made the successor state the full end state, and that restatement introduced a stricter cadence test than the original, which no review caught and the first real patch run did. Smaller defects rode the same rounds: a sentence spliced mid-paragraph, stale counts, overlong lines.
