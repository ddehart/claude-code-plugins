---
genitor: "[[observations]]"
tags: [recognition, natural-language]
date: 2026-11-06
supports: ["[[a list of negating phrasings cannot be complete, so allow what may follow]]", "[[added complexity generates its own defect supply]]", "[[each fix round manufactures the next round's defects]]"]
---
To reject headings like "Deep review not due," a fix round added a lookahead of negating words. The next review pass found "— Deep review can wait" still matched, which would suppress a due review, the original bug in a narrower form. The fix named what may follow `deep review` instead, and a test case the previous round had invented with no real data behind it was dropped.
