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

## still open (2026-07-28) — two competing mechanisms, one discriminator

**This section was first written as an answer and retracted the same day.** It claimed the cause is the
*spawn shape*: `name:` on the Agent tool produces an in-process teammate delivering through a mailbox, so
"your final message is the deliverable" reaches nobody, while an unnamed subagent's final message *is* the
return value. Evidence from `session:f64160a1`, same instruction throughout — one named agent idle four
times through two follow-ups and a stand-down; an unnamed re-spawn reporting in ~2 minutes; four unnamed
readers all reporting unprompted.

Retracted on reading the commons, where a claim promoted from **osu-builders-studio** the same day reports
the opposite base rate: *"forty-three of forty-four workers finished holding findings and volunteered none
of them, under four different briefs and two task shapes."* If a meaningful share of those 44 were plain
unnamed subagents, the spawn-shape mechanism is wrong — and n=1 named against n=5 unnamed, inside one
session, was never enough to settle it. The retracted answer is itself an instance of
[[a plausible story arrests the investigation before the mechanism is found]], written by the same run that
recorded three others.

**The discriminator:** were osu-builders-studio's 43 silent workers named teammates or plain subagents?
That is checkable in that project's transcripts and settles between the two mechanisms. Until it is
checked, neither the delta's fanout rationale nor the spawn-shape account is established.

The instruction stands under either — requiring an explicit negative is right regardless of why silence
occurs. Only the stated reason is in question, and a correction still requires a superseding delta rather
than an in-place rewrite.

## evidence
- [[an unnamed subagent returns its report where a named teammate delivers it nowhere]]

## related
- [[justifying prose drifts from the thing it justifies]]
- [[a plausible story arrests the investigation before the mechanism is found]]
- [[named readers went silent while unnamed re-spawns with identical briefs all reported]]
