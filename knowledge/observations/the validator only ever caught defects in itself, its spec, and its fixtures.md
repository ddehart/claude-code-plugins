---
genitor: "[[observations]]"
tags: [validation, anti-pattern]
date: 2026-07-15
supports: ["[[added complexity generates its own defect supply]]", "[[prose conventions plus human approval can replace a validator]]"]
---
Across its entire life the executable validator caught defects only in itself, its spec, and its
hand-built fixtures — never in real graph content. The ledger saga was emblematic: an invented file-level
stamp created an append problem, which spawned two new fields, which created self-match bugs, which took
three fix rounds, all later deleted. Building the validator PR surfaced seven defects, every one of them in
the validation apparatus itself. The machinery was generating its own defect supply, and each catch was
mis-scored as "validation working."
