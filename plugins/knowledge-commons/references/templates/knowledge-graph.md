---
name: knowledge-graph
description: >
  Search, capture, and query the {graph.name} knowledge graph. Use when asked to "capture
  this", "add this to the graph", "what do we know about X", "update the graph", "check
  the graph for X", or when a decision, pattern, or non-obvious fact surfaces mid-session
  that's worth recording.
  <!-- SLOT: description-triggers — append domain-specific trigger phrases built from the
  evidence/attractor type names in .commons.yml, e.g. for an orchard graph: "log an
  observation", "what patterns do we have about pruning", "any decisions on the gala
  block" -->
argument-hint: "[topic or note title]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

> Every `{value}` in this file is filled from `.commons.yml` and the generation interview.
> Nothing in braces, and no SLOT comment, should remain in the skill this produces.

# Knowledge Graph — {graph.name}

## Overview

The graph lives at `{graph.root}`, with the atlas at `{graph.root}/{graph.atlas}`. This skill is the only
thing that creates or edits notes in it. You are the graph's primary writer; a human approves what gets
written by reading the plan before it lands, and browses the result directly in Obsidian. There is no
validator standing between a bad plan and the graph — the conventions below, plus that approval, are what
keep it healthy.

The structure here — which maps exist, how they're organized — isn't fixed by this file. It emerges from
what actually gets written, the same way the rest of this skill is expected to drift as real runs show
where a convention or a judgment call was off.

## Conventions

A compact restatement of the graph's structural contract. The full version lives in the plugin's
`references/graph-conventions.md`; everything a writing session needs day to day is here.

**Navigation.** Every note carries `genitor: "[[parent-map]]"` in its frontmatter, pointing at the map that
indexes it, and gets an entry in that map, alphabetically. The atlas links to maps; maps link to notes.
Nothing should exist in the graph that isn't reachable by following links down from the atlas.

**Maps are the index.** An attractor map entry is annotated, not bare —
`- [[title]] — the "so what" in one clause` — so reading an attractor map top to bottom is reading the
distilled corpus, not a table of contents.

**Frontmatter contract.**
- Every note: `genitor: "[[map-title]]"`.
- Evidence notes also carry `tags:`, `date:`, and `supports:` — a list of wikilinks to the attractor(s)
  the note bears on.
- Attractor notes carry `genitor:` and `tags:` only. They don't `supports:` anything; they're what gets
  supported.
- Promoted notes (arriving from another graph via `/promote`) add `domain:` — the source graph's name, a
  plain string, never a link or a path.

**Naming.** A note's title is its filename: a descriptive, lowercase natural-language phrase (the filename
is the link target), not a type-prefixed slug.
An evidence note's title states what happened or was found; an attractor note's title states the claim
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

**The one rule that matters more than the others:** every `{evidence-type}` note must support at least one
attractor — both in its own frontmatter (`supports:`) and as a line in that attractor's `## evidence`
section. This convention is what keeps evidence connected to its distillations instead of accumulating as
an unlinked pile. Everything else on this list is a judgment call; this one is close to load-bearing.

## Types in This Graph

