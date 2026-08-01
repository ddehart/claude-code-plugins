---
genitor: "[[observations]]"
tags: [agents, delegation, silent-failure]
date: 2026-08-01
supports: ["[[does a shared brief explain the original fanout symptom]]", "[[an index omission silently disables the check that reads it]]"]
---
**Provenance: recorded from the run itself, not from the archived transcript.** The export ends mid-run,
before this happened. Everything below was observed directly by the session that wrote it.

A `/process` inspection fanout spawned four readers, each passed `name:`, each briefed with an explicit
instruction to report in words and to say "nothing in this class" if empty. Three went idle without
reporting; one was chased with a detailed follow-up and went idle a second time. `TaskStop` resolved every
one immediately by name and reported `task_type: in_process_teammate`.

All four were then re-spawned **unnamed, with byte-identical briefs**. All four returned full structured
reports — 9, 9, 5 and 6 findings with quotes and line numbers — in two to three minutes each.

This is the discriminator the graph's open question asked for. The prior observation recorded two
competing mechanisms and said the brief could not be ruled out. Here the brief was held constant and only
the spawn shape varied, and the outcome tracked the spawn shape exactly. Passing `name:` produces an
in-process teammate whose output goes to a mailbox; omitting it produces a subagent whose final message
is the return value.

The chase cost two follow-up messages that could not have worked, and the mechanism was already recorded
in this graph — read only after the third reader went silent, and only because the failure was familiar.
