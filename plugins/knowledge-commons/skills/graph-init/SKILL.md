---
name: graph-init
description: >
  Scaffold a new knowledge-commons graph in the current project, or wire an existing hand-built
  graph into promotion. Interviews the user, writes .commons.yml, scaffolds the atlas/maps/type
  directories, and generates project-owned process and knowledge-graph skills. Use when the user
  wants to "set up a knowledge graph", "init a graph in this project", "scaffold /process for this
  repo", "wire this graph to the commons", "instantiate the commons", or says "graph-init". Also
  fires for a bare config pass with no scaffolding via the --config-only flag.
argument-hint: "[--config-only]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# graph-init

This is the generator. It runs in the target project — the project that wants a
graph, not the plugin repo — and writes real, project-owned files: a `.commons.yml`, a scaffold, and
(full mode only) two generated skills. Nothing it writes is a stub or a wrapper around this skill;
once written, the project owns it and is expected to sharpen it from real runs.

Two modes, chosen by the invocation: **full** (default, `/graph-init`) sets up a graph from scratch.
**Config-only** (`/graph-init --config-only`) writes just `.commons.yml` for a graph that already has
working hand-written skills — it exists so `/promote` has something to read.

## Full mode

### 1. Orient

Before asking anything, check the project root for `.commons.yml`. If it exists, this graph is
already initialized — say so, and offer to re-interview one or two specific blocks (name them by
number, see the interview below) rather than starting over. Don't silently overwrite a working
config.

If no `.commons.yml` exists, proceed to the interview. Once block 1 has answered `root:`, before
scaffolding (step 5), check whether that directory already holds files. An empty or missing
directory scaffolds cleanly; a populated one means this is probably a hand-built graph that needs
`--config-only`, not a fresh scaffold — stop and say so rather than writing over existing notes.

### 2. Interview

Run these six blocks in order, using `AskUserQuestion`. Batch the questions within a block into as
few calls as the tool allows — but completeness beats round-trip economy: **no question may be
dropped to make a block fit one call.** `AskUserQuestion` takes at most four questions per call, so a
block of five takes two calls, not one truncated one. Ask every question in the block before moving
on, and don't skip a question because a similar one was asked earlier — each is here for a reason.
Don't improvise additional questions beyond this list, and never answer one yourself on the user's
behalf; if something later turns out to need a decision this list doesn't cover, ask it inline when
it comes up, not as a seventh block.

**Block 1 — Graph.**
1. What's this graph's name? It becomes `domain:` on every note this graph promotes — name it for the
   *kind of work* (`orchard`, `wellstead`), not for any person or party.
2. Where does it live? A root path, relative to the project (e.g. `knowledge/`).
3. What should the atlas — the graph's single navigation root — be called? Any name works
   (`principium.md`, `atlas.md`, `index.md`); it's recorded as `graph.atlas` and every map's genitor
   points at it. Don't assume a default without asking.
4. What does it promote to — a path to an existing commons, "none" for a leaf graph, or "I don't have
   one yet"? Before you act on any answer here, understand what a commons *is*: one person's single
   cross-domain graph, shared by every domain graph they own, on every machine they work from. However
   they move it between machines — a git remote, a synced folder, a copy carried across by hand — it is
   normally not new. A local filesystem search tells you whether it is present *here*; it tells you
   nothing about whether it exists. Those are different questions, and conflating them is how a machine
   ends up with a second empty graph also named `commons`, diverging silently from the real one — the
   failure surfaces months later as "why can't this domain see the other domain's claims".

   So resolve provenance in this order, and don't skip to the end:
   - **Is it present here?** If a path was given, verify it — check for a `.commons.yml` there. If
     that misses, search likely roots (`ls -d ~/commons ~/Developer/commons 2>/dev/null`, then a shallow
     scan such as `ls ~/*/.commons.yml ~/Developer/*/.commons.yml 2>/dev/null`) and confirm any candidate
     whose `graph.name` is `commons` with the user.
   - **Does it exist somewhere else?** A local miss means "not on this machine", nothing more — so
     **ask outright**: do you already have a commons somewhere I should copy in, on another machine or
     somewhere I can't see from here? Ask this every time the local search misses. It is the whole check,
     not a fallback for when some other check fails, and it's the only one that works regardless of how
     this person stores things. If they use a git host you can reach, a search there
     (`gh repo list --limit 100 2>/dev/null | grep -i commons`) can *accelerate* the question by giving
     you a candidate to confirm — but treat it as a hint only. It proves nothing when it comes back
     empty: `gh` may be absent, unauthenticated, or pointed at the wrong account, and the commons may
     live somewhere it can't see or under a name this grep won't match. **A silent tool is not a
     negative answer** — that is the same mistake as reading a local miss as "doesn't exist". If a
     commons turns up by either route, you are adopting, not creating — go to step 3's adopt path.
   - **Only once the user has confirmed there is no existing commons**, offer to create one. Creating is
     the last branch, and it needs an actual answer to get there, never merely an empty search.

