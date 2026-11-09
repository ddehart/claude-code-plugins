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
| `anchor` | The **exact `##` heading text** the change targets — not a pattern, not a section number. A delta whose anchor doesn't resolve is skipped and reported loudly, never relocated by guess. For `process`, write the heading as the current template has it (`## 12. Report`); from 0.8.0 the patcher matches on the title and ignores the stage number, because live graphs number stages differently. See "A numbering divergence" below. |
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

Two fields are optional:

| Field | Purpose |
|---|---|
| `scope` | `next-section` extends the delta to the one `##` section immediately after its anchor: `/graph-patch` judges, edits, and verifies both. Omitted, the delta is confined to its anchor. Use it for a delta aimed at the preserve stage (see "A numbering divergence" below), never as a way to reach content by guessing where it moved. |
| `supersedes` | The `id` of an earlier delta this one replaces. The successor states the full end state with its own complete `satisfied-test`, so the earlier delta never needs applying: `/graph-patch` doesn't select it while pending, and stamps it once the successor verifies. The earlier entry stays in the log unchanged, because graphs have its id stamped. |

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

# Superseded (0.8.0) by step10-entity-type-gap-direct-edit: point (d)'s graph-init route is wrong.
# Kept unchanged because graphs have this id stamped.
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
    rather than assertion. (d) Recommending is not doing: point at the work and name re-interviewing
    graph-init's block 2 as the sanctioned route for changing declared types. Describe that work for
    both cases the inversion in (a) creates — where an entity: list already exists it is a new entry
    plus a directory, a map, and backfill; where there is none it is *establishing* the tier, which
    is the larger ask and must be said rather than assumed away. This step must never edit
    .commons.yml itself. Attribute that file to graph-init only: /graph-patch amends the generated:
    block and guarantees every other key survives byte-identical, so naming it as an owner of the
    entity: list sends a reader to a skill that will correctly refuse.
    Gate it on a cadence rather than raising it every run, in the same shape this section already
    uses for pending template patches: write a marker naming the category into the changelog entry
    this step already writes, and before raising a category scan both the live changelog and the most
    recent monthly changelog archive for it. The marker's *prefix* is the fixed, literal part — the
    category name inside it is prose the raising run chooses — so the scan matches the prefix, reads
    the categories already recorded, and decides sameness by meaning rather than by string equality.
    That distinction is the substance of the cadence, not a refinement of it: nothing constrains how
    successive runs word a category, so a literal whole-marker match lets "MCP servers" and "MCP
    server integrations" read as different gaps and re-raises the same one every run, with each run
    looking locally correct. Suppression is per-category so a genuinely different gap still surfaces,
    and it expires when the marker rotates out of both files, letting a still-recurring category be
    raised again.
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
    a single mention; it must name the category and its evidencing instances; and it must stop at
    recommending, pointing at graph-init's block-2 re-interview rather than editing the config, and
    describing the work for a graph with no entity: list (establish the tier) as well as for one that
    has it (add an entry). Two further things it must NOT say: that /graph-patch owns or may change
    the entity: list, and that the suppression marker is matched literally in whole — the test for
    the cadence is whether the section fixes only the marker's *prefix*, has the scan read the
    categories already recorded under it in both the live and the archived changelog, and decide
    whether the category is the same one by meaning rather than by string equality. A section that
    scans for the whole marker including a free-form category name fails this test, because nothing
    holds that name stable between runs.

