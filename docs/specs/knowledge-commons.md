# Knowledge Commons Plugin — Specification

> **Version:** 1.0.1 · **Status:** built (Phase 1) · **Date:** 2026-07-14
>
> **v1.0.1 — Phase-1 build amendments**, from the paper-parity check against the reference (G2). Three
> findings, all mechanism the 5-role model couldn't hold: (1) an optional **synthesis** type role — an
> intermediate note between a rich bounded source and its atomic evidence — added to the conventions,
> the knowledge-graph template, and interview block 2; (2) the **entity** role's "lookup-only" describes
> retrieval mode, not thinness — entity notes may accumulate curated context and interaction logs; (3)
> source tiers may declare a **conditional pre-step** (formatting raw material) and **entity-level
> batching** for transactional sources, and hand-fed tiers (no glob) prompt for input rather than being
> queued. Recorded here; implemented in the templates.
>
> **Design history.** This is a fresh start. Three earlier iterations (a private v0.2, and v0.3–v0.6.1 in
> this repo) converged on the right generator model but accumulated a validation apparatus — an executable
> validator, write transactions, lifecycle machinery, a federation registry — that solved problems the
> working reference implementation demonstrates do not occur under a human-in-the-loop workflow. All of it
> was reverted from `main` on 2026-07-13; the superseded specs remain reachable in git history
> (`docs/specs/knowledge-commons-plugin.md` and `docs/specs/knowledge-commons-generator.md` at commit
> `b33e712`). This spec carries forward what survived: the generator model, the config/procedure split, the
> note conventions, and the promotion-as-derivation model — at the weight of the system it generalizes.

---

## 1. Problem

Personal knowledge systems die the same way: automated **capture** with no **refinement** stage. The
motivating natural experiment is two vaults by one author in one tool: a professional knowledge graph with
~93% of notes touched in 90 days and a 2:1 derived-to-source ratio, and a personal vault an order of
magnitude larger with 0.3% touched and effectively zero lateral links.

The living graph runs on ~1,150 lines of prose: a thin `/process` command, an orchestrator skill
(inspect → plan → approve → run → stamp), and a knowledge-graph skill carrying conventions and extraction
workflows. It has **no validator in the write path, no lifecycle machinery, and no enforcement layer** —
its health rests on two things: an LLM is the primary writer following prose conventions, and a human
approves every plan. That is the mechanism this plugin generalizes, at that weight.

Two gaps remain that the reference cannot fill by itself:

1. **Every domain needs its own instance.** Standing up a new graph (a project repo, a new engagement)
   currently means hand-writing the skill pair from scratch.
2. **Nothing spans domains.** A pattern observed in one domain has nowhere to meet the same pattern from
   another. The **commons** — a personal cross-domain graph — is that missing tier, and the instruction
   tier (`~/.claude/rules/`) is its graduation target.

## 2. Goals

- **G1.** `graph-init` scaffolds a working per-project processing pipeline — config, graph skeleton, and
  project-owned `process` + `knowledge-graph` skills — from a config-driven interview.
- **G2.** Filled with the reference implementation's answers, the templates produce skills functionally
  equivalent to the reference's hand-written pair (a paper diff, not a live swap).
- **G3.** Knowledge accrues as a byproduct of work: one plan approval per `/process` run, no manual
  authorship, and every graph with a `promotes-to:` asks "does any of this generalize?" as part of the run.
- **G4.** Promotion is one uniform mechanism for every graph — same flow into the commons from any domain,
  same flow from the commons into the instruction tier.

## 3. Non-goals

- **NG1. No verification machinery.** No validator, no write-time gates, no transactions, no lifecycle
  enforcement. Graph health is prose conventions + plan approval. If real use ever produces real structural
  drift, a check script earns its way in that day — evidence first.