**Block 2 — Types.** This block has five questions and so needs **two** `AskUserQuestion` calls —
questions 5 through 7, then 8 and 9. Don't try to fit it into one; question 9 is the one that gets
lost, and its answer shapes both the source tiers and whether a synthesis tier exists at all.
5. What does this domain call its evidence type — the atomic, provenanced note (e.g. `observation`,
   `claim`)?
6. What attractor types does it need? For each, is it *open* (accumulates evidence, no verdict —
   like a pattern) or *settled* (a decision with reasoning attached)?
7. Are there entities worth lookup-only notes — the nouns worth a name but no synthesis? Name them or
   say none.
8. Does this graph need a reference tier for unbounded lookup facts that are never an association
   surface?
9. Are there source tiers whose raw material must be preserved verbatim, distinct from the types
   above? And do any rich bounded sources (a call, a meeting) warrant an intermediate *synthesis* note
   between the source and its evidence — one note distilling the event before atomic extraction?

**Block 3 — Sources.**
10. What arrives on its own, without being asked for — a chronicle directory and glob, pasted URLs,
   something else? Name every tier.
11. Are there on-demand sources too — articles, docs, reference material you'd point the pipeline at
   when they come up, rather than anything arriving on a schedule? These get a resolve-and-preserve
   pipeline (fetched material can vanish; keep a source note) but no queue.
12. For each tier: how does an input resolve to the canonical `source:` identity the ledger keys on,
    and is there a resolver skill, or is it already local content?
13. What signal classes should inspection look for in this source — the categories of thing worth
    turning into a note?

**Block 4 — Sinks.**
14. Where do non-graph outputs go — tasks, tracker rows, anything that isn't a note? Name every sink
    and which skill handles it.
15. What's the approval mode per sink — per-item (the sink confirms itself), batch (one combined
    confirmation), or silent?

**Block 5 — Procedure.**
16. Walk one source through, start to finish: what gets created, in what order, and what else has to
    update alongside it — attractor evidence sections, entity notes, map entries?
17. What's durable here versus operational — the line between what earns a note and what belongs in
    an operational system?
18. What must never be captured in this graph — sensitive personal data, anything with a legal or
    safety sensitivity specific to this domain?

**Block 6 — Judgment.**
19. When it's unclear whether something clears the bar, capture or skip — and which error costs more
    here, a thin note or a missed one?
20. What tends to generalize out of this domain, and what must never leave it?

### 3. Adopt or create the commons

Block 1 question 4 ends in one of three states, and they are not interchangeable. **Already present
here** — nothing to do; use the confirmed path. **Exists but isn't on this machine** — adopt it. **Doesn't
exist at all** — create it. Reaching the create branch without having genuinely ruled out the other two
is the one mistake in this skill that quietly costs the most, so don't arrive here by default.

**Where it lives, and why that isn't a free choice.** Every domain graph on every machine writes the
literal string `promotes-to: <commons root>` into its own `.commons.yml`, and those files travel with
their projects. The path has to resolve to the same graph on every machine that reads it. `~/commons` is
the default for exactly that reason — it is machine-independent and it is what the other machines already
wrote. This holds however the commons is kept in sync, or even if it isn't: the string is what has to
match, not the transport. A different root (`~/dev/commons`, a repo-relative path) is fine only if it is
chosen once and used everywhere; choose it here alone and the breakage is silent, deferred, and lands on
a *different* machine than the one where the choice was made. So when confirming the root, say why it
matters rather than presenting it as bare preference — and if the user already has a commons, its path is
already decided, not up for discussion.

