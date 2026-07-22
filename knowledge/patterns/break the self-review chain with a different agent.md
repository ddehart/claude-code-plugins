---
genitor: "[[patterns]]"
tags: [verification, review, agents]
---

# break the self-review chain with a different agent

An author auditing their own artifact agrees with their own intent, so the self-review chain only breaks
with a *different* agent (or real execution, or a human). When delegating that cold read, brief the agent
to **build** — "produce an implementation plan; can you do this without clarifying questions?" — not to
attack. A neutral "can you build this?" pass measures the spec; an adversarial "enumerate everything
wrong" pass measures the brief and will return a long list from any artifact, inflating it. Delegated
authoring gets the same discipline: fan work out to cheaper models, then verify every returned artifact
against the spec and check load-bearing factual claims directly — trust nothing on report alone.

*One witness (2026-07-15). Open.*

## evidence
- [[a neutral build-it cold read measured the spec where an adversarial loop inflated it]]
- [[subagent findings and delegated artifacts were verified against the spec, not trusted on report]]
- [[the anti-silent-loss machinery shipped four instances of the shape it was built to eliminate]] (2026-07-22)
- [[a satisfied-test asserted a property its own template did not have]] (2026-07-22)

*Qualified 2026-07-22: a different agent is necessary but not sufficient — see
[[a check inherits the frame of whoever briefed it]]. Where the author writes the reviewer's brief, the
review inherits the author's intent and scope, and cannot check either.*

## related
- [[a check inherits the frame of whoever briefed it]]
- [[execution against real data catches what authoring and review miss]]
- [[added complexity generates its own defect supply]]