- **NG2. No ambient/push discovery.** No SessionStart injection. Consultation is pull ("what do we know
  about X" → read the maps, follow links).
- **NG3. No retrieval infrastructure.** No MCP server, embeddings, or vector search. The association
  surface is small and read directly.
- **NG4. No bulk-capture sources** (read-later archives, highlight exports) until the refinement loop is
  proven on chronicles.
- **NG5. No scheduled cross-graph sweep in v1.** The chronicle queue makes unprocessed material
  re-discoverable; add a sweep only if real use shows in-band promotion missing things.
- **NG6. The plugin never contains content.** Graphs, configs-in-use, and notes live in private repos.
  Examples in the plugin and this spec are fresh-authored.

---

## 4. Design decisions

### D1 — The plugin is a generator; generated skills are project-owned prose

`graph-init` interviews, then writes real skills into the target project — not stubs, not thin wrappers
around a runtime engine. The generated skills are owned by the project and **expected to drift**, exactly
as the reference's hand-written skills do: the procedure is the living part of the system, and sharpening
it from real runs is how these graphs stay good. There is no `--upgrade`, no invariant markers, no fork
anxiety. A project that wants a newer template re-runs `graph-init` and merges by hand.

The plugin itself keeps exactly two skills: `graph-init` and `promote`.

### D2 — Config drives shapes; the interview fills procedures

Two kinds of specialization, split by kind:

| Kind | Lives in | Examples |
|---|---|---|
| **Data-shaped** | `.commons.yml` | type names, directories, frontmatter fields, sources, sinks, `promotes-to:` |
| **Procedure-shaped** | generated skills, as prose | extraction workflows per source type, judgment rules, debiasing instructions, title conventions |

The config is both the generator's input and standing metadata any session can read. No YAML key attempts
to hold a procedure — that was the central lesson of the earlier iterations, and it survives.

### D3 — Graph anatomy (the invariant conventions every instantiation shares)

- **Navigation:** an atlas links to maps; maps link to notes. Every note carries
  `genitor: "[[parent-map]]"` and is entered in its map, alphabetically. Every note is reachable from the
  atlas. Maps are never created empty — create one when ~5 notes cluster with no map covering them.
- **The one structural rule:** evidence notes must support ≥1 attractor (a frontmatter link plus the
  attractor's evidence section). This single convention is why living graphs have lateral edges and dead
  vaults are taxonomies. It is enforced the way everything here is enforced: the writing skill says so,
  and the human reads the plan.
- **Type roles**, named per graph in config: **source** (raw, preserved, carries the ledger stamp),
  **evidence** (atomic, provenanced, supports attractors), **attractor** (accumulates evidence; has a
  "so what"), **entity** (the nouns; lookup-only), **reference** (lookup facts; unbounded; never an
  association surface). Non-graph outputs (tasks, tracker rows) route to **sinks** and never become notes.
- **Maps are the index.** Attractor map entries are annotated — `- [[title]] — the "so what" in one
  clause` — so reading the attractor maps *is* reading the distilled corpus. There is no separate
  generated index artifact.
- **A changelog** records why the graph looks the way it does: one entry per session that changed it,
  current month in `changelog.md`, archived monthly.
- **Durable over ephemeral:** operational facts (amounts, dates, statuses) live in operational systems,
  not the graph. **Check before creating:** search first; update the existing note. **Capture the
  non-obvious:** facts re-derivable from sources are not worth a note.

### D4 — Processing is local: every domain processes at home

Each domain that produces knowledge gets its **own graph** and its own generated `/process`:

- The reference work graph processes its calls and email where it lives.
- A project repo (e.g. wellstead, devbox) gets a `knowledge/` graph in the repo; its `/process` works the
  repo's own chronicle files. Domain-local observations — design decisions, project patterns — accumulate
  *there*, where they're useful in context.
- The generated orchestrator is the reference's flow: **resolve → find ledger → inspect (inline under
  ~1,500 words; subagent fan-out per signal class above) → propose plan → one approval `[y / edit /
  explain]` → run in dependency order → continue-and-collect failures → stamp → report.** Re-pause only
  for genuine ambiguity or conflict with the existing record.
- **The ledger is local:** each processed input gets a source note in the graph, keyed on a canonical
  `source:` (a chronicle file's repo-relative path; a recording URL; a thread permalink), holding the
  `processed:` stamp (`date / ran / skipped / errored`, a list, so it keeps history). Granularity is one
  note per input file. If a chronicle file grows after processing, re-running `/process` on it enters
  **augment mode**: read the stamp and the existing notes, do only what's new — judged by reading, not by
  digests. Sessions read chronicle sources; nothing ever writes into another repo's files.

### D5 — The commons receives; it never processes

The commons is a graph instantiation like any other (evidence: **claims**; attractors: **principles** and
**questions**; a `reference/` tier for portable tool facts) with two deliberate absences: **no sources and
no orchestrator**. Everything in it arrives by promotion from a domain graph, carrying
`domain: <source graph.name>` — the one field that exists only on promoted notes. Nothing is authored
directly into it; hand-authorship is the "remember to write notes" failure this design exists to remove.

Conventions, not machinery:

- A **principle** carries a `## so what` (the actionable consequence) and an evidence list whose entries
  show their domains. A principle whose evidence spans **2+ domains** is *held*; below that it is
  *provisional*. This is one line of convention applied by reading — no status field is required, no
  check enforces it.
- **Questions absorb the singletons.** A claim that supports no principle yet lands under an open
  question, so nothing is dropped and nothing is enshrined early.
- The commons' own `promotes-to:` is the **instruction tier** (`~/.claude/rules/`): a principle that
  should change how sessions *behave* graduates into a rule, deliberately, under approval. The graph is
  the epistemic tier where stances accumulate evidence; rules are the behavioral view of the few that
  earned it.

### D6 — Promotion: one uniform mechanism, no posture distinctions

`/promote` behaves identically for every graph pair — reference → commons, wellstead → commons,
commons → rules. There is no personal/professional mode switch.

- **Derivation, never migration.** The source note stays. A **new, self-contained** note is written into
  the target carrying only the portable substance. The test that defines promotion is the portability
  test: *would this stay true and useful if its source domain vanished?* If a derived note needs its
  source to make sense, it has not generalized.
- **Provenance is `domain:`** — the source graph's `graph.name`, a plain non-resolving field. Never a
  path, never a link. Wikilinks in a promoted note must resolve within the target graph.
- **Association happens at promote time.** `promote` reads the target's attractor maps (the annotated
  index, D3) and connects the incoming claim: support an existing principle, attach to an open question,
  or propose a new question. "This principle now has evidence from a second domain" is a sentence in the
  proposal, noticed by reading.
- **Every promotion is proposed, and a human approves it** — the same gate as every other write. There is
  no separate boundary apparatus; you read the derived note before it lands. If real use ever leaks
  something that review didn't catch, a screening question earns its line in the promote prose then.
- **Into the instruction tier** (commons → rules), the flow is the same shape with a different write: the
  proposal is a rule file, the extra question is *"is this steering-grade — should it change how sessions
  behave?"*, and `promote` reads the existing rules first, because a graph built from sessions those
  rules steered will keep re-deriving them.

**Three trigger paths, in order of load-bearing-ness:**

1. **In-band:** any generated `/process` on a graph with `promotes-to:` ends by asking *"does any of this
   generalize?"* and puts candidates **in the same plan**. Fires because the pipeline fires; depends on
   no one remembering.
2. **Awareness:** mid-session, any work session may notice something commons-worthy and offer to promote —
   the reference's awareness protocol, generalized.
3. **Manual:** `/promote` invoked directly.

**The proposal bar is lean.** When uncertain, propose — a declined candidate costs one "skip" at plan
review; a missed observation is invisible damage. The screen, carried as prose in the generated skills:
strip the entities and see if a claim remains; method-over-material; non-obvious (would you tell your
future self in a *different* domain?); not already steering (check the target first). The interview
customizes it with one question: *"what in this domain must never leave, and what kind of thing tends to
generalize?"*

### D7 — Verification is the human gate, full stop

What stands between a `/process` run and a bad graph: the generated skill's conventions (D3), and the plan
approval you give every run. The session protocol keeps the reference's non-mechanical habits — read the
changelog and atlas at session start; report a change summary and append a changelog entry at session end.
No checker ships with the plugin. The reference's own checker has had latent bugs for a year — three note
types never validated, most vocabularies unenforced — and the graph thrives, which is the strongest
available evidence that the checker is not what keeps it alive.

---

## 5. Plugin components

```
plugins/knowledge-commons/
  .claude-plugin/plugin.json
  references/
    graph-conventions.md     # D3 in full: note shapes, frontmatter, map format, changelog format
    templates/
      process.md             # the orchestrator template
      knowledge-graph.md     # the graph-skill template
  skills/
    graph-init/SKILL.md      # the generator: interview → config + scaffold + generated skills
    promote/SKILL.md         # uniform cross-graph derivation (D6)
```

### graph-init

Two modes:

- **Full** (default): interview → write `.commons.yml` → scaffold the graph (atlas, `maps/`, type
  directories, empty changelog) → generate `process` and `knowledge-graph` skills into the project's
  `.claude/skills/`, with the interview's procedure answers written in as prose. For a graph whose
  `promotes-to:` names a commons that doesn't exist yet, offer to instantiate the commons first (it's a
  `graph-init` run with the commons preset: claims/principles/questions, no sources, no generated
  orchestrator).