**Adopting an existing commons.** Get a copy to the agreed root by whatever means the user already uses
to move it between machines — cloning a repo, pointing at a synced folder, copying it across. Ask if it
isn't obvious; don't assume a version control system. Then verify rather than assume: read the copy's
`.commons.yml` and confirm `graph.name` is `commons`. If it is, you're done — an existing commons already
carries its own config, its own atlas, and its own claims. **Write nothing.** No `.commons.yml`, no
scaffold, no `knowledge-graph` skill; that graph has all of them, sharpened by real runs, and regenerating
them would overwrite work. Just record its root as this project's `promotes-to:` and move on to step 4.
If `graph.name` is something other than `commons`, stop and ask — you've got the wrong directory, or this
person's commons is named differently and the rest of the setup needs to know.

**Creating a new commons.** Only once the user has confirmed no existing commons — an empty local search
is not that confirmation. Offer to instantiate it before touching the project graph. The commons is a
fixed preset, not a fresh interview — confirm only its root path (default `~/commons`, per the reasoning
above) and its atlas name (same question as block 1 question 3), then write it directly:

```yaml
graph:
  name: commons
  root: <confirmed root>
  atlas: <confirmed atlas name>
types:
  evidence:   { name: claim, dir: claims/, supports: principles-or-questions }
  attractors:
    - { name: principle, dir: principles/ }
    - { name: question,  dir: questions/ }
  reference:  { name: reference, dir: reference/ }
promotes-to: ~/.claude/rules/
```

No `sources:` and no `sinks:` — the commons never processes anything; everything in it arrives
by promotion. Scaffold it per step 5 and generate its `knowledge-graph` skill per step 6 — but **not**
a `process` skill: a graph with no sources has nothing to orchestrate.

### 4. Write `.commons.yml`

At the project root, write the config from the interview answers, following the shape in the spec's
`.commons.yml` sketch (§5): `graph:`, `types:`, `sources:`, `sinks:`, `promotes-to:`. Under `types:`,
entity and synthesis tiers (when the interview declared them) follow the reference tier's shape —
`entity: { name: <name>, dir: <dir>/ }`, `synthesis: { name: <name>, dir: <dir>/ }`. Omit `sources:`
and `sinks:` entirely for a graph that has none — don't write empty lists. Do not invent top-level keys
the spec doesn't name (there is no `feeders:` or similar registry in this design).

### 5. Scaffold

