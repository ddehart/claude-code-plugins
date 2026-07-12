---
name: process
description: >
  Refine source artifacts — session chronicles, call transcripts, documents — into an attractor-linked
  knowledge graph, routing typed outputs to their sinks. A ledgered pipeline: inspect the queue, propose a
  concrete plan, take one approval, run to completion, stamp each source, report. Use when asked to process
  session records or chronicles, refine sources into the graph, run the commons pipeline, or catch the graph
  up on new material. Supports --dry-run (propose only, no writes) and --augment (reprocess for what's new).
argument-hint: "[source-path] [--augment] [--dry-run]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "AskUserQuestion", "Agent", "Skill"]
---

# Process

The orchestrator. Capture happens as a **byproduct of work**, never as a separate act of authorship — the
trigger is *a thing existing*, not a person remembering.

The flow, and it does not vary:

**inspect → propose plan → single approval → run to completion → stamp → report**

Read the contract before starting:

- `${CLAUDE_PLUGIN_ROOT}/references/mechanism.md` — roles, the invariant, the boundary, graduation
- `${CLAUDE_PLUGIN_ROOT}/references/note-formats.md` — what the proposed notes will look like
- `${CLAUDE_PLUGIN_ROOT}/references/commons-yml.md` — config schema, including the ledger stamp

The human's role in a healthy run is **one plan approval**. If runs routinely turn into editing sessions,
that is the signal the proposals are bad — not that the human should settle in and edit. Say so.

## Step 1: Load the config

Find `.commons.yml` (cwd, then the graph root). **Absent → stop.** Report it and point at `/commons-init`.
Do not improvise a graph layout, invent type names, or guess at sinks.

Resolve role → type name → directory. The graph may call its evidence `insight` and its attractors
`opportunity`; never assume the personal-commons names.

## Step 2: Inspect

**Enumerate the queue.** For each source tier in `sources:`, glob its `path` and read the ledger stamp
(`processed:` frontmatter on the source, or the sidecar — per the tier's `ledger:` setting).

- No stamp → unprocessed. Queue it.
- Stamped, all classes `ran` → skip, unless `--augment`.
- Stamped with any class `errored` → **queue it**; resume that class only. This is what the per-class stamp
  is for.
- `--augment` → reprocess, proposing only what is *new* relative to what the graph already holds.

**Resolve each source to readable text.** If the tier declares `resolve-via:`, invoke that edge skill (see
*Edge-skill discovery* below). If it is `null`, the artifact is already readable — just read it.

**Adapt to input size.** Read short sources inline. For long ones (a full transcript, a month of
chronicles), **fan out subagents by signal class** — one pass looking for claims, one for tasks, one for
lifecycle transitions — so each reads the whole source with a single question in mind. A single pass looking
for everything finds the obvious and misses the rest.

**Read the full `index.md` into context.** This is not optional and it is not bookkeeping: holding the new
material and the entire distilled corpus *simultaneously* is the condition that makes cross-domain
association possible at all. It is the reason this step happens here, in the session that is paid to look,
rather than being left to a future session that would have to already know the connection exists to find it.

Also run the `commons-check` skill, so its flags (graduations earned, staleness, orphans) can be folded into
the plan as proposed transitions.

## Step 3: Propose the plan

One concrete, reviewable plan. The human reads this and says yes once — so it must be specific enough that
"yes" is a real decision, not a shrug.

For each source, propose:

- **Evidence notes** — title, the one-line substance, and **which attractors each supports**. An evidence
  note with no attractor is not proposable; either find its attractor, propose a new one, or drop it.
- **New attractors** — title and the `## so what` clause. Proposing a new attractor is a bigger deal than
  proposing a claim; it should be rare, and the plan should show why the existing attractors don't fit.
- **Lifecycle transitions to apply**, from `commons-check`'s flags. State the evidence: *"principle X now
  has evidence from devbox and wellstead → graduates to `held`."*
- **Dispatch items** — tasks and tracker updates, with their sink and the defaults that will be applied.
- **What is skipped, and why.** Silence is not a skip. Every source in the queue that produces nothing gets
  a line saying so.

Then, two things that only this step can surface:

- **Cross-domain connections.** *"This is the third domain where this pattern has appeared — it graduates."*
  This is the payoff of holding the index and the new material at once. Surface it explicitly, by name.
- **Steering-grade principles.** The few principles that ought to change how sessions *behave* are
  candidates for the always-loaded instruction tier (e.g. `~/.claude/rules/`). Flag them as candidates —
  promotion out is a decision, and it goes in the plan like everything else.

## Step 4: One approval gate

Present the plan. Take **one** approval for the whole thing.

Then **run to completion.** Pause mid-run *only* on:

- **Genuine ambiguity** the plan did not resolve, or
- **Conflict with the existing record** — the new material contradicts an attractor the graph already holds.
  That is not an error to route around; it is the most interesting thing that can happen. Surface it.

Do not pause to re-confirm things the plan already covered. The plan approval *was* the confirmation, and a
pipeline that re-asks is a pipeline the human learns to click through.

## Step 5: Run

**Delegate every graph write to the `knowledge-graph` skill.** Do not write graph notes directly — that
skill owns the invariant enforcement, and routing around it is how orphan evidence gets in.

**Route each dispatch class to its configured edge skill.** Dispatch outputs (tasks, tracker updates) never
become graph notes: they are extracted, routed with their configured `defaults` folded in, and recorded in
the stamp.

**Approval semantics are heterogeneous by design.** A graph write and a tracker mutation do not deserve the
same gate:

| `approval:` | Behavior |
|---|---|
| `plan` (default) | Covered by the Step 4 approval. Just run. |
| `per-item` | Confirm each item interactively before dispatch. |
| `field-level` | Confirm individual fields before writing them. |

**Continue-and-collect on failure.** A failing output class does not abort the run: mark it `errored`,
carry on with the rest, and report every failure together at the end. Failures are **never silently
swallowed** — an error that vanishes is worse than one that stops the run, because the graph then silently
disagrees with reality.

### The boundary gate

For a `professional` posture, or **any** promotion across a domain boundary, all three layers — none
sufficient alone (see `mechanism.md`):

1. **Mechanical** — no wikilink resolves outside the target graph. `knowledge-graph` enforces this at write.
2. **LLM review** — three questions, **three noes required**: Does this name or identify any person,
   organization, or client? Does it disclose any fact specific to one engagement? Would it remain true and
   useful if every party involved vanished?
3. **Human approval** — explicit, per promotion. **Non-negotiable.** Not covered by the plan approval; this
   one is asked separately, every time.

A promoted note is **newly written and self-contained**, carrying only portable substance, with `domain:` as
non-resolving provenance. It is never the original note moved. *If it needs its source to make sense, it has
not generalized* — do not promote it; say why.

## Step 6: Stamp

Write the ledger stamp to each processed source — **per output class**:

```yaml
processed:
  date: 2026-07-12
  claim: ran
  principle: ran
  task: errored
```

This is what makes the queue enumerable and re-runs idempotent: nothing silently evaporates, and a re-run
resumes the errored class instead of redoing the whole source.

Skip stamping entirely on `--dry-run`.

## Step 7: Report

- What was written to the graph, and where.
- What was routed to which sink.
- **What failed** — collected, with the actual errors.
- **Cross-domain connections found.**
- **Graduation candidates** and steering-grade principles flagged for the instruction tier.

## Edge-skill discovery

Config **names** edge skills (`resolve-via:`, `via:`); it never contains their procedure. Match those names
against the **live skill list available in this session, at runtime.**

**Never work from a hardcoded catalog of edge skills.** The set of them is open, project-owned, and expected
to drift — a catalog in this file would be wrong the first time a project adds a sink.

**If a named edge skill is missing:** do **not** improvise the procedure. Writing to someone's task manager
or tracker by guessing at its interface is exactly the kind of confident wrongness that costs trust.
Instead:

1. Report the gap in the plan.
2. Mark that output class **skipped-with-reason** in the stamp.
3. Continue with every other class — continue-and-collect.
4. Point at `/commons-init`, which stubs missing edge skills.

## `--dry-run`

Inspect and propose. **No writes, no stamp, no dispatch.** Print the plan and stop.

This is the mode that makes the plugin's own acceptance test possible: feed it a source the incumbent
workflow already processed, and compare the proposed plan against what the incumbent produced. Anything the
generalization dropped shows up immediately, with nothing at risk.