- **Config-only** (`--config-only`): for an existing, working graph (the reference). Short interview —
  graph name, root, type names, `promotes-to:` — writes `.commons.yml` and touches nothing else. The
  existing skills stay exactly as they are; `promote` reads the config.

**The interview** (full mode), kept lean — target ~15 questions:

1. **Graph:** name (becomes `domain:` on everything it promotes), root, what it promotes to.
2. **Types:** what this domain calls its evidence and attractors; entities worth notes; a reference tier?
   sources that must be preserved verbatim?
3. **Sources:** what arrives on its own (chronicle glob, pasted URLs), how each resolves, what signal
   classes inspection should look for.
4. **Sinks:** where non-graph outputs go (task manager, trackers), with what approval mode.
5. **Procedure** (written into the generated skills as prose): walk one source through, start to finish —
   what gets created, in what order, and what else must update when evidence is created (attractor
   evidence sections, entity notes, maps). What's durable here vs. operational. What must never be
   captured.
6. **Judgment:** when uncertain, capture or skip — and which error costs more here? What tends to
   generalize out of this domain, and what must never leave?

### promote

Loads the source graph's config for one value (`graph.name` → `domain:`) and the target's config for
everything else (type names, directories, maps). Derives the candidate note, reads the target's attractor
maps for association, presents the proposal (note + map updates + any new question), writes on approval,
appends the target's changelog. When the target is the instruction tier, the write is a rule file and the
proposal includes the steering-grade question.