Create, under `graph.root`:
- `{atlas}` (the file named in `graph.atlas`) with initial links to the maps you're about to create.
- `maps/`, with one map file per type that will hold notes immediately — every source, evidence,
  attractor, entity, and reference type declared in this graph's config. Each map carries frontmatter:
  `genitor:` pointing at the atlas, `tags: [map]`. This is the one place graph-init
  deliberately overrides "maps are never created empty" (graph-conventions.md's Navigation section):
  the type directories are about to receive their first notes, so seed each with an index from the
  start rather than waiting for five notes to accumulate with nowhere to go. Don't extend this
  exception past initialization — once the graph is running, new maps still wait for the ~5-note
  threshold.
- One directory per declared type (`{evidence-dir}`, each attractor's `dir:`, entity dir if any,
  `{reference-dir}` if any, and a `sources/` directory if this graph has sources). In a git repo, drop
  a `.gitkeep` in each still-empty type directory — git doesn't track empty directories, and a scaffold
  that vanishes on first commit is a confusing first impression.
- An empty `changelog.md` at the graph root.

### 6. Generate the skills

Fill `${CLAUDE_PLUGIN_ROOT}/references/templates/process.md` and
`.../templates/knowledge-graph.md` and write the results to `<project>/.claude/skills/process/SKILL.md`
and `<project>/.claude/skills/knowledge-graph/SKILL.md`. Skip `process/SKILL.md` entirely for a graph
with no sources (the commons).

For each template:
- Replace every `{brace}` value with the concrete config value it names, rendered as natural prose
  where a literal paste would read oddly (`root: .` becomes "the project root", not a bare `.`).
- Where a template refers to "the plugin's `references/graph-conventions.md`", stamp the resolved
  concrete path (`${CLAUDE_PLUGIN_ROOT}/references/graph-conventions.md` resolves for *you*, the
  generator, even though it won't for the generated skill) — a generated skill in a project has no
  other way to find the plugin's files.
- Write prose into every `<!-- SLOT: ... -->` block from the matching interview answers — the
  comment names which block. The example under each SLOT shows the *kind* of prose expected, not
  content to reuse; write this domain's own.
- Delete every SLOT comment and its example after filling it, and delete the template's top
  instruction note (the blockquote in `knowledge-graph.md` explaining the brace convention to you,
  the generator — it has no business in a file a session will read as its own skill).
- In `process.md`, include section 11 (the promotion tail) only if this graph's `promotes-to:` is
  set; omit the whole section, not just its content, when there's nothing to promote to.
- For a graph with no sources (the commons), the knowledge-graph template's extraction-workflow
  section has no pipeline to describe: replace it with a short "How notes arrive" section — claims
  arrive via the plugin's `promote` skill carrying `domain:`, nothing is authored directly, and the
  association step (existing principle / open question / new question) is where new material meets the
  graph. Narrow the awareness protocol accordingly: structural noticing (drift, duplicates, a question
  ready to graduate), not new-evidence capture.

The file you write must contain no braces, no SLOT comments, and no orchard or shopcraft examples —
those exist in the templates to teach *this* generation step, not to ship. If you finish and a brace
or a SLOT comment remains, that's a generation bug — go back and fill it, don't ship it.

### 7. Report

State what was written and where — `.commons.yml`, the scaffold, and (if generated) the two skill
paths. Then check the repo for CI workflows with path-based triggers (`.github/workflows/*.yml`,
`lefthook.yml`, similar): processing commits will touch the graph root and the generated skill paths on
every run, and shouldn't trigger builds or deploys — flag any workflow whose path filters would fire on
them and suggest the exclusion. Finally, suggest the first concrete step: `/process` on one real source
file. For a commons-only run,
suggest running `/promote` from the domain graph that names it instead.

## Config-only mode (`--config-only`)

For an existing, working graph — the reference implementation is the motivating case — that just
needs `.commons.yml` so `/promote` can read it. Interview only:
- Block 1 in full (name, root, promotes-to).
- From block 2, type **names only** — evidence name, attractor names, entity/reference names if
  present. Skip directories, sources, sinks, procedure, and judgment entirely; this mode reads an
  already-working graph, it doesn't shape one.

Write `.commons.yml` and stop. Touch no notes, no maps, no skills. Say explicitly that this wires an
existing hand-built graph into promotion — the graph's actual skills stay exactly as they are.

**Then check that promotion can actually fire.** The graph's existing pipeline was written before this
config existed, so if `promotes-to:` was set, grep its processing/orchestrator skills for an in-band
promotion step ("promote", "generalize"). If none exists, say so plainly: *with `promotes-to:` set but
no promotion tail in the pipeline, promotions will only ever happen manually via `/promote` — the
byproduct-of-work path this config exists for won't fire.* Offer the promotion-tail section of
`${CLAUDE_PLUGIN_ROOT}/references/templates/process.md` as the model for a hand-added tail (screen the
run's findings, candidates in the same plan, `promote` invoked last, once per approved candidate) — but
don't edit the existing skills yourself; surfacing the gap is this mode's job, closing it is the
owner's.

## Never

- Never copy this plugin's own `graph-init` or `promote` skills into a project. Only the *templates*
  get instantiated, as project-owned files.
- Never generate into a graph whose `.claude/skills/process` or `knowledge-graph` already exist
  without asking first — a silent overwrite can destroy hand-sharpened prose.
- Never create a commons off a search coming up empty. A local miss means "not present here", not
  "doesn't exist"; a repo search that finds nothing may just mean the tool is missing, unauthenticated,
  or looking in the wrong place. No search result substitutes for asking the user. Two graphs named
  `commons` diverge silently and nothing in this design will ever tell anyone.
- Never regenerate config, scaffold, or skills into a commons you just copied in. It arrives complete;
  writing into it overwrites work done on another machine.
- Never assume the user keeps the commons in git, or in any particular tool. Ask how they move it
  between machines rather than reaching for a clone command.
- Never invent `.commons.yml` keys beyond `graph:`, `types:`, `sources:`, `sinks:`, `promotes-to:`.
  If a future need surfaces a gap, that's a spec question, not a generator improvisation.
