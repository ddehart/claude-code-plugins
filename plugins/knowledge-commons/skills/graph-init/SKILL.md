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
few calls as the tool allows; don't skip a question because a similar one was asked earlier — each is
here for a reason. Don't improvise additional questions beyond this list; if something later turns
out to need a decision this list doesn't cover, ask it inline when it comes up, not as a seventh
block.

**Block 1 — Graph.**
1. What's this graph's name? It becomes `domain:` on every note this graph promotes — name it for the
   *kind of work* (`orchard`, `wellstead`), not for any person or party.
2. Where does it live? A root path, relative to the project (e.g. `knowledge/`).
3. What should the atlas — the graph's single navigation root — be called? Any name works
   (`principium.md`, `atlas.md`, `index.md`); it's recorded as `graph.atlas` and every map's genitor
   points at it. Don't assume a default without asking.
4. What does it promote to — a path to an existing commons, "none" for a leaf graph, or "I don't have
   one yet"? If a path is given (or you're about to suggest one), **verify it before relying on it**:
   check for a `.commons.yml` there. If the expected location has none, don't conclude the commons
   doesn't exist — search likely roots first (`ls -d ~/commons ~/Developer/commons 2>/dev/null`; then a
   shallow scan such as `ls ~/*/.commons.yml ~/Developer/*/.commons.yml 2>/dev/null`) and confirm any
   candidate whose `graph.name` is `commons` with the user. Only after the search comes up empty do you
   offer to create one.

**Block 2 — Types.**
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
11. For each tier: how does an input resolve to the canonical `source:` identity the ledger keys on,
    and is there a resolver skill, or is it already local content?
12. What signal classes should inspection look for in this source — the categories of thing worth
    turning into a note?

**Block 4 — Sinks.**
13. Where do non-graph outputs go — tasks, tracker rows, anything that isn't a note? Name every sink
    and which skill handles it.
14. What's the approval mode per sink — per-item (the sink confirms itself), batch (one combined
    confirmation), or silent?

**Block 5 — Procedure.**
15. Walk one source through, start to finish: what gets created, in what order, and what else has to
    update alongside it — attractor evidence sections, entity notes, map entries?
16. What's durable here versus operational — the line between what earns a note and what belongs in
    an operational system?
17. What must never be captured in this graph — sensitive personal data, anything with a legal or
    safety sensitivity specific to this domain?

**Block 6 — Judgment.**
18. When it's unclear whether something clears the bar, capture or skip — and which error costs more
    here, a thin note or a missed one?
19. What tends to generalize out of this domain, and what must never leave it?

### 3. Find or create the commons

If block 1's answer to "promotes to" names a commons whose `.commons.yml` doesn't exist yet — after
the search in block 1 question 4 has actually come up empty, not merely after one default path missed —
offer to instantiate it before touching the project graph. The commons is a fixed preset, not a fresh
interview — confirm only its root path (default `~/commons`) and its atlas name (same question as
block 1 question 3), then write it directly:

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
  attractor, entity, and reference type declared in this graph's config. This is the one place graph-init
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
paths. Suggest the first concrete step: `/process` on one real source file. For a commons-only run,
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

## Never

- Never copy this plugin's own `graph-init` or `promote` skills into a project. Only the *templates*
  get instantiated, as project-owned files.
- Never generate into a graph whose `.claude/skills/process` or `knowledge-graph` already exist
  without asking first — a silent overwrite can destroy hand-sharpened prose.
- Never invent `.commons.yml` keys beyond `graph:`, `types:`, `sources:`, `sinks:`, `promotes-to:`.
  If a future need surfaces a gap, that's a spec question, not a generator improvisation.