### `.commons.yml` (sketch — finalized against the first two instantiations)

A project graph:

```yaml
graph:
  name: orchard                  # becomes domain: on notes this graph promotes
  root: knowledge/
  atlas: atlas.md
types:
  evidence:   { name: observation, dir: observations/, supports: patterns }
  attractors:
    - { name: pattern,  dir: patterns/ }
    - { name: decision, dir: decisions/ }
  reference:  { name: reference, dir: reference/ }
sources:
  - { type: chronicle, path: docs/chronicle/, glob: "20*.md" }
sinks:
  - { name: tasks, skill: todoist-followups, approval: per-item }
promotes-to: ~/commons
```

The commons:

```yaml
graph:
  name: commons
  root: ~/commons
  atlas: atlas.md
types:
  evidence:   { name: claim, dir: claims/, supports: principles-or-questions }
  attractors:
    - { name: principle, dir: principles/ }
    - { name: question,  dir: questions/ }
  reference:  { name: reference, dir: reference/ }
# no sources:, no sinks: — nothing is processed into the commons (D5)
promotes-to: ~/.claude/rules/
```

### Note shapes (fresh-authored; full contract in `references/graph-conventions.md`)

```yaml
# claims/mulching before the first freeze cut winter loss.md
---
genitor: "[[claims]]"
tags: [practice]
date: 2026-07-14
domain: orchard                  # promoted notes only — the source graph's name
supports: ["[[timing beats technique for seasonal work]]"]
---
One self-contained paragraph. If it needs its source to make sense, it has not generalized.
```

