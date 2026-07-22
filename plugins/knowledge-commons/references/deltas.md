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
    run, keyed on what is locally observable rather than on what it implies: raise it every run while
    this project's .commons.yml has no generated: block; raise it about monthly once a block exists;
    and raise it whenever the cadence cannot be determined. Make the monthly arm durable — have it
    write a literal, fixed marker string into the changelog entry this step already writes, and have
    it scan both the live changelog and the most recent monthly archive for that marker. Both halves
    matter: a free-form note is not reliably recognizable to the run that has to find it, and this
    graph's changelog rotates monthly, so scanning only the current file re-raises at every month
    boundary.
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
    on every run? And where that cadence has a periodic arm that suppresses the suggestion based on
    having raised it before, does the section name a fixed marker string to write and to look for,
    and require looking in the archived changelog as well as the live one — so the suppression
    survives the changelog's monthly rotation?

- id: step10-entity-type-gap
  file: process
  anchor: "## 10. Report"
  version: 0.5.0
  instruction: >
    Have the run report recommend a new entity *type* — a new entry in .commons.yml's entity:
    list — when the run keeps naming a category of thing the graph has no declared type for.
    This is about the schema, not about missing notes for nouns of a type that already exists.
    Four properties are the substance of it. (a) It is NOT conditional on the graph already
    declaring an entity type: a graph whose interview answered "none" is exactly the graph that
    may need its first one, so gating on an existing entity tier disables the check where it
    matters most. (b) The bar is recurrence, not a single sighting: several distinct instances of
    one category, named as things a reader would look up, none covered by a declared type; the
    graph's existing notes may supply corroborating instances where one run is thin. (c) The
    report names the category and the instances evidencing it, so the reader judges from evidence
    rather than assertion. (d) Recommending is not doing: point at the work — a .commons.yml
    entry, a directory, a map, backfill — and name re-interviewing graph-init's block 2 as the
    sanctioned route for changing declared types. This step must never edit .commons.yml itself;
    that file belongs to graph-init and /graph-patch, and a schema change must not ride a per-run
    plan approval, which is why this lives in the report and not in the plan.
    Gate it on a cadence rather than raising it every run, in the same shape this section already
    uses for pending template patches: write a literal marker naming the category into the
    changelog entry this step already writes, and before raising a category scan both the live
    changelog and the most recent monthly changelog archive for that marker with that category.
    Suppression is per-category so a different gap still surfaces, and it expires when the marker
    rotates out of both files, letting a still-recurring category be raised again.
  rationale: >
    The requested capability was "proactively identify and recommend new entities where they are
    relevant to the graph." It was first built at the instance level — noticing individual nouns
    that lacked an entity note and proposing notes for them — and shipped at 0.2.0 as the deltas
    step4-entity-signal-class and step5-entity-recommend. That was the wrong layer of abstraction.
    The entity: list in .commons.yml holds *types* (plugin, skill), and graph-init's block 2
    question asks the user to name types, not instances. So "recommend new entities" means noticing
    that the material keeps naming a *kind* of thing the graph has no type for — a schema gap, not
    a missing note. The two instance-level deltas were removed rather than superseded: no graph had
    applied them in any durable state (no live .commons.yml carried a generated: block), so nothing
    downstream had recorded them, and the append-only convention exists to protect what a graph has
    already recorded as applied. This entry is the corrected one, and the run report is the surface
    because a schema recommendation is an observation for a human to act on later rather than a
    write for this run to approve.
  satisfied-test: >
    Does the section have the run report recommend adding a new entity TYPE to .commons.yml — as
    distinct from recommending notes for individual nouns of an existing type — when the run
    repeatedly names a category that no declared type covers? The recommendation must be
    unconditional on the graph already having an entity type (a section that applies this only
    when an entity tier exists, or that proposes lookup notes for un-noted nouns, does NOT satisfy
    this test); it must set a recurrence bar over multiple distinct instances rather than firing on
    a single mention; it must name the category and its evidencing instances; it must stop at
    recommending, pointing at the .commons.yml / directory / map work and at graph-init's block-2
    re-interview rather than editing the config; and it must state a cadence that suppresses a
    category already raised, using a fixed marker looked for in both the live and the archived
    changelog.
```
