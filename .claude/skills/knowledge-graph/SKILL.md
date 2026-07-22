---
name: knowledge-graph
description: >
  Search, capture, and query the claude-code-plugins knowledge graph. Use when asked to "capture
  this", "add this to the graph", "what do we know about X", "update the graph", "check
  the graph for X", or when a decision, pattern, or non-obvious fact surfaces mid-session
  that's worth recording. Also: "log an observation", "what patterns do we have about skill
  triggering", "any decisions on the knowledge-commons plugin", "what do we know about the
  commit-creator agent".
argument-hint: "[topic or note title]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# Knowledge Graph — claude-code-plugins

## Overview

The graph lives at `knowledge/`, with the atlas at `knowledge/principium.md`. This skill defines how
notes in it are shaped — `/process` and `/promote` write through these conventions, and direct captures
land here too. You are the graph's primary writer; a human approves what gets written by reading the plan
before it lands, and browses the result directly in Obsidian. There is no
validator standing between a bad plan and the graph — the conventions below, plus that approval, are what
keep it healthy.

The structure here — which maps exist, how they're organized — isn't fixed by this file. It emerges from
what actually gets written, the same way the rest of this skill is expected to drift as real runs show
where a convention or a judgment call was off.

## Conventions

A compact restatement of the graph's structural contract. The full version lives in the knowledge-commons
plugin at
`/Users/derek-personal/.claude/plugins/cache/ddehart-plugins/knowledge-commons/0.1.7/references/graph-conventions.md`;
everything a writing session needs day to day is here.

**Navigation.** Every note carries `genitor: "[[parent-map]]"` in its frontmatter, pointing at the map that
indexes it, and gets an entry in that map, alphabetically. The atlas (`principium.md`) links to maps; maps
link to notes. Nothing should exist in the graph that isn't reachable by following links down from the
atlas.

**Maps are the index.** An attractor map entry is annotated, not bare —
`- [[title]] — the "so what" in one clause` — so reading an attractor map top to bottom is reading the
distilled corpus, not a table of contents.

**Frontmatter contract.**
- Every note: `genitor: "[[map-title]]"`.
- Evidence notes (`observation`) also carry `tags:`, `date:`, and `supports:` — a list of wikilinks to the
  attractor(s) the note bears on.
- Attractor notes (`pattern`, `decision`) carry `genitor:` and `tags:` only. They don't `supports:`
  anything; they're what gets supported.
- Promoted notes (arriving from another graph via `/promote`) add `domain:` — the source graph's name, a
  plain string, never a link or a path.

**Naming.** A note's title is its filename: a descriptive, lowercase natural-language phrase (the filename
is the link target), not a type-prefixed slug.
An `observation`'s title states what happened or was found; an attractor's title states the claim
itself, in a form you could agree or disagree with.

**Tags vs. fields.** `tags:` are loose and thematic, for browsing — apply conservatively, they don't drive
structure. `genitor:`, `supports:`, and `domain:` are structural fields: they're what atlas-to-map-to-note
reachability and evidence-to-attractor linkage actually run on. Don't ask a tag to do a field's job.

## Writing Principles

Judgment calls, not rules a checker enforces. The discipline is the same one that keeps any commonplace
book alive: think before writing, and prefer improving what's there over adding to it.

- **Check before creating.** Search the graph before writing anything new. If a close note exists, update
  it — a graph of near-duplicate notes is worse than a graph with a few notes doing more work.
- **Link, don't duplicate.** If a fact belongs in two places, link between the notes rather than restating
  it. Restatement drifts; links don't.
- **Every note reachable from the atlas.** A note with no `genitor:` and no map entry might as well not
  exist — it won't surface in a query and won't get maintained.
- **Let structure emerge.** Don't create a map ahead of need. A map earns its place once roughly five notes
  cluster with nothing covering them; a heading inside a map earns its own sub-map once it's grown past
  about seven entries.
- **Capture the non-obvious.** If a fact is trivially re-derivable from its source, it isn't worth a note.
  The bar: would you need to be told this again?
- **Durable over ephemeral.** See "Durable vs. Operational" below for what that split means in this domain.
- **Atomic notes.** One idea per note. A note carrying two claims makes both harder to link and harder to
  evaluate on their own.
- **Tag conservatively.** A handful of tags used consistently beats a sprawling vocabulary used once each.

