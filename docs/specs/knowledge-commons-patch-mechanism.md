# Spec: knowledge-commons patch mechanism (`/graph-patch`)

**Status:** Draft — not yet implemented
**Date:** 2026-07-21
**Plugin:** `knowledge-commons` (currently v0.1.8 on `main`; 0.1.9 pending in PR #65)
**Related:** [`knowledge-commons.md`](./knowledge-commons.md) (the plugin's founding spec)

## Problem

`graph-init` generates two project-owned skills from templates in the plugin: `process/SKILL.md` and
`knowledge-graph/SKILL.md`. The generator tells projects explicitly that they own these files and are
expected to sharpen them from real runs. They do, heavily.

When a template bug is fixed in the plugin, **nothing reaches the graphs already generated.** Three exist
today: `claude-code-plugins`, `wellstead`, `osu-builder-in-residence`. Neither available option works:

- **Regeneration** destroys the local prose that makes the skill useful.
- **Hand-editing** doesn't scale, and silently rots — nothing tracks which graph got which fix.

The failure shape matters: a template fix that never propagates leaves the plugin looking correct while
every downstream graph stays broken, with no mechanism that surfaces the gap. That is the same
silent-loss shape as the four bugs that motivated this work.

## Key finding: structure is stable, prose is not

Measured across all three generated `process` skills on 2026-07-21:

| Graph | Lines | `## N.` sections | Anchors match template |
|---|---|---|---|
| template | 208 | 11 | — |
| claude-code-plugins | 184 | 11 | byte-identical |
| wellstead | 332 | 11 | byte-identical |
| osu-builder-in-residence | 371 | 11 | byte-identical |

**Section headings survive generation byte-identical in every case; bodies diverge by up to 78%.**

This is the empirical basis for the whole design. Anchoring on `## N. Title` is reliable. Textual
diffing is not — the same section holds 3 example signal classes in the template and 8 domain-specific
ones in osu.

A second observation, within sections: there is usually a **stable generic spine** (the template's own
scaffolding sentences survive nearly verbatim — osu still reads "fan out one subagent per signal class…
Don't forward subagent output verbatim") wrapped in diverged domain prose. Some deltas edit the spine;
some must weave into the body. See D13.

### `knowledge-graph` anchors are weaker than `process` anchors

The table above measures `process` only. `knowledge-graph` was measured separately and behaves worse —
its headings are unnumbered, and two of twelve are unstable:

| Heading | Behavior |
|---|---|
| 10 of 12 (`## Overview`, `## Conventions`, `## Judgment Rules`, …) | byte-identical across all three |
| `## Extraction Workflow: {source-type}` | **templated** — three headings in wellstead, collapses to bare `## Extraction Workflow` in osu |
| `## Durable vs. Operational` | osu hand-edited to `## Durable versus Operational` |

This does not block v1: all seven initial deltas target `process`. It does constrain the design — see
D8's anchor field and Q1.

## Goals

- Propagate template fixes into already-generated skills without destroying local prose.
- Track what has been applied, per graph, per file.
- Make an unpropagated fix visible rather than silent.

## Non-goals

- **Restructuring a graph.** Notes, maps, atlas, and directory layout are out of scope entirely (D10).
- **Automatic delta derivation** from template diffs (D16 rejects this).
- **Patching the plugin's own skills.** `graph-init` and `promote` live in the plugin and update with it.
  Only generated, project-owned files need patching — this is why the initial batch is smaller than the
  bug count suggests (see "Initial batch").
- **Pushing.** The patcher commits; the human pushes (D12).

## Decisions

### Shape and invocation

**D1. A new `/graph-patch` skill**, alongside `graph-init` and `promote` — not a mode of `graph-init`.
*Rationale:* clean separation of concerns (init creates, promote moves claims, patch maintains), its own
trigger phrases, no flag-parsing ambiguity. `graph-init` is already 237 lines with two modes.

**D2. Pull, not push: run from inside the target project.** You are in `wellstead`, you invoke the
patcher, it reads the plugin's delta log and applies what's missing. *Rationale:* matches how
`graph-init` and `promote` already work, and approval happens where the domain context lives — you judge
a prose edit to wellstead's `process` skill while thinking about wellstead.

**D3. One delta per semantic change.** Not per version, not per file-version pair. *Rationale:* finer
approval granularity, clearer skip and conflict handling, and the log self-documents.

**D4. Approval is per delta, showing the concrete diff** against the project's actual current prose —
`y / edit / skip`. *Rationale:* this is hand-written prose; a batch approval hides exactly what needs
judgment. Slower for a 5-delta batch, correct for the material.

### State

**D5. Applied-patch state lives in a `generated:` block in `.commons.yml`.** Shape:

```yaml
generated:
  process:
    template-version: 0.1.9
    applied: [step4-explicit-negative, step9-stamp-gate, step11-pull-target]
  knowledge-graph:
    template-version: 0.1.9
    applied: [entity-proactive-recommend]
```

*Rationale:* `.commons.yml` is already the plugin's config file, already read by `promote` and
`graph-init`, and carries no risk of colliding with Claude Code's skill-frontmatter parsing. (Frontmatter
was the first proposal and was rejected: whether Claude Code tolerates an unrecognized frontmatter key is
unverified, and the design should not rest on an unverified assumption.)

**D6. Bootstrap: assume `0.1.8` and stamp on first run.** All three existing graphs were generated from
templates at 0.1.8, so this is true by construction. The patcher writes the stamp, then applies every
delta since. *Rationale:* correct for all known cases; content-probing is real complexity for a
population of zero older graphs.

**D7. `graph-init` must write the `generated:` block at generation time** from now on, so freshly
generated graphs never need the D6 bootstrap. This is a change to `graph-init`, not just `graph-patch`.

*Conflict to resolve when implementing:* `graph-init`'s **Never** section currently reads *"Never invent
`.commons.yml` keys beyond `graph:`, `types:`, `sources:`, `sinks:`, `promotes-to:`."* D5 adds a sixth.
That bullet must be amended to sanction `generated:` explicitly — otherwise the generator is instructed
not to write the block D7 requires.

### Delta format

**D8. Each delta entry is rich**, carrying:

| Field | Purpose |
|---|---|
| `id` | Stable kebab-case identifier, recorded in `applied:` |
| `file` | `process` or `knowledge-graph` |
| `anchor` | The **exact `##` heading text** it targets — not a pattern, not a number. `## N. Title` for `process`; bare heading text for `knowledge-graph`, where numbering doesn't exist and two headings are unstable |
| `version` | Plugin version that introduced it |
| `instruction` | The semantic change, in domain-neutral terms |
| `rationale` | *Why* — lets the agent adapt the edit to diverged prose instead of pasting |
| `satisfied-test` | An explicit test for "does the target already say this?" |

*Rationale:* the instruction alone is not enough when the target has diverged 78%. The rationale is what
lets an agent write the change in the project's own voice. The `satisfied-test` is load-bearing twice
over — see D9 and D14.

**D9. The patcher judges redundancy before proposing.** Read the target section; if the
`satisfied-test` already passes, report *already satisfied*, record the delta as applied, and propose no
edit. *Rationale:* a project may have hand-fixed the same defect. Consistent with the explicit-negatives
principle the initial batch is about.

**D10. Scope: the two generated skills only** — `process/SKILL.md` and `knowledge-graph/SKILL.md`. The
`.commons.yml` `generated:` block is written as bookkeeping, not as a patchable target. Notes, maps,
atlas, and scaffold structure are never touched. *Rationale:* covers the entire pending batch; a patcher
that can restructure a live graph is a materially different risk class.

**D11. Discovery: `/process` reports pending patches, and manual invocation always works.** Step 10 of
`process` already says to suggest out-of-plan actions in the report rather than auto-running them — a
pending-patch line fits that idiom exactly. *Rationale:* you find out during work you were already doing,
without coupling maintenance to processing.

**D12. The patcher commits but never pushes.** Name the paths explicitly (never blanket-stage),
conventional-commit message citing the applied delta ids. *Rationale:* the push decision stays with the
human because these are project repos with their own PR conventions, and because a patch run edits prose
the project wrote by hand. Note this **deliberately diverges from `promote` §6**, which commits *and*
pushes — `promote`'s reasoning (an uncommitted promotion is invisible to every other machine, so the
cross-domain chain dies in a working tree) does not apply here: a patch is local maintenance, not a
contribution other machines are waiting on.

### Application semantics

**D13. Body-weaving deltas use the same flow as spine deltas.** The `instruction` names the insertion
point in domain terms — *"add an entity signal class alongside this graph's existing classes in step
4"* — and the agent writes it in the project's own voice and vocabulary. *Rationale:* the entity delta is
one of the pending batch; deferring body edits to manual handling would mean v1 delivers a minority of
its own batch. The per-delta approval (D4) is where a bad weave gets caught.

**D14. Verification: re-run the `satisfied-test` as a post-condition.** The same test that answered "is
this already present?" before the edit answers "did it land?" after. *Rationale:* one artifact serving
both directions. Given the initial batch is entirely about failures that are indistinguishable from
success, the patcher must not have that failure mode itself.

**D15. Partial failure: continue, collect, report together.** Skip the failing delta, apply the rest,
report every failure at the end with enough detail to retry. **Stamp only what actually applied.**
*Rationale:* mirrors `process` step 8's continue-and-collect — the plugin already has this idiom and the
patcher should not invent a second one.

**D16. A missing anchor is skipped, reported loudly, and never stamped.** Do not attempt semantic
relocation. *Rationale:* guessing where content "moved to" is where a patcher would do real damage to
hand-written prose, and there are real cases where an anchor legitimately doesn't exist: osu renamed
`## Durable vs. Operational`, and `## Extraction Workflow: {source-type}` resolves to a different heading
in every graph. D16 is what makes the weaker `knowledge-graph` anchoring safe rather than destructive —
a delta that can't find its target does nothing, loudly, instead of landing somewhere plausible.

*(An earlier draft justified this with "graph-init omits section 11 for a graph with no `promotes-to:`."
That case has a population of zero: the only sourceless graph is the commons, which gets no `process`
skill at all. The rule stands; that illustration didn't.)*

### Resolved during implementation (PR #66)

The spec was silent on these five; they were settled while building `/graph-patch` and are recorded here
so they aren't re-derived.

**D18. An ambiguous anchor is treated exactly like a missing one** — skip, report loudly, never stamp.
D16 covered *missing* only, but multi-match is live for `knowledge-graph` (wellstead has three
`## Extraction Workflow: …` headings). Same rationale: a patcher that picks among candidates is guessing.

**D19. `template-version` on a partial run** is set to the highest `version` among deltas actually
stamped *for that file*, and left untouched if nothing stamped. `applied:` is the source of truth;
`template-version` is a convenience. Because selection is set-membership on `id` (D15), legitimate holes
below the version number can exist — the skill states this explicitly so a reader doesn't treat the
version as a completeness claim.

**D20. A missing target file is not an error.** A commons graph has no `process` skill at all, so its
`process` deltas are simply out of scope for that project. Report it, don't stamp it, don't treat it as
failure.

**D21. A reader-modified `edit` still runs the D14 post-condition.** A hand-edited weave is at least as
likely to miss the satisfied-test as a generated one.

**D22. The bootstrap stamp is written to disk before the first edit.** D6 said "writes the stamp, then
applies" without pinning ordering; making it explicit means a crashed or interrupted run still leaves
honest state rather than edits with no record.

### Keeping the log honest

**D17. A template edit is incomplete without its delta entry.** Stated as a rule in the plugin README and
the repo's `CLAUDE.md`, next to the existing mandatory version-bump rule. *Rationale:* same enforcement
model already used for version bumps — stated as non-optional, applied by whoever edits, costs nothing to
build. A forgotten delta reproduces the exact failure this mechanism exists to prevent.

## The delta log

Lives at `plugins/knowledge-commons/references/deltas.md` — a prose-and-YAML document in the same idiom
as the rest of the plugin's references. Entries are append-only and ordered by version.

Sketch of one entry:

```yaml
- id: step4-explicit-negative
  file: process
  anchor: "## 4. Inspect"
  version: 0.1.10
  instruction: >
    A signal-class subagent that returns nothing is an error condition to chase, never a null
    result to accept. Require an explicit "nothing in this class" statement before recording a
    class as empty; silence is not that statement. Route a non-reporting reader into the
    continue-and-collect path so it surfaces in the run report.
  rationale: >
    On the first real /process run, all four signal-class subagents completed their reads and went
    idle without volunteering findings — four of four, so it is a property of the fanout, not a
    fluke. A run reading silence as "nothing found" would assemble a plan from zero findings and
    stamp the source processed, permanently marking the session handled. The four readers had
    actually produced 3 patterns and 9 observations.
  satisfied-test: >
    Does the section state that a non-reporting or silent subagent is an error to chase rather
    than an empty result?
```

## Initial batch

**Important:** only *generated* files need deltas. Fixes to `graph-init` and `promote` are plugin skills
and propagate on plugin update. Of the four Todoist-tracked bugs, the two `graph-init` bugs need no delta
(shipped in PR #65), and issue 4's `promote` changes need no delta — only its `process` step 11 change
does.

| # | id | File | Anchor | Source |
|---|---|---|---|---|
| 1 | `step4-explicit-negative` | process | `## 4. Inspect` | Issue 3 |
| 2 | `step8-collect-nonreporting` | process | `## 8. Continue-and-collect` | Issue 3 |
| 3 | `step9-stamp-gate` | process | `## 9. Stamp` | Issue 3 |
| 4 | `step11-pull-target` | process | `## 11. The promotion tail` | Issue 4 |
| 5 | `step4-entity-signal-class` | process | `## 4. Inspect` | Entity proactivity |
| 6 | `step5-entity-recommend` | process | `## 5. Propose the plan` | Entity proactivity |
| 7 | `step10-pending-patches` | process | `## 10. Report` | D11 (this spec) |

Delta 7 is self-referential and easy to miss: D11 requires editing the `process` template to surface
pending patches in the run report. That edit is itself a template change, so by D17 it needs its own
delta. It ships in PR 4 alongside the mechanism.

Deltas 5 and 6 may also warrant a `knowledge-graph` counterpart — to be settled when that template change
is written (see Q1).

> **Superseded 2026-07-22 (plugin 0.5.0).** Deltas 5 and 6 were built at the wrong layer of abstraction:
> they recommended entity *notes* for individual un-noted nouns, where the request was for new entity
> *types* — entries in `.commons.yml`'s `entity:` list. Both were removed from the log rather than
> superseded within it, which the append-only convention permits here only because no graph had recorded
> them as applied (no live `.commons.yml` carried a `generated:` block, so nothing downstream was stamped).
> They are replaced by a single entry, `step10-entity-type-gap` (`## 10. Report`, version 0.5.0), which is
> deliberately *not* conditional on the graph already declaring an entity type. The table above is left as
> the record of the initial batch as it shipped.

All seven target `process`, which is the file with fully stable anchors. That is fortunate rather than
designed; Q1 is where it stops being true.

## Execution plan

*Revised 2026-07-21 to match what actually shipped. The original plan put the delta log **file** in PR 4
while assigning its **entries** to PRs 2 and 3 — those can't both be true, since an entry needs a file to
live in. Execution resolved it by creating `deltas.md` in the PR that authored the first entries. Also:
PRs 2 and 3 merged into one, because both edit `templates/process.md` step 4 and splitting them across
parallel agents guaranteed a collision.*

1. **PR #65** (0.1.9, patch) — `graph-init` fixes: commons discovery and the Q9 drop. No deltas —
   `graph-init` is a plugin skill and propagates on plugin update. Also carries D7's one-line Never-section
   amendment sanctioning the `generated:` key, pulled forward because leaving it out ships a plugin whose
   `graph-init` forbids the key `/graph-patch` writes.
2. **PR #67** (0.2.0, minor) — template fixes for issues 3 and 4, `promote` changes, the entity
   proactivity behavior, **and `references/deltas.md` itself** carrying deltas 1–6. Minor rather than
   patch because the entity change is new behavior.
3. **PR #66** (0.3.0, minor) — the `/graph-patch` skill, `.claude/rules/template-deltas.md`, README.
   **Blocked on #67**: the skill reads `deltas.md`, which doesn't exist until #67 lands.
4. **Follow-up PR** — the rest of D7 (`graph-init` writes the `generated:` block at generation time) and
   delta 7 (`process` step 10 discovery hook, per D11). Deferred because both touch files that were in
   flight; **currently owned by no open PR**, so D11 — the spec's own answer to "make an unpropagated fix
   visible rather than silent" — is unimplemented until this lands.
5. **Apply** — run `/graph-patch` in `claude-code-plugins`, `wellstead`, and
   `osu-builder-in-residence`. This is also the mechanism's first real test.

Merge order is **#65 → #67 → #66**, matching the version sequence. Nothing enforces it mechanically, so
merging #66 early would ship an inert skill with dead README links and make #67's 0.2.0 a version
regression.

#67 is inert until #66 ships. That ordering is deliberate: it means the patcher was designed against six
real deltas rather than a speculative one.

**D17 placement diverged from the spec.** D17 said the rule goes in the plugin README and the repo's
`CLAUDE.md`. It shipped in the README and a new `.claude/rules/template-deltas.md` instead, with
`CLAUDE.md` untouched — the rules directory is the better home given the sibling `plugin-updates.md`, and
per the documentation taxonomy behavioral steering belongs in rules rather than in an index file.
Recorded here rather than silently absorbed.

## Risks and open questions

**R1. The patcher is itself an unverified agent editing prose.** D14's post-condition test is the
mitigation, but a locally-correct edit can still contradict a nearby paragraph the project wrote. The
per-delta diff is the human's only defense. *Consider:* whether the patcher should re-read the full file
after a run and report coherence concerns, beyond the per-delta post-condition.

**R2. `satisfied-test` quality determines whether D9 and D14 work at all.** A vague test makes redundancy
detection and verification both unreliable. There is no mechanism proposed to keep tests sharp beyond
author discipline.

**R3. D17 rests on discipline, and discipline is what failed in the four originating bugs.** The
mechanical alternative (drift detection: compare the template against the last version with delta
coverage, report uncovered changes) was considered and not taken. If a delta is missed in practice, that
is the escalation.

**Q1. Does the entity change need a `knowledge-graph` delta as well as the `process` ones?** The
reactive entity rule currently lives in both templates (`knowledge-graph` step 6 of its per-observation
workflow). Settle when writing PR 3 — and note the constraint: the natural anchor there is
`## Extraction Workflow: {source-type}`, which is exactly one of the two unstable headings. A delta
targeting it would resolve in `claude-code-plugins`, miss in `osu` (renamed to bare `## Extraction
Workflow`), and be ambiguous in `wellstead` (three such headings). If PR 3 needs that anchor, the
mechanism needs a story for multi-match and near-match before it can carry it.

**Q2. Delta ids are hand-authored and must be globally unique forever.** No collision check is proposed.
Low risk at current scale; worth a thought if the log grows past a few dozen entries.

**Q3. What happens when a project has deliberately removed a section?** D16 says skip-and-report, and
never stamp. That means the same delta is reported as unapplied on every subsequent run, forever. A
"declined permanently" state may be worth adding if this proves noisy. **Still open, and now live** —
`/graph-patch` (PR #66) reports this correctly but has no declined state. The three-graph rollout is the
trigger: if it proves noisy there, add one.