- id: preserve-stage
  file: process
  anchor: "## 2. Resolve"
  version: 0.6.0
  instruction: >
    Add a preservation stage immediately after the resolve section: a named step that writes the
    source note and puts the raw material somewhere durable. Two forms, chosen by the size of the
    source, and the form varies while the presence does not. A small self-contained source (a
    journal entry, a fetched page) is carried verbatim in the source note's body with no separate
    archive. A large one (a transcript, a recording) is written to a committed archive directory
    under the project, with the source note carrying identity, date, a one-line description, the
    processed: stamp, and a pointer to the archived file. State that the archive is version
    controlled and never a scratch or gitignored path. State that this stage writes before the
    plan-approval gate — deliberately, because a run abandoned at plan review should still have
    kept the material — and that what it writes is the source note and the archived file only,
    never evidence and never the stamp. State that preserving twice must not overwrite: an
    existing source note is left alone but for anything genuinely missing, its processed: history
    is never touched, and an existing archive file is left as it is.
    Where the archive's destination is public or shared, the stage carries a redaction gate that
    runs BEFORE the file is written: a deterministic scan for credential shapes that fails closed
    on a hit AND on its own failure (a scan that could not run is not a scan that passed), plus a
    subagent read-through for what patterns cannot catch — third-party names, personal details,
    unreleased plans. Both must pass. Each hit is resolved individually as redact, withhold, or
    accept, with every redaction and withholding recorded on the source note so a degraded archive
    says so. Where the hits cannot be put to a human — a non-interactive or unattended run — the
    stage withholds rather than archiving.
  rationale: >
    The pipeline had no step that wrote a source note. One step searched for one and another
    stamped one; nothing created one. For a small source the gap is invisible, because an
    implementer fills in the obvious. For a large one it fails silently: in the graph where this
    was found, preservation had degraded to a pointer into a gitignored exports directory. That
    graph's founding transcript was in no repository, backed up by nothing, its originating
    worktree already deleted, and unreachable by the pipeline's own queue — recoverable only
    because someone looked outside the resolver's glob. Nothing had been destroyed yet; the
    material was simply undefended, which is the condition a preservation stage converts into a
    committed artifact. (An earlier version of this rationale said the transcript was already
    lost. It was not — 2.8 MB, intact, under another project's slug — and the claim came from a
    scoped search read as absence. The corrected fact is the stronger argument: the stage is
    justified by material being one prune away from gone, not by a loss anyone can point to.)
    The gate is scoped to publication rather than to archival because the hazard is publication;
    a private destination pays nothing. It is deliberately two halves: the floor is dumb and
    verifiable against a planted secret, the read-through covers the majority of a transcript's
    sensitive surface, which is not credential-shaped. Neither is adequate alone — patterns miss
    meaning, and an agent read is judgment that varies run to run and cannot be proven to work.
  satisfied-test: >
    Does the skill have a named stage, before the ledger lookup, that WRITES the source note and
    durably preserves the raw material — as opposed to searching for a source note, stamping one,
    or describing what a source note contains? It must give both forms (inline for small sources,
    committed archive plus pointer for large ones), require the archive to be version controlled
    rather than a scratch or gitignored path, and say that re-preserving does not overwrite an
    existing source note or its processed: history. Where any source tier archives to a public or
    shared destination, it must also gate that write on both a deterministic credential scan that
    fails closed on its own failure as well as on a hit, and a semantic read-through — with hits
    resolved one at a time and withholding as the behavior when no human can resolve them. A
    section that merely says raw material is important, or that describes the source note's shape
    without instructing the run to write one, does NOT satisfy this test.

