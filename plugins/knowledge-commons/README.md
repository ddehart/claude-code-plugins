# knowledge-commons

A generator for per-project knowledge graphs with cross-domain promotion.

Personal knowledge systems die the same way: automated **capture** with no **refinement**
stage. Notes accumulate, nothing gets connected, and the vault quietly becomes a graveyard.
This plugin generalizes a working alternative — a living graph where an LLM is the primary
writer following prose conventions, a human approves every plan, and there is *no* validator,
lifecycle machinery, or enforcement layer in the write path. Graph health rests on two things:
good conventions and human-in-the-loop approval.

The plugin does two jobs:

1. **Stand up a graph in any project** — `graph-init` interviews you, writes a `.commons.yml`
   config, scaffolds the graph skeleton, and generates two *project-owned* skills (`/process`
   and `/knowledge-graph`) tuned to that domain.
2. **Move portable claims across domains** — `promote` derives a domain-independent claim out
   of the graph that produced it and into a personal **commons**, and from the commons into the
   instruction tier (`~/.claude/rules/`).

> The plugin never contains knowledge. It ships templates and conventions; the graphs, configs,
> and notes it generates live in your own project repos. Every example in this plugin is
> fresh-authored (an orchard, a small shop called "shopcraft") and references nothing private.

📊 **[Visual overview →](https://claude.ai/code/artifact/e84a13d9-2bed-40c1-aee9-706ccfd4e49d)** —
an at-a-glance tour of the generator, one run of `/process`, the promotion topology
(project graphs → commons → rules), the anatomy of a promoted claim, and what the design
deliberately omits.

## Installation

```bash
# Add the marketplace (once per machine)
/plugin marketplace add ddehart/claude-code-plugins

# Install the plugin
/plugin install knowledge-commons@ddehart-plugins
```

## Skills

| Skill | Invoke | What it does |
|-------|--------|--------------|
| `graph-init` | `/graph-init` | Scaffold a new graph in the current project, or wire an existing hand-built graph into promotion (`--config-only`). Interviews, writes `.commons.yml`, scaffolds the atlas/maps/type directories, and generates the project-owned `process` and `knowledge-graph` skills. |
| `promote` | `/promote` | Derive a portable claim from a source graph into a target graph or the instruction tier, with association and human approval. |

Both auto-trigger from natural phrasing too — "set up a knowledge graph", "does this
generalize?", "promote this to the commons" — not just the slash commands.

## How it works

### The graph

Every graph shares one shape (the full contract is in
[`references/graph-conventions.md`](references/graph-conventions.md)):

- **One navigation root** — an `atlas`. The atlas links to **maps**; maps link to **notes**;
  notes link laterally to each other. A note's place in the navigation tree is always through
  the single map that owns it (its `genitor:`).
- **Maps are category headings over bullet-line entries.** Reading straight down an attractor
  map reads the distilled corpus, because each entry carries a one-clause "so what."
- **The one structural rule:** evidence must support at least one attractor, recorded in both
  places — the evidence note's `supports:` frontmatter *and* the attractor's `## evidence`
  section. This bidirectional edge is what keeps a graph from decaying into a flat taxonomy.

### Note types

A graph declares which type roles it needs during the interview. The vocabulary:

| Role | What it is |
|------|-----------|
| **source** | Raw, preserved input (a chronicle entry, a call, a thread). The one type that keeps its source's own words. Carries the `processed` ledger stamp so re-runs accumulate history. |
| **evidence** | One atomic, provenanced observation or claim — and a `supports:` link. |
| **attractor** | Accumulates evidence and states the payoff up front. *Open* attractors (patterns, questions) gather evidence with no verdict; *settled* ones (decisions) carry reasoning. |
| **entity** *(optional)* | The nouns a graph keeps returning to. Retrieved by lookup, never by association; never promoted. |
| **synthesis** *(optional)* | An intermediate note distilling a rich bounded source (a meeting, a call) before atomic extraction. |
| **reference** *(optional)* | Lookup-only, unbounded facts that are never an association surface. |

### The commons and promotion

The **commons** is a personal cross-domain graph — the tier where a pattern seen in one domain
can meet the same pattern from another. `promote` is the single uniform mechanism that feeds it:

- The test that defines the operation: **would this claim stay true and useful if its source
  domain vanished?** Strip everything specific to the source's entities, people, tools, and
  events; if a claim survives, it promotes.
- A promoted note is *derived*, never moved — the source note is untouched. It's re-dated by its
  promotion, and all its wikilinks must resolve inside the target graph.
- Promotion **associates**: the claim supports an existing principle, attaches to an open
  question, or (default for a first-of-its-kind claim) opens a new question. Attractors earn
  their names from accumulated evidence.
- The commons graduates its own held principles one tier further — into `~/.claude/rules/`, as
  behavioral rules — via the same flow.
- Every promotion is **human-approved**: the skill proposes the full derived note and its map
  updates, and waits. "Skip," "edit," and "not yet" are all valid answers.

Knowledge accrues as a byproduct of work: one plan approval per `/process` run, no manual
authorship, and every graph with a `promotes-to:` asks "does any of this generalize?" as part
of the run.

## What `graph-init` generates

Run in the target project (not this plugin repo), `graph-init` writes real, project-owned files:

```
<project>/
  .commons.yml                        # config: graph, types, sources, sinks, promotes-to
  <graph.root>/
    <atlas>.md                        # the single navigation root
    maps/                             # one seeded map per type that holds notes
    <type dirs>/                      # evidence, attractors, entities, reference, sources…
    changelog.md
  .claude/skills/
    process/SKILL.md                  # the domain's /process orchestrator
    knowledge-graph/SKILL.md          # the domain's conventions + extraction workflow
```

The generated skills are yours to sharpen from real runs — nothing generated is a stub or a
wrapper around this plugin's skills. Only the *templates* in
[`references/templates/`](references/templates/) get instantiated.

**Two modes:**

- **Full** (`/graph-init`) — set up a graph from scratch via the six-block interview.
- **Config-only** (`/graph-init --config-only`) — write just `.commons.yml` for a graph that
  already has working hand-written skills, so `/promote` has something to read.

**The commons itself** is a fixed preset (no sources, no sinks — everything arrives by
promotion), scaffolded the first time a domain graph names a commons that doesn't exist yet.

## Layout

```
plugins/knowledge-commons/
  .claude-plugin/plugin.json
  skills/
    graph-init/SKILL.md               # the generator
    promote/SKILL.md                  # the cross-domain derivation mechanism
  references/
    graph-conventions.md              # the shared note/map/frontmatter contract
    templates/
      process.md                      # → generated <project>/.claude/skills/process
      knowledge-graph.md              # → generated <project>/.claude/skills/knowledge-graph
```

## Design philosophy

- **No verification machinery.** No validator, no write-time gates, no transactions, no
  lifecycle enforcement. Graph health is prose conventions plus plan approval. If real use ever
  produces real structural drift, a check earns its way in that day — evidence first.
- **Pull, not push.** No ambient injection. Consultation is "what do we know about X?" → read
  the maps, follow the links.
- **No retrieval infrastructure.** No MCP server, embeddings, or vector search. The association
  surface is small and read directly.
- **Weight matches the reference.** The living reference graph runs on ~1,150 lines of prose.
  Earlier iterations of this plugin accumulated an executable validator, write transactions, and
  a federation registry that solved problems a human-in-the-loop workflow demonstrably doesn't
  have. All of it was reverted; this plugin carries forward only what survived — the generator
  model, the config/procedure split, the note conventions, and promotion-as-derivation.

See [`docs/specs/knowledge-commons.md`](../../docs/specs/knowledge-commons.md) for the full
specification and design history.