```yaml
# principles/timing beats technique for seasonal work.md
---
genitor: "[[principles]]"
tags: [method]
---
## so what
Schedule the work window first; refine the method inside it.

## evidence
- [[mulching before the first freeze cut winter loss]] (orchard)
- [[deploy freezes before the holiday sale beat better runbooks]] (shopcraft)
```

Attractor map entry (the index line): `- [[timing beats technique for seasonal work]] — schedule the
window first; refine the method inside it`

---

## 6. Verification & acceptance

1. **Paper parity (G2):** while authoring the templates, fill them with the reference's answers and diff
   against the reference's actual skills. Divergences are triaged as deliberate generalization or template
   gap. No live swap; the reference keeps its hand-written skills. (The reference's location is a private
   detail, supplied by the author at build time — deliberately absent from this public spec.)
2. **The real gate:** instantiate the commons and one project graph (wellstead), `/process` real chronicle
   files, and judge the proposed notes by reading them. Then the first real promotion crosses into the
   commons under D6. **Proposal precision** — the fraction of proposals accepted unedited — is the
   quality signal, watched informally across the first ~2 weeks; sustained low precision means sharpening
   the generated prose from the declined examples, which is exactly what project-owned skills are for.

## 7. Phasing

| Phase | Work | Gate |
|---|---|---|
| **1** | Build the plugin (2 skills, 2 templates, conventions reference). Paper-parity diff against the reference. Instantiate the commons. | Templates fill cleanly with the reference's answers; commons scaffold exists |
| **2** | `graph-init` a first project graph (wellstead); `/process` real chronicles. | Real claims accepted from a real run; first promotion lands in the commons |
| **3** | `--config-only` on the reference graph; first cross-domain promotion from it. | A commons principle carries evidence from two domains |
| **4** | Second project graph (devbox). Register in `marketplace.json`; README. | Installable by a stranger |

The plugin stays unregistered until Phase 4 (per the unregistered-plugin exception in
`.claude/rules/plugin-updates.md`).

## 8. Risks & open items

- **R1. Cross-domain transfer may be rare.** The design keeps finding out cheap: the commons costs one
  scaffold and promotion rides existing `/process` runs. Phase 3's gate is the first evidence either way.
- **R2. Proposal precision at the abstraction level.** Deriving portable claims is harder than structured
  extraction against a tight work ontology. Watched informally (§6); the remedy is sharpening the
  project-owned prose, not adding machinery.
- **R3. The interview may not elicit a domain's procedure in one sitting.** Mitigated by drift-by-design:
  the generated skill is a starting point the project sharpens from real runs, not a contract.
- **R4. In-band promotion may under-fire in unbounded domains.** Accepted for v1; the chronicle queue
  keeps missed material discoverable, and NG5 names the evidence trigger for adding a sweep.
- **O1.** `.commons.yml` schema — finalized against the first two instantiations, not in the abstract.
- **O2.** The README naming convention (gerund skill names) doesn't fit `graph-init` / `promote` /
  generated `process`. Relax the convention in the build PR: names should be specific and
  intention-revealing; plugin namespacing (`knowledge-commons:promote`) supplies disambiguation.
- **O3.** Commons physical location and Obsidian vault registration (multi-machine, multi-user) — private
  instantiation details, settled at Phase 1, not specified here.