- id: resolve-orphaned-synthesis
  file: process
  anchor: "## 2. Resolve"
  version: 0.6.0
  instruction: >
    Give the resolve section a named, permanent path for a source whose raw material is gone —
    a pruned transcript, a dead URL. Where the graph has a synthesis for that source, extraction
    reads the synthesis instead, and the source note records raw: unavailable with the reason and
    the date the absence was observed. Constrain it sharply: it fires only when the raw material
    is VERIFIABLY absent, never because the material is large, slow to fetch, or inconvenient to
    read. Where neither the raw material nor a synthesis exists, there is nothing to process.
    Remove any primary/secondary ordering between source tiers that cover the same underlying
    events, and any guard about double-counting between them: this path replaces both. A
    distillation of an event is not a second source tier for that event.
  rationale: >
    "The transcript is usually there, and when it isn't the write-up is what remains" is a real
    case, and the pipeline that lacked a preservation stage handled it by registering the write-up
    as a second, lower-ranked source tier. That inverted the model — a distillation written for a
    human reader is the pipeline's own OUTPUT, not an input — and everything downstream was
    machinery built to contain the inversion: a primary/fallback ordering, an overlapping-tiers
    guard, a survival check run before processing, and a decision note elevating the workaround to
    design. Naming the genuine case honestly, as a degraded path with an explicit marker, costs
    one branch and removes all of it. The verifiably-absent constraint is what stops the path
    becoming a convenient way around extracting from the raw material.
  satisfied-test: >
    Does the section name a specific path for the case where the raw material is gone — extract
    from the synthesis, mark the source note as having no raw material available, with the reason
    — and restrict that path to raw material that is verifiably absent rather than merely large or
    inconvenient? And is the skill free of any primary/secondary ranking between two source tiers
    describing the same events, and of any accompanying guard about the same evidence arriving
    twice through two tiers? A skill that still ranks a distillation as a fallback source tier,
    or that still tells the run to check one tier before extracting from another covering the same
    events, does NOT satisfy this test.

- id: extract-from-raw
  file: process
  anchor: "## 4. Inspect"
  version: 0.6.0
  instruction: >
    State in the inspection step that findings are extracted from the RAW material, and that where
    a synthesis of the same source also exists it may be read for orientation but never sources or
    supplies the wording of a finding. Give the reason, because the reason is what makes the rule
    survive a rewrite: a document written for a human reader has already compressed away the
    corrections, the dead ends, and the exact wording that atomic evidence is made of, and an
    extraction that runs on it inherits every omission without being able to detect any of them.
    Name the single exception — the orphaned path where the raw material is verifiably gone — so
    the rule reads as absolute everywhere else.
  rationale: >
    This is the specific thing the four-stage model exists to protect, and it is the one that gets
    lost first, because reading the synthesis is easier and looks equivalent. It is not: the first
    real run of this pipeline on a session transcript found three divergences between the session's
    own account of itself and what the transcript showed, and every one of them is invisible to a
    reader of the account alone. A synthesis on the input side is how a graph ends up recording
    what an agent remembered rather than what happened.
  satisfied-test: >
    Does the inspection step direct extraction at the raw material and explicitly forbid the
    synthesis as the source of a finding, while allowing it to be read for orientation? The test is
    the direction of the constraint, not the presence of the word: a section that merely MENTIONS
    the synthesis, describes it as available, or says evidence "comes from the source" without
    ruling out the synthesis does NOT satisfy this test. It must be readable as an instruction that
    a finding is sourced and quoted from the raw material — with the verifiably-absent-raw case as
    the stated exception, if it names an exception at all.

- id: synthesis-in-plan
  file: process
  anchor: "## 5. Propose the plan"
  version: 0.6.0
  instruction: >
    CONDITIONAL — applies only to a graph that declares a synthesis tier; where none is declared,
    this delta is satisfied vacuously and no edit is needed. Have the proposed plan name what the
    synthesis stage will do: link the synthesis that already exists for this source, or invoke the
    graph's configured producer to write one. Both cases are ordinary — a source distilled at the
    time and processed later arrives with its synthesis written; a source processed fresh does not.
    Have the plan also name what the preservation stage already wrote before this gate, so the
    reader can see what landed and what the approval is actually deciding.
  rationale: >
    The synthesis stage's substance straddles the approval gate: the plan has to name it and the
    run has to write it. A single delta anchored on the run step would edit only the write side and
    leave a run that writes something the plan never proposed — which is a write escaping the one
    approval this pipeline rests on. The patcher edits one section per anchor and cannot reach
    backward, so the two halves are two deltas on adjacent anchors. The preservation line is here
    for the same reason from the other direction: preservation writes BEFORE this gate, so a plan
    that doesn't mention it leaves the reader unable to tell what has already happened.
  satisfied-test: >
    For a graph declaring a synthesis tier: does the plan step state that the plan names the
    synthesis work — either linking an existing one or invoking the configured producer — so it
    falls under the single approval rather than happening outside it? A plan step that describes
    only notes created and updated, with no mention of the synthesis, does NOT satisfy this test.
    For a graph with no synthesis tier, this test is satisfied by construction.

