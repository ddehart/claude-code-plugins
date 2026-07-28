---
genitor: "[[observations]]"
tags: [agents, delegation, silent-failure]
date: 2026-07-28
supports: ["[[does a shared brief explain the original fanout symptom]]", "[[naming a failure shape confers no immunity to it]]"]
---
Passing `name:` to the Agent tool produces an in-process teammate whose output goes to a mailbox; omitting
it produces a subagent whose final message is the return value. The same brief — "your final message is the
deliverable" — is true for the second and false for the first. A named cold-read agent went idle four times,
ignored two follow-ups and an explicit stand-down, and was invisible to `TaskList` while `TaskStop`
resolved it by name immediately. An unnamed re-spawn with the same brief returned a full report in about
two minutes; four unnamed inspection readers later reported unprompted, the first fanout in this graph to
do so. This is the mechanism behind the earlier four-silent-readers episode, which was already diagnosed as
a briefing error: the brief was wrong only for one spawn shape, and the parameter that selects the shape
looks like a label. Talking to the stalled agent never worked; terminating it did.

## source
- [[session f64160a1 — the process pipeline correction, specced not built]]
