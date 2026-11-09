---
genitor: "[[patterns]]"
tags: [triggers, pipelines, scheduling]
---

# each stage of a staged pipeline needs its own trigger, and closing one gap exposes the next

A pipeline that moves material through stages (taken in, then consolidated, then made to steer) usually
gets a trigger for its first stage and inherits the assumption that later stages will follow. They don't.
Each stage waits on its own prompt, and a stage with none accumulates a backlog that reads as a quiet
system. Fixing one stage's trigger moves the pile to the next stage, where it is just as invisible.

*One witness (2026-11-08): promotion was scheduled; graduating questions had no trigger until that day, with 72 of
141 eligible; turning principles into rules still had none. Open.*

## evidence
- [[nothing prompted graduation because its only trigger lived in a skill promoting sessions never load]]

## related
- [[question graduation is triggered where evidence lands, from the plugin, not from the receiving graph]]
- [[build enforcement against demonstrated need, not anticipated failure]]
