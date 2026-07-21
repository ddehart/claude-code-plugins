# Template deltas

`graph-init` generates two project-owned skills from the templates in `references/templates/`:
`process/SKILL.md` and `knowledge-graph/SKILL.md`. Projects own those files and are told to sharpen them
from real runs, which they do — measured across the three graphs generated so far, section bodies diverge
by up to 78% while the `## N. Title` headings survive byte-identical. That is what this log is for:
regenerating a graph would destroy the local prose, and hand-editing three graphs doesn't scale and rots
silently. A delta describes a template fix in terms an agent can re-apply *into* diverged prose, in the
project's own voice, rather than as text to paste.

**A template edit is incomplete without its delta entry.** This sits alongside the mandatory version-bump
rule and works the same way: stated as non-optional, applied by whoever makes the edit. A template fix
with no delta leaves the plugin looking correct while every already-generated graph stays broken, with
nothing that surfaces the gap — which is the same silent-loss shape most of these deltas were written to
fix.

Only **generated** files need deltas. Fixes to `graph-init` and `promote` live in the plugin and reach
every project on plugin update; they must not appear here.

## The seven fields

| Field | Purpose |
|---|---|
| `id` | Stable kebab-case identifier. Recorded in the project's `.commons.yml` `applied:` list, so it can never be renamed once shipped. |
| `file` | `process` or `knowledge-graph`. |
| `anchor` | The **exact `##` heading text** the change targets — not a pattern, not a section number. A delta whose anchor doesn't resolve is skipped and reported loudly, never relocated by guess. |
| `version` | The plugin version that introduced the delta. |
| `instruction` | The semantic change, in domain-neutral terms. What must be true of the section afterward — not the words to insert. |
| `rationale` | *Why* the change exists, including how the defect was found. This is what lets an agent adapt the edit to prose that has diverged from the template instead of pasting into it. |
| `satisfied-test` | An explicit test for "does the target section already say this?" |

**Write the `satisfied-test` carefully.** It is load-bearing in both directions: the patcher runs it
*before* proposing, so a project that already hand-fixed the defect is reported as satisfied rather than
edited twice; and it runs *again* after the edit as the post-condition proving the change landed. A vague
test breaks both at once, and it breaks them quietly — redundancy detection starts producing duplicate
edits, and verification starts passing on edits that did nothing. Make it a question an agent reading an
unfamiliar, heavily-rewritten version of that section can answer reliably, about substance rather than
wording.

Entries are append-only and ordered by version.

## Entries