- id: synthesis-write
  file: process
  anchor: "## 6. Run to completion"
  version: 0.6.0
  instruction: >
    CONDITIONAL — applies only to a graph that declares a synthesis tier; vacuously satisfied
    otherwise. Have the run write the synthesis as a SIBLING of evidence extraction: both are made
    from the same raw material, neither is upstream of the other, and the run does not wait for one
    before doing the other. Link the synthesis from the source note when it lands. State plainly
    that the run does not extract from the synthesis once it exists. Where the producer is a
    separate skill, it is invoked, never reimplemented or reordered from out here — it has its own
    rules about how it writes and in what order.
  rationale: >
    The synthesis role had been defined as an "intermediate" between a rich source and the evidence
    extracted from it, which places a lossy distillation inside the extraction path — the opposite
    of the model. Defined that way the type had no clear place in a pipeline whose extraction step
    already reads the source directly, which is the likeliest reason it was specified into four
    artifacts and implemented in none. Naming it a sibling output is what gives the stage somewhere
    to sit. The invoke-never-reimplement constraint keeps the coupling to two skills at
    invoke-and-link, rather than this pipeline acquiring opinions about how the other one works.
  satisfied-test: >
    For a graph declaring a synthesis tier: does the run step write the synthesis as a sibling of
    evidence extraction — explicitly neither upstream nor downstream of it, both from the raw
    material — and link it from the source note? A section that writes the synthesis first and then
    extracts from it, or that writes it after extraction as a summary OF the extracted notes, fails
    this test: both make it an intermediate, in opposite directions. Where a separate skill produces
    it, the section must invoke that skill rather than restating what it should write.

- id: synthesis-is-sibling
  file: knowledge-graph
  anchor: "## Types in This Graph"
  version: 0.6.0
  instruction: >
    Correct the synthesis type's description from an intermediate between a source and the evidence
    extracted from it, to a sibling output of the raw material: one note distilling a bounded source
    for a HUMAN reader, produced alongside the atomic evidence rather than in between. State that
    evidence is extracted from the raw material and not from the synthesis, that the synthesis links
    back to its source note and lists what was extracted alongside it, and that a synthesis note may
    be an existing project artifact adopted into the tier at the path it already occupies rather
    than one the graph authored. Where the graph currently declares no synthesis tier BECAUSE its
    stated reasoning is that its source is already a distillation of some event, that reasoning
    identifies a synthesis tier rather than the absence of one — correct it to name the real tier.
  rationale: >
    The intermediate framing was in the conventions, this template, and the plugin README, and it is
    what made the type unimplementable: an intermediate has no place in a pipeline whose extraction
    step already reads the source directly. The framing also produces a specific wrong answer in
    graphs whose sources include a write-up of an event — they reason, correctly, that the write-up
    is already a synthesis, and then conclude, incorrectly, that they therefore have no synthesis
    tier. The first clause is right and the conclusion inverts it: being a synthesis of the event is
    what makes it output rather than input.
  satisfied-test: >
    Does the synthesis entry describe the note as a sibling output of the raw material, produced for
    a human reader alongside atomic extraction, with evidence extracted from the raw rather than
    through it? An entry calling it an intermediate, or describing evidence as extracted FROM the
    synthesis, fails. So does an entry stating the graph has no synthesis tier on the grounds that
    its source is already a session- or event-level synthesis — that reasoning names a synthesis
    tier and must be corrected to declare it rather than to deny it.