- **Source** — {source-type-or-none}, stored in `{source-dir}`. Preserves raw material as received, keyed
  on a canonical `source:` (a chronicle file's repo-relative path, a URL). Carries the `processed:` stamp
  that makes `/process` re-runs resume instead of redoing.
- **Synthesis** — {synthesis-type-or-none}. An optional intermediate for rich bounded sources (a call, a
  meeting): one note distilling the whole event, from which atomic evidence is then extracted. It links
  back to its source note and lists what was extracted from it. Thin transactional sources don't need
  one — evidence comes straight from the source.
- **Evidence** — `{evidence-type}`, stored in `{evidence-dir}`. Atomic, provenanced notes; each one
  supports at least one attractor.
- **Attractors** — {attractor-type-list}. Accumulate evidence; each carries a "so what."
- **Entities** — {entity-type-or-none}. Notes for the nouns worth a name in this graph. Retrieved by
  lookup, never by association — but they may accumulate curated context and a dated interaction log if
  the domain calls for it; "lookup" describes how they're found, not how thin they must stay.
- **Reference** — {reference-type-or-none}, stored in `{reference-dir}`. Unbounded lookup facts; never an
  association surface.

<!-- SLOT: extraction-workflows — the domain's procedure for turning one source into graph notes: what
gets created, in what order, and what else must update (attractor `## evidence` sections, entity notes,
map entries). Written from interview block 5 ("walk one source through, start to finish"). Replace the
example below with this graph's actual source-to-note pipeline; keep the same level of step-by-step
concreteness. -->

## Extraction Workflow: {source-type}

Working a `{source-type}` — here, one entry from an orchard logbook (`journal/2026-06-02.md`):

1. If this entry has no source note yet, create one under `sources/` — raw content preserved, canonical
   `source:` in frontmatter — and add it to the sources map. This note is the ledger `/process` stamps.
2. Read the entry. Note candidate observations: anything that could stand alone as evidence — a decision
   made, a result observed, a technique tried.
3. For each candidate, check the atlas and search the graph first. If a close observation already exists,
   update that note instead of creating a new one.
4. Write the observation under `observations/`, atomic, one paragraph, with frontmatter naming the
   pattern(s) it supports. If nothing existing fits, flag it in the plan as a candidate for a new pattern
   or a line under an open question.
5. Update the supported pattern's `## evidence` section with the new observation, and its map entry's
   gloss if the new evidence changes the "so what."
6. If the entry names a grove, cultivar, or tool not yet in `entities/`, add a lookup-only entity note.
7. Add the observation to `maps/observations.md` in alphabetical position.
8. Scan for cross-references — does this observation relate closely enough to another recent one to link
   them directly, not just through a shared pattern?

Example note from that entry:

```yaml
# observations/late pruning on the gala block delayed bud break by 9 days.md
---
genitor: "[[observations]]"
tags: [pruning, timing]
date: 2026-06-02
supports: ["[[pruning window sets the whole season's timing]]"]
---
Pruned the gala block on 3/15 instead of the usual late-February window (weather). Bud break landed 9
days later than the block's five-year average — consistent with the pattern that pruning date, not
pruning technique, is what shifts the season.
```

<!-- SLOT: judgment-rules — the capture-vs-skip bar for this domain, which error costs more (missed
observation vs. cluttered graph), distinctions that must not be collapsed, and known failure modes of
plausible-looking notes that turn out to be noise. From interview block 6. -->

## Judgment Rules

When it's unclear whether something clears the bar, lean toward capturing — a note that turns out thin
costs one skipped line at the next plan review; a dropped observation is invisible, and by the time its
absence is noticed the source context is gone.

The failure mode to watch for in this graph: a note that sounds like a pattern but is really one grower's
habit restated twice. Two data points from the same source aren't two data points — check who or what
generated each piece of evidence before treating repetition as confirmation. Keep "the tree needs less
water in a drought" (operational, re-derivable, skip) distinct from "watering on a fixed schedule
underperforms watering by soil-moisture reading, across three seasons" (a pattern, worth a note).

<!-- SLOT: durable-vs-operational — what counts as durable knowledge worth a note in this graph vs. an
operational fact that belongs elsewhere (a log, a tracker, a calendar). From interview block 5. -->

## Durable vs. Operational

Durable: why a technique worked or failed, a pattern across seasons or blocks, a decision about how the
orchard is run and the reasoning behind it. Operational: this week's harvest tally, a specific irrigation
valve's schedule, a supplier's phone number — these live in the farm log or the spreadsheet, not here. The
test: would this fact still matter in three years, or is it only true until the next entry overwrites it?

<!-- SLOT: never-capture — what must never be captured in this graph: sensitive personal data, other
people's private information, anything with a legal or safety sensitivity specific to the domain. From
interview block 5. -->

## Never Capture

Never capture: disputes naming a specific person's conduct, financial figures (costs, prices, wages), or
anything else the domain marked off-limits during setup. Those live in the private farm ledger, not here.

<!-- SLOT: title-conventions (optional) — a domain-specific naming pattern for note titles, if the
interview surfaced one (block 5). Omit this section entirely if the graph uses the default: a descriptive
sentence-case phrase, no type prefix. -->

## Title Conventions

Observation titles state the finding, not the method: "late pruning on the gala block delayed bud break by
9 days," not "pruning experiment results." Pattern titles state the generalization as a claim you could
argue with: "pruning window sets the whole season's timing," not "pruning timing."

## Session Protocol

At the start of a session that will touch this graph, read the current month's `changelog.md` and the
atlas — the fastest way to pick up where the graph left off without re-deriving something already settled.

At the end of a session, report a change summary — one line per item, grouped as created / updated / map
changes / corrections — and append a changelog entry: what changed, what was decided and by whom, what was
learned, and any open questions the session surfaced but didn't resolve. The current month's entries live
directly in `changelog.md`; at the first session of a new month, move the prior month's entries to
`changelog/YYYY-MM.md` before appending.

## Workflows

**Capture** — turning something into a note:
1. Search the graph for anything close to what you're about to write.
2. Update the existing note if one's close enough; otherwise create, with the frontmatter its type
   requires.
3. Add a map entry in alphabetical position.
4. Scan for cross-references — does this note relate closely enough to another recent one to link them
   directly?

See "Extraction Workflow" above for how this graph turns a `{source-type}` into notes end to end.

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
- Promote a heading inside a map to its own sub-map once that heading has more than about seven entries.
- Update the atlas whenever a map is created, split, or renamed. An atlas that's out of date is worse than
  no atlas.

## Awareness Protocol

Outside an explicit `/process` run or a direct request to capture something, this skill can still speak up
mid-session. Suggest a capture when:

- a synthesis emerges that isn't obvious from any single source,
- the reasoning behind a decision gets articulated out loud, or
- a pattern crystallizes across two or more things that happened separately.

<!-- SLOT: awareness-triggers (optional) — domain-specific awareness triggers beyond the three generic
ones above, from interview blocks 5–6: recurring situations in this domain where something capture-worthy
surfaces mid-session (e.g. for an orchard graph: a supplier answers a cultivar question authoritatively —
worth a line in that cultivar's entity note). Omit if the interview surfaced none. -->

Don't suggest for operational detail, for something already captured, or for a fact that's trivially
re-derivable from its source — the bar for interrupting mid-session is higher than the bar for capturing
once asked.

Keep the offer to one line: *"Worth capturing as [title] under [map]?"* If declined, drop it — don't
re-raise the same suggestion.