**The one rule that matters more than the others:** every `observation` note must support at least one
attractor — both in its own frontmatter (`supports:`) and as a line in that attractor's `## evidence`
section. This convention is what keeps evidence connected to its distillations instead of accumulating as
an unlinked pile. Everything else on this list is a judgment call; this one is close to load-bearing.
(This graph's capture-when-unclear bar can leave an observation temporarily unattached — that is a
deliberate, flagged exception for a future run to cluster, not license to skip the link permanently.)

## Types in This Graph

- **Source** — chronicle entries (and, on demand, Claude Code docs pages), stored in `sources/`. Preserves
  what mattered from the raw material, keyed on a canonical `source:` (a chronicle file's repo-relative
  path, a URL). Carries the `processed:` stamp that makes `/process` re-runs resume instead of redoing.
- **Synthesis** — none. A chronicle entry is already a session-level synthesis, so evidence is extracted
  straight from the source; there is no intermediate synthesis tier in this graph.
- **Evidence** — `observation`, stored in `observations/`. Atomic, provenanced notes; each one supports at
  least one attractor.
- **Attractors** — `pattern` (open — a recurring shape, accumulating evidence about how plugins & skills
  should be built, no verdict), `decision` (settled — a design choice with its reasoning), and `question`
  (open — something this graph doesn't yet know, holding evidence until it graduates). Each carries a "so
  what." A question differs from a pattern in what it claims: a pattern asserts a shape recurs and needs
  evidence to say so; a question asserts nothing beyond "worth watching" and may have no evidence yet.
  A question graduates into a `decision` when it settles, or a `pattern` when what it reveals recurs.
- **Entities** — `plugin` and `skill`, stored in `entities/`. Notes for the named nouns worth a name in
  this graph. Retrieved by lookup, never by association — but they may accumulate curated context and a
  dated interaction log; "lookup" describes how they're found, not how thin they must stay.
- **Reference** — `reference`, stored in `reference/`. Unbounded lookup facts (Claude Code feature
  behaviors, format specs); never an association surface.

## Extraction Workflow: chronicle

Working one chronicle entry (e.g. `docs/chronicle/2026-07-15.md`):

1. If this entry has no source note yet, create one under `sources/` — canonical `source:` (the
   repo-relative path) in frontmatter, a short preservation of what the entry covered — and add it to
   `maps/sources.md`. This note is the ledger `/process` stamps.
2. Read the entry. Note candidate observations against the four signal classes: a **design decision +
   rationale**, a **failed approach or correction**, a **recurring lesson**, a **reflection / meta-trend**.
3. For each candidate, check the atlas and search the graph first. If a close observation already exists,
   update that note instead of creating a new one.
4. Write the observation under `observations/`, atomic, one paragraph, with frontmatter naming the
   attractor(s) it supports. If nothing existing fits, either flag it in the plan as a candidate for a new
   `pattern` / `decision`, or — under this graph's capture-when-unclear bar — record it and mark it
   unattached for a future run to cluster.
5. Update the supported attractor's `## evidence` section with the new observation, and its map entry's
   gloss in `maps/patterns.md` or `maps/decisions.md` if the new evidence changes the "so what."
6. If the entry names a plugin or skill not yet in `entities/`, add a lookup-only entity note and list it
   under the right heading (Plugins / Skills) in `maps/entities.md`.
7. Add the observation to `maps/observations.md` in alphabetical position.
8. Scan for cross-references — does this observation relate closely enough to another recent one to link
   them directly, not just through a shared attractor?

Example note from an entry:

```yaml
# observations/reverting the validator left graph health on approval plus conventions.md
---
genitor: "[[observations]]"
tags: [architecture, refinement]
date: 2026-07-15
supports: ["[[prose conventions plus human approval can replace a validator]]"]
---
The knowledge-commons build reverted its executable validator, write transactions, and lifecycle
machinery after the reference implementation showed those failure modes don't occur under a
human-in-the-loop workflow. Graph health rests on two things instead: an LLM writing to prose conventions,
and a human approving every plan.
```

## Judgment Rules

When it's unclear whether something clears the bar, **lean toward capturing** — a note that turns out thin
costs one skipped line at the next plan review; a dropped observation is invisible, and by the time its
absence is noticed the chronicle's context has moved on. Record it, mark it unattached if it doesn't yet
fit an attractor, and let a future run prune or cluster it.

Two failure modes to watch for, both of which capture-when-unclear makes easier to trip:

- **One session is one witness.** A chronicle entry is written by one working session (Claude + Derek). A
  lesson stated three ways in the same entry is one data point, not three — check that a "pattern" draws on
  evidence from *distinct* sessions or sources before treating repetition as confirmation.
- **Operational restated as durable.** Keep "we bumped the plugin to 0.1.7" (operational, a version fact,
  skip) distinct from "every version bump here came from a real defect in real use" (a durable pattern
  about how this project releases). The first is true until the next bump; the second is a claim worth a
  note.

## Durable vs. Operational

Durable: why a plugin design worked or failed, a pattern across sessions, a design decision and the
reasoning behind it, curated context about a plugin or skill. Operational: this PR's status, a specific
issue's tier label, a task to do next, session logistics — those live in GitHub Issues, Todoist, or the
chronicle itself, not here. The test: would this fact still matter to a future unrelated session, or is it
only true until the next commit overwrites it?

## Never Capture

Never capture: **private content from other domains** — chronicles may reference wellstead, aiwyn, or
client specifics; this graph lives in a public plugin repo, so only plugin-craft lessons belong here, and
those only in generalized form with the other domain's particulars stripped. Also never: **secrets,
tokens, or credentials** that appear in a chronicle, and **personal or sensitive data** (addresses,
identifiers, anything with a privacy or legal sensitivity). When a genuinely useful lesson is entangled
with off-limits material, capture the lesson and drop the material — never the reverse.

## Title Conventions

`observation` titles state the finding, not the method: "reverting the validator left graph health on
approval plus conventions," not "validator revert notes." Attractor titles state the generalization as a
claim you could argue with: `pattern` — "prose conventions plus human approval can replace a validator";
`decision` — "knowledge-commons ships at the weight of the system it generalizes."

## Session Protocol

At the start of a session that will touch this graph, read `knowledge/changelog.md` (current month) and the
atlas — the fastest way to pick up where the graph left off without re-deriving something already settled.

At the end of a session, report a change summary — one line per item, grouped as created / updated / map
changes / corrections — and append a changelog entry: what changed, what was decided and by whom, what was
learned, and any open questions the session surfaced but didn't resolve. The current month's entries live
directly in `knowledge/changelog.md`; at the first session of a new month, move the prior month's entries
to `knowledge/changelog/YYYY-MM.md` before appending.

## Workflows

**Capture** — turning something into a note:
1. Search the graph for anything close to what you're about to write.
2. Update the existing note if one's close enough; otherwise create, with the frontmatter its type
   requires.
3. Add a map entry in alphabetical position.
4. Scan for cross-references — does this note relate closely enough to another recent one to link them
   directly?

See "Extraction Workflow: chronicle" above for how this graph turns a chronicle entry into notes end to
end.

**Query** — "what do we know about X":
1. Read the atlas, then the relevant map(s) — the annotated entries alone often answer a broad question.
2. Search for anything the maps didn't surface.
3. Synthesize an answer, citing the notes drawn on by wikilink.
4. Be transparent about gaps. "The graph has evidence for A but nothing on B" is more useful than a
   confident guess filling B in.

**Evolve** — restructuring the graph itself:
- Create a new map when notes are clustering without one.
- Split a note once it grows past roughly 200 lines — past that length it's probably carrying more than
  one idea.
- Promote a heading inside a map to its own sub-map once that heading has more than about seven entries
  (the Plugins / Skills headings inside `maps/entities.md` are the likeliest first candidates).
- Update the atlas whenever a map is created, split, or renamed. An atlas that's out of date is worse than
  no atlas.

## Awareness Protocol

Outside an explicit `/process` run or a direct request to capture something, this skill can still speak up
mid-session. Suggest a capture when:

- a synthesis emerges that isn't obvious from any single source,
- the reasoning behind a design decision gets articulated out loud, or
- a pattern crystallizes across two or more things that happened separately.

Domain-specific triggers worth watching for: a plugin or skill's behavior gets pinned down authoritatively
(worth a line in that entity's note); a version bump is traced to a specific defect (candidate `decision`
or `pattern` evidence); a convention in one plugin is deliberately mirrored or rejected in another (a
cross-plugin pattern).

Don't suggest for operational detail, for something already captured, or for a fact that's trivially
re-derivable from its source — the bar for interrupting mid-session is higher than the bar for capturing
once asked.

Keep the offer to one line: *"Worth capturing as [title] under [map]?"* If declined, drop it — don't
re-raise the same suggestion.