- id: step10-entity-type-gap-direct-edit
  file: process
  anchor: "## 12. Report"
  version: 0.8.0
  supersedes: step10-entity-type-gap
  instruction: >
    Have the run report recommend a new entity *type* (a new entry in .commons.yml's entity: list)
    when the run keeps naming a category of thing the graph has no declared type for. This is the end
    state step10-entity-type-gap described, with its route corrected, so a graph that applied that
    delta needs only the route changed. (a) It is NOT conditional on the graph already declaring an
    entity type: a graph whose interview answered "none" is the one that may need its first. (b) The
    bar is recurrence: several distinct instances of one category, named as things a reader would
    look up, none covered by a declared type; existing notes may corroborate where one run is thin.
    (c) The report names the category and the instances evidencing it. (d) The route is a direct
    edit, made once the graph's owner says yes: a new entry in the entity: list, a directory, a map,
    an atlas link, a line in the sibling knowledge-graph skill's type list, a mention wherever this
    process skill names the declared types (an inspect-step signal class, for example), and backfill.
    Remove any statement that the entity: list or .commons.yml's type declarations belong to
    graph-init or are graph-init's to write, and any statement that re-interviewing graph-init (its
    block 2, or its types questions) is the sanctioned, required, or only route. A re-interview may be
    named as optional, never required; if it is named, say it doesn't rewrite already-generated
    skills, so the skill edits are needed either way. Where the section covers a graph with no
    entity: list, say plainly that establishing the tier is the larger ask, by the same route; a
    section already rewritten for a graph that declares types may leave that case out. (e)
    Recommending is not doing: during the run the step never edits .commons.yml, adds the entry, or
    creates the directory; it may offer to make the edit after the run. Don't name /graph-patch as an
    owner of the entity: list; it amends only the generated: block and would correctly refuse. (f)
    Cadence: a category already raised is not raised again while its record lasts, and sameness is
    judged by meaning rather than by string equality, because nothing constrains how runs word a
    category. The template does this with a marker of the form [entity-type-gap: <category>] in the
    changelog entry this step already writes, scanning the live changelog and the most recent monthly
    archive for its fixed prefix. A graph that already keeps that record another way (a marker
    without brackets, a shadow log) keeps its own mechanism: never change an existing graph's marker
    form, since its recorded markers would stop matching and every category already raised would be
    raised again.
  rationale: >
    The graph-init route was never how types were actually added. Graph owners add entity types by
    direct edit with their own approval: financial-planning added estate-document on 2026-11-01 and
    income-stream on 2026-11-08 that way; claude-usage added its first three types on 2026-10-05;
    osu-builder-in-residence added program on 2026-07-28 and published copy on 2026-08-01;
    airbnb-prep declared tool on 2026-09-27 directly at the user's instruction. None of those
    involved a re-interview. Because generated skills repeated the graph-init route, they kept
    steering their owner toward a heavier path. The route was also incomplete. A re-interview
    rewrites .commons.yml, but graph-init won't overwrite hand-sharpened generated skills without
    asking. So a graph that followed it got a config declaring the new type and skills that still
    enumerated the old ones: airbnb-prep's knowledge-graph skill said "none declared" for seventeen
    days after its tier existed. The enumeration in the two generated skills is the part both routes
    kept missing, which is why (d) lists it. Points (a)-(c), (e) and (f) are step10-entity-type-gap's,
    unchanged; they are restated so this entry is complete on its own and the superseded one never
    needs applying. Point (f) and its test clause are stated by substance rather than by the
    template's literal marker: the first patch run (2026-11-08) found four graphs that had already
    kept the cadence a different way on purpose, three with unbracketed markers and one with a
    shadow log, and a literal clause would have left their edit permanently unverifiable. That
    correction was made in place, before any graph had stamped this id.
  satisfied-test: >
    Does the section have the run report recommend adding a new entity TYPE to .commons.yml (not
    notes for individual nouns of an existing type) when the run repeatedly names a category no
    declared type covers, unconditionally on the graph already having an entity type, with a
    recurrence bar over multiple distinct instances, naming the category and its instances? Does it
    name a direct edit, made once the owner approves, as the route, listing among the work at least
    the entity: entry, a directory, a map, an atlas link, and the line in the sibling knowledge-graph
    skill's type list? Does it stop at recommending during the run, without editing .commons.yml?
    Does it have a cadence that keeps an already-raised category from being raised again, with a
    record that survives the changelog's monthly rotation and a sameness judgment made by meaning?
    Any fixed record form passes: the template's [entity-type-gap: prefix, the same prefix without
    brackets, or a graph's own log. The section FAILS if, as a current instruction, it says the
    entity: list or type declarations belong to graph-init or are graph-init's to write; names a
    graph-init re-interview as the sanctioned, required, or only route; says /graph-patch owns or
    may change the entity: list; applies the check only when an entity tier exists; or decides
    sameness by matching a free-form category name literally. Naming the re-interview as an optional
    alternative passes, and so does a sentence reporting the graph-init route as a former claim that
    was corrected. If the section covers a graph with no entity: list, it must call establishing the
    tier the larger ask, by the same route; a section for a graph that already declares types may
    omit that case.

