---
genitor: "[[observations]]"
tags: [review, handoff, agents]
date: 2026-07-28
supports: ["[[execution against real data catches what authoring and review miss]]", "[[break the self-review chain with a different agent]]"]
---
An independent no-context cold read, briefed as an implementer, returned "no blocking items" and two real
defects — and did not notice that three passages of the spec said "this session." The phrase meant the
authoring session; a fresh implementing session would have read all three as its own and processed the
wrong transcript, completing and stamping cleanly against the wrong material. The reason the reader missed
it is structural rather than careless: it was producing a *plan*, and a deictic referent resolves fine to
anyone planning. It only misbinds at the moment a different reader executes. A review that plans cannot
surface an error whose existence depends on who is running it — the defect was found instead by the user
asking which session the plan was for.

## source
- [[session f64160a1 — the process pipeline correction, specced not built]]
