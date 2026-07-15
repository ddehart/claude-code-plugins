---
genitor: "[[observations]]"
tags: [scaffolding, gap-detection, tooling]
date: 2026-07-15
supports: ["[[a scaffolder owns its environmental blast radius]]"]
---
Config-only wiring mode wrote a `promotes-to:` field into an existing mature graph, but that graph's
pipeline had no in-band step to act on it, so promotion could only ever fire manually — and the gap was
invisible until Derek noticed it himself. The mode's "touch no skills" contract was correct, but touching
and checking are different: it should have grepped the existing pipeline for a promotion step, found none,
and told the user, editing nothing. The fix removes the human as the detection mechanism.