- id: kg-types-entity-route
  file: knowledge-graph
  anchor: "## Types in This Graph"
  version: 0.8.0
  instruction: >
    Have the Entities entry say how a new entity type is added: a direct edit once the graph's owner
    says yes, never a required graph-init re-interview, and the edit includes a line in this types
    section. Point at the sibling process skill's report step for the rest of the work rather than
    listing it here; this skill is read on every search and capture, and the change is rare. If the section already names graph-init or a re-interview of its block 2 as the
    sanctioned or required route for a new type, replace that claim; keep any history of how this
    graph's existing types were actually added, reworded so it no longer asserts the route as
    required. Don't edit the type list itself or the descriptions of the types it declares.
  rationale: >
    The process template's report step, through step10-entity-type-gap, told generated graphs that a
    new entity type had to go through a graph-init re-interview. At least one graph (airbnb-prep)
    carried that claim into its knowledge-graph skill's types section as local prose: "That remains
    the sanctioned route for a new type." Graph owners actually add types by direct edit (see
    step10-entity-type-gap-direct-edit for the instances), and a re-interview leaves this skill's type
    list stale because graph-init won't overwrite hand-sharpened generated skills without asking.
    airbnb-prep's list said "none declared" for seventeen days after its tier existed. This section
    is where a reader looks to see what types exist, so it is the right place to say that adding one
    means editing the list too. The template now says so; graphs whose section never mentioned a
    route only gain the sentence.
  satisfied-test: >
    Does the section, in or next to its Entities entry, say that a new entity type is added by direct
    edit once the graph's owner approves, and that the edit includes a line in this types section
    (not only the .commons.yml entity: entry)? The section FAILS if, as a current instruction, it
    names graph-init or a re-interview of its block 2 as the sanctioned, required, or only route for
    a new type, or says type declarations are graph-init's to write. Naming the re-interview as an
    optional alternative passes, and so does history recording that a past type was added that way.