```yaml
- id: step4-explicit-negative
  file: process
  anchor: "## 4. Inspect"
  version: 0.2.0
  instruction: >
    A signal-class subagent that returns nothing is an error condition to chase, never a null
    result to accept. Require an explicit "nothing in this class" statement, from that reader
    about that class, before recording the class as empty; silence, an empty message, and a
    reader that simply stopped are none of them that statement. Follow up to get the findings,
    and if the reader still won't report, treat the class as failed rather than empty and route
    it into the continue-and-collect step.
  rationale: >
    On the first real /process run, all four signal-class subagents completed their reads and went
    idle without volunteering findings — four of four, so it is a property of the fanout, not a
    fluke. Each needed an explicit follow-up before reporting. A run reading that silence as
    "nothing found" would assemble a plan from zero findings, write the source note, stamp it
    processed with an empty ran: list, and report a clean sweep — and because the stamp is what
    makes re-runs resume instead of redo, the source would be permanently marked handled. The
    failure mode is indistinguishable from a successful run. The four readers had actually
    produced 3 patterns and 9 observations, including three divergences between the session's
    self-account and what the transcript showed.
  satisfied-test: >
    Does the section state that a silent or non-reporting subagent is an error to chase rather
    than an empty result, and require an explicit statement of "nothing found" from the reader
    before a class may be recorded as empty?

- id: step8-collect-nonreporting
  file: process
  anchor: "## 8. Continue-and-collect"
  version: 0.2.0
  instruction: >
    A signal-class reader that never reported is a failure collected and reported by this step,
    even though it failed before the plan existed. Name it under its class name, state plainly
    that the class was never inspected, and offer the re-read alongside the other retries.
  rationale: >
    Companion to step4-explicit-negative. Step 4 makes a silent reader an error; this is where
    the error has to surface, or the run's report says nothing went wrong. It is the one failure
    with no error message attached to it, so a collect step that only gathers steps which threw
    will never mention it — leaving the report indistinguishable from a clean run, which is the
    exact defect being fixed.
  satisfied-test: >
    Does the section route a non-reporting or silent signal-class reader into the collected
    failure report, naming the class and saying it was never inspected?

- id: step9-stamp-gate
  file: process
  anchor: "## 9. Stamp"
  version: 0.2.0
  instruction: >
    Gate the processed: stamp on inspection coverage. Refuse to write it while any signal class
    handed to a subagent has neither returned findings nor explicitly reported none. Instead,
    withhold the stamp, name the unaccounted-for classes, and offer the re-read. Scope the gate to
    the fanout path explicitly: on an inline read there are no readers to hear from and every class
    was inspected in-conversation, so an unscoped gate would withhold the stamp on a complete run.
  rationale: >
    The stamp is what makes re-runs resume instead of redo, so writing one marks the source
    handled for good — the next run reads it and moves on. Stamping over a class that was never
    inspected discards that part of the input silently and permanently. The gate is the last
    point at which the silent-reader failure is still recoverable: an unstamped partial run can
    be re-run, a complete-looking stamp over an uninspected class cannot be distinguished from a
    finished one afterward.
  satisfied-test: >
    Does the section make writing the stamp conditional on every fanned-out signal class having
    either reported findings or explicitly reported none, and say what to do instead when one has
    not — while leaving an inline read, where no subagent was involved, free to stamp normally?

- id: step11-pull-target
  file: process
  anchor: "## 11. The promotion tail"
  version: 0.2.0
  instruction: >
    Refresh the promotion target before the screen runs — not after candidates are derived. If
    the target is a git repo with a remote, fetch and fast-forward, and say what came in, since
    new claims in the target change the screen's answer. Degrade explicitly: with no remote, no
    network, no git, a fetch error, or a fetch that returns cleanly while the fast-forward is
    refused (diverged local copy, dirty tree), the screen still runs, but state that it ran
    against a possibly-stale copy rather than letting silence imply the target is current. The
    check is that the fast-forward happened, not that the fetch returned.
  rationale: >
    Found while promoting five claims into the personal commons. The "not already steering"
    screen reads the target graph from the local working copy without fetching; against a stale
    copy it cannot see recent claims, so duplicates read as novel. Redundancy detection is the
    screen's entire job, so a stale copy makes it decorative while it still reports clean. The
    ordering is the substance of the fix: the screen runs before the plan is presented, so a
    refresh that happens after candidates are derived is too late to change what they were
    screened against.
  satisfied-test: >
    Does the section require refreshing the target graph from its remote before the redundancy
    screen runs, and require saying so explicitly whenever the copy did not reach the remote's
    tip — including when a fetch succeeds but the fast-forward is refused?

- id: step4-entity-signal-class
  file: process
  anchor: "## 4. Inspect"
  version: 0.2.0
  instruction: >
    APPLIES ONLY IF this graph declares an entity type in .commons.yml. The entity tier is
    optional — a graph whose interview answered "none" has no entity type, no scaffolded entity
    directory, and no map to enter one in. For such a graph this delta does not apply: report it
    as not applicable and propose no edit.
    Where it does apply: make entity recognition a first-class inspection concern: named nouns
    this graph tracks that have no entity note yet are a finding in their own right, not a side
    effect of writing an observation that mentions one. Both the inline-read path and the
    subagent-fanout path look for them, and both carry the mention count forward to the plan. Add
    an unnamed-entities class to this graph's signal-class list, phrased in the domain's own
    vocabulary for the nouns it tracks.
  rationale: >
    Entity creation was reactive and conditional — the only rule anywhere was "if the entry names
    a plugin or skill not yet in entities/, add a lookup-only entity note," buried as one step of
    the sibling knowledge-graph skill's per-observation workflow. It fired only as a side effect
    of writing an observation that happened to mention a noun. With no entity signal class,
    inspection had no way to treat a named noun the graph keeps returning to as a finding at all,
    so an entity clearly worth a note but with nothing attaching to it was invisible to the run.
    The mention count is what lets the plan make the case at step 5.
  satisfied-test: >
    First, does this graph declare an entity type in .commons.yml? If not, the delta is not
    applicable and the section is correct as it stands. If it does: does inspection treat unnamed
    entities — nouns the graph tracks with no entity note yet — as a signal class of their own,
    found on both the inline and fanout paths, independently of whether any observation in the
    run attaches to them?

- id: step5-entity-recommend
  file: process
  anchor: "## 5. Propose the plan"
  version: 0.2.0
  instruction: >
    APPLIES ONLY IF this graph declares an entity type in .commons.yml — same applicability test
    as step4-entity-signal-class, and the two travel together: apply both or neither. For a graph
    with no entity tier, report not applicable and propose no edit; a plan that recommends
    entities there proposes writes into a directory that was never scaffolded.
    Where it applies: the plan surfaces entity recommendations as their own line items — naming
    the noun, its mention count for this run, and that it has no entity note yet — rather than
    folding them into the notes that mention them. Shape: "this run named X and Y four times
    each; neither has an entity note; create them?"
  rationale: >
    Companion to step4-entity-signal-class: step 4 finds the entity, step 5 is where the human
    gets to approve it. Without an explicit line item, an entity that plainly warrants a note but
    has no observation attaching to it never reaches the approval gate, so the finding is
    discarded at exactly the point it was supposed to become actionable. The count is what makes
    the case reviewable — the reader judges from the evidence rather than from an assertion.
  satisfied-test: >
    First, does this graph declare an entity type in .commons.yml? If not, the delta is not
    applicable and the section is correct as it stands. If it does: does the plan present entity
    recommendations as explicit, separately-approvable line items carrying the mention count,
    rather than as a consequence of the observations being written?

- id: step10-pending-patches
  file: process
  anchor: "## 10. Report"
  version: 0.4.0
  instruction: >
    Make the run report the place an unpropagated template fix stops being silent: have it suggest
    the plugin's /graph-patch skill, which reads the current delta log and answers authoritatively
    whether anything applies. The generated skill must not read the delta log itself and must not
    assert that patches are pending — it lives in the project and has no path to the plugin, and any
    plugin path written into it was resolved at generation time, so it names the generating version
    rather than the installed one. Suggest, never auto-run: /graph-patch edits hand-written prose
    under per-delta approval. Gate the suggestion on a stated cadence rather than raising it on every
    run — raise it unconditionally while this project's .commons.yml has no generated: block, since
    nothing has ever been propagated here and the condition extinguishes itself on the first patch
    run; raise it only periodically once a block exists, recording that it was raised in the
    changelog entry this step already writes so a later run can see when it last happened; and raise
    it whenever the cadence cannot be determined.
  rationale: >
    The mechanism's stated goal is to make an unpropagated fix visible rather than silent, and manual
    invocation was its only discovery path — a maintenance mechanism nobody is ever reminded to run
    reproduces the failure it was built to prevent. This step already suggests out-of-plan skills
    rather than auto-running them, so a pending-patch line fits the idiom exactly. The constraint on
    where the log is read is not incidental. graph-init stamps resolved plugin paths into generated
    skills, and those are already stale in the wild: two live graphs point at knowledge-commons 0.1.7
    and 0.1.8 while the plugin is at 0.4.0, resolving today only because those cache directories
    happen to survive. A discovery hook reading a stale log would report "nothing pending" from it,
    which is worse than no hook at all — it converts an unnoticed gap into a confirmed clean bill of
    health. The cadence is part of the fix rather than polish on it: a notice that fires on every run
    carries no information and gets tuned out, which is the same silence by another route.
  satisfied-test: >
    Does the section direct the report to surface pending template patches by suggesting the
    plugin's /graph-patch skill — rather than by reading the delta log or any other plugin-side file
    itself, and without claiming to know whether patches are actually pending — and does it state a
    cadence under which the suggestion is sometimes withheld, rather than raising it unconditionally
    on every run?
```
