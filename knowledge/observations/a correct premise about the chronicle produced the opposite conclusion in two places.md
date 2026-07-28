---
genitor: "[[observations]]"
tags: [knowledge-commons, documentation, root-cause]
date: 2026-07-26
supports: ["[[a workaround written up as a decision stops reading as a workaround]]"]
---
Two artifacts in this graph state that a chronicle entry is already a session-level synthesis, and both
conclude from it that the chronicle belongs on the *input* side of the pipeline. The generated
knowledge-graph skill: "A chronicle entry is already a session-level synthesis, so evidence is extracted
straight from the source; there is no intermediate synthesis tier in this graph." And a decision note
arguing the chronicle is a lossy fallback source tier. The premise is right in both; being a synthesis is
what makes it output, not input. The pipeline had no stage that could produce a synthesis, so the synthesis
was placed where the pipeline could reach it, and each artifact that then had to explain the arrangement
wrote it up as intentional — one of them as a recorded design decision with rationale.

## source
- [[session f64160a1 — the process pipeline correction, specced not built]]