- id: kg-conventions-by-skill
  file: knowledge-graph
  anchor: "## Conventions"
  version: 0.9.0
  instruction: >
    Where the section points at the full graph conventions, have it name the plugin's
    knowledge-commons:conventions skill as the way to load them, and remove every filesystem path into
    a plugin installation: a resolved literal, a glob, or a discovery command (ls, find, sort -V over
    the plugin cache, or similar). A repository or GitHub location offered as the way to read them is
    replaced too. Keep the section's statement that the compact restatement covers day-to-day work,
    and keep the restatement itself unchanged.
  rationale: >
    graph-init used to stamp the resolved, version-pinned path to the plugin's
    references/graph-conventions.md into this section, because a skill in a project gets no
    ${CLAUDE_PLUGIN_ROOT} substitution (verified live on Claude Code 2.1.319). That literal names one
    version on one machine. Checked on devbox 2026-11-08, six of fourteen graphs pointed at a file that
    no longer existed (pruned 0.5.0 caches, macOS paths, a Remote Control plugin directory since
    removed), and five resolved only to the 0.6.0 copy, which differs from the 0.8.2 contract by 23
    lines, so a session read an outdated contract with no sign it was outdated. Hand-fixes moved the
    rot instead of removing it: a cache glob assumes one install layout, runtime discovery can't pick
    this session's install out of the registry's many project-scoped entries at different versions,
    and a repository path isn't readable from a session. A plugin skill gets ${CLAUDE_PLUGIN_ROOT}
    substituted to the installed version each time it loads, so naming the skill is the one reference
    that cannot go stale. This is the pattern Anthropic's plugin docs recommend for reaching plugin
    files from outside the plugin, and the platform has no stable install path to use instead
    (anthropics/claude-code#82068, closed unanswered).
  satisfied-test: >
    Does the section name the knowledge-commons:conventions skill as how to load the full conventions,
    AND contain no filesystem path, glob, or discovery command into a plugin installation (any
    directory under ~/.claude/plugins/ or ~/.claude/remote/plugins/, or a /Users/... equivalent,
    versioned or not)? Both halves are required. A cache glob or a find command fails, as does a
    GitHub or repository path offered as where to read the file. A section that names the skill and
    also still carries a path fails.

- id: preserve-plugin-files-by-skill
  file: process
  anchor: "## 2. Resolve"
  scope: next-section
  version: 0.9.0
  instruction: >
    Applies to the preserve stage only, which is either a subsection of this section or its own stage
    directly after it (often "## 3. Preserve"), wherever the preserve-stage delta put it. Wherever
    that stage cites the plugin's graph conventions (typically, small sources carried inline "as the
    conventions describe"), have it name the knowledge-commons:conventions skill as the way to load
    the full contract when the sibling knowledge-graph skill's restatement doesn't cover it, so the
    citation is a fallback rather than a load on every run.
    Wherever its redaction gate runs the floor scan, have it invoke the knowledge-commons:scan-secrets
    skill with the rendered file path(s) as arguments instead of running the script by path, and add
    to the gate's fail-closed rule that the skill being unavailable means the scan did not run, which
    is a stop. Remove every filesystem path into a plugin installation from the stage. A path to the
    scanner's source inside the plugin's own repository, in the graph that is that repository, is a
    project path and may stay. Change nothing else about the gate: the scratch-path rendering, the
    subagent read-through, per-hit resolution, and withholding when no human can be asked all stay as
    written. If this graph has no preserve stage, or the stage cites neither the conventions nor the
    scanner, there is nothing to change.
  rationale: >
    The same generator defect as kg-conventions-by-skill, in the process skill. graph-init stamped the
    resolved conventions path into this stage's inline-form bullet (two live graphs carry a 0.6.0 cache
    path there), and the template stamped a resolved path to scripts/scan-secrets.sh into the redaction
    gate. A stale scanner path fails closed, which is safe but blocks every archive until someone
    notices, and the next gated graph generated would have received one. Running the scan through a
    plugin skill keeps it a script with an exit code, which is the reason the floor is a script at all:
    the skill's allowed-tools rule runs it with no permission prompt, and it reports the exit code
    verbatim (verified live: exit 0 on a clean file, exit 1 with the finding on a planted ghp_ token).
    The anchor is the resolve section rather than the preserve stage's own heading because live graphs
    carry that stage both as its own "## 3. Preserve" and as a subsection of "## 2. Resolve"; see "A
    numbering divergence" below. Anchoring on the preserve heading instead would skip loudly, and stay
    unstamped forever, in every graph that has no such heading. Reaching the following stage is what
    scope: next-section (added in 0.9.0) is for.
  satisfied-test: >
    In the preserve stage (a subsection of this section, or its own stage directly after it), is
    there no filesystem path into a plugin installation (under ~/.claude/plugins/,
    ~/.claude/remote/plugins/, or a /Users/... equivalent), does every citation of the plugin's graph
    conventions name the knowledge-commons:conventions skill, and, if the stage has a redaction gate,
    does its floor scan either invoke the knowledge-commons:scan-secrets skill and treat that skill
    being unavailable as a stop, or (only in the plugin's own source repository) run the scanner by
    its repo-relative source path? A conventions citation by bare filename with no way to load it
    fails. A graph with no preserve stage, or whose stage cites neither file, passes.
```

## A numbering divergence the 0.6.0 entries introduce

The six 0.6.0 entries above add two stages to the `process` template, so a freshly generated skill numbers
its sections differently from a patched one: the template renumbers freely, while the deltas anchor on
headings that already exist in generated prose and instruct insertion *relative* to them (never a
renumber, which would invalidate all six pre-0.6.0 anchors at once).

**Future deltas targeting the preserve or synthesize stages must anchor on the pre-existing heading,
not on the new stage's own heading** — `## 2. Resolve` rather than `## 3. Preserve` — until this log
records that every live graph has been patched through 0.6.0. **A preserve-stage delta anchored on
Resolve must also set `scope: next-section`** (0.9.0). Without it `/graph-patch` judges only Resolve,
sees none of the preserve text in graphs that carry it as its own stage, and reports those graphs
*already satisfied*: the edit never happens and the delta is stamped anyway. A delta anchored on `## 3. Preserve`
resolves in a freshly generated graph and silently fails to resolve in every patched one, which is the
failure this log's skip-loudly rule exists to make visible rather than to rely on.

**The divergence runs in both directions, and the reverse arm is the easier one to forget.** Nine of the
twelve anchors through 0.6.0 — every pre-0.6.0 `process` entry, plus the three 0.6.0 ones anchored on
`## 4. Inspect`, `## 5. Propose the plan` and `## 6. Run to completion` — name headings the 0.6.0
template no longer has, because inserting two stages renumbered everything after `## 2. Resolve`. They
still resolve in every *already-generated* graph, which is the population they exist to patch, so this
is not a defect in them.

What it means in practice: **`applied:` is what protects a freshly generated graph, not anchor
resolution.** `graph-init` stamps every current delta id as applied at generation time precisely because
the prose is rendered from current templates, so those deltas are never selected for it. Two paths can
still reach an anchor that will not resolve — `/graph-patch`'s 0.1.8 bootstrap, and a retry after a
delta failed and stayed unstamped. Both skip loudly and neither misapplies, but a reader seeing
`anchor not found` on a 0.6.0-generated graph should recognize it as this, not as a corrupted skill.

**A delta written after 0.6.0 has neither protection**, and this is what title matching fixes. It
isn't stamped on 0.6.0-generated graphs, so it is selected for both populations, and any `process`
stage after `## 2. Resolve` carries a different number in each: `## 10. Report` in a patched graph,
`## 12. Report` in a fresh one, and `## 11. Report` in a fresh one without a synthesis tier, since the
template omits that stage and renumbers. From 0.8.0 the patcher ignores the stage number and matches the
title (D23 in the patch-mechanism spec), so one anchor, written as the current template has it, resolves
in all three. It also lets the pre-0.6.0 anchors above resolve on the bootstrap and retry paths. A
heading whose *title* a project renamed by hand still skips loudly, which is correct. And the rule above
about the preserve and synthesize stages still stands: a patched graph may have those stages under a
different title, or not at all.
