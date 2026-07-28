---
genitor: "[[questions]]"
tags: [agents, delegation, rationale]
---

# does a shared brief explain the original fanout symptom

The shipped delta `step4-explicit-negative` states as its rationale that "all four signal-class subagents
completed their reads and went idle without volunteering findings... Four out of four — a property of the
fanout, not a fluke."

That inference does not follow. Those four readers shared one orchestrator and one briefing template, so
four identical outcomes are exactly as consistent with *the brief caused it* as with *the fanout causes
it*. N=4 is not four independent trials. The rationale asserts a mechanism its own cited evidence cannot
isolate, and treats ruling out chance as though it identified a cause.

**What would settle it:** read the four original briefs. If they specified a reply channel that could not
reach the orchestrator, the symptom has a mundane explanation and the delta's rationale names the wrong
mechanism.

The instruction is sound either way — requiring an explicit negative is right regardless of why silence
occurs. Only the stated reason is in question.

**Why it matters practically:** the delta is applied and stamped in this graph and pending for two others,
so its rationale has already propagated. Unlike the entity deltas removed in v0.5.0, durable stamped state
now exists, so the in-place-replacement exception does not apply — a correction requires a superseding
delta.

*Opened 2026-07-22. No evidence either way; the deciding artifact was not part of this session's record.*

## answer (2026-07-28) — ready to graduate

Yes, and the mechanism is sharper than "a shared brief." The brief was not wrong in general; it was wrong
for **one spawn shape**. `name:` on the Agent tool produces an in-process teammate that delivers through a
mailbox, so "your final message is the deliverable" reaches nobody. Without `name:`, the final message *is*
the return value and the same sentence is correct.

A near-controlled comparison ran in `session:f64160a1`, same instruction throughout: one named agent went
idle four times and ignored two follow-ups and a stand-down; an unnamed re-spawn returned a full report in
~2 minutes; four unnamed readers then all reported unprompted — the first fanout in this graph to do so.

So the delta's rationale names the wrong mechanism: the fanout is not the cause, and the count of four was
never the evidence it was read as. Per the note below, correcting it requires a superseding delta, since
`step4-explicit-negative` is stamped here and pending in two other graphs. The instruction stands
regardless.

## evidence
- [[an unnamed subagent returns its report where a named teammate delivers it nowhere]]

## related
- [[justifying prose drifts from the thing it justifies]]
- [[a plausible story arrests the investigation before the mechanism is found]]
