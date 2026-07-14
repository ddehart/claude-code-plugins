# Graph conventions

This is the shared contract for every knowledge-commons graph — the reference implementation, a
project's own graph, and the commons itself. A generated `process` or `knowledge-graph` skill points
here instead of restating it. If you're a session reading or writing notes in one of these graphs,
this file tells you the shape a compatible note has to take.

The examples below use a fresh, invented world (an orchard's project graph, and a small shop called
"shopcraft" as a second domain) so the conventions read against real-looking content without
referencing anything private.

## Navigation

A graph has one navigation root: `atlas.md`. The atlas links to maps; maps link to notes. Notes link
to each other freely — lateral edges are the point — but a note's place in the *navigation tree* is
always through the one map that owns it, named in its `genitor:`.

- **Every note carries `genitor: "[[parent-map]]"`** in its frontmatter, and is entered as a bullet
  in that map. For a map itself, the genitor points at whatever owns it — the atlas, or (for a
  promoted sub-map) the parent map it was split out of.
- **Every note is entered in its map alphabetically**, grouped under whatever category headings the
  map uses. Alphabetical within a heading, not across the whole file.
- **Every note is entered somewhere in the atlas's reachable tree.** A note that exists on disk but
  isn't linked from any map is not part of the graph — it's just a file.
- **Maps are never created empty.** Stub maps waiting to be filled are how taxonomies happen instead
  of graphs. Create a map when roughly five notes cluster with no existing map covering them; until
  then, those notes live under whatever map is the closest fit, or under a general heading in the
  atlas.
- **Promote a map heading to its own sub-map once it holds around seven or more entries.** The
  sub-map's genitor points back at the map it came from; the parent map replaces the heading's
  bullet list with a single link to the new sub-map.

## Map format

A map file is category headings over bullet-line entries. Each line has one job: name the note and,
for attractors, say why it matters.

```markdown
# Patterns

## Pruning
- [[thin before petal fall not after]] — schedule thinning to land before petal fall, not after
- [[stub cuts heal faster than flush cuts on stone fruit]] — leave a short stub, don't flush-cut

## Frost & timing
- [[three consecutive frost warnings beat a fixed date for cover crop cover]] — watch the forecast, not the calendar
```

The **first wikilink on a bullet line is the entry** — the note this line is indexing. Any wikilinks
that appear later on the same line are annotations, not additional entries: they're there because
the "so what" clause happens to reference another note, not because the line indexes two things.

**Attractor entries carry an annotation: an em-dash followed by the note's "so what" in one clause.**
This is what makes a map more than a table of contents — reading straight down an attractor map is
reading the distilled corpus. Evidence, entity, and reference entries don't need the annotation
(the note title usually carries enough information on its own), though a short clarifying clause is
fine when the title alone would be ambiguous.

## Frontmatter contract

Every note has `genitor` and `tags`. Everything past that depends on the note's type role.

| Field | Required on | Notes |
|---|---|---|
| `genitor` | every note | `"[[parent-map]]"` — quoted, since `[[...]]` isn't valid bare YAML |
| `tags` | every note | a YAML list, never inline `#hashtags` in the body |
| `date` | dated notes only | source notes tied to a dated input; evidence tied to a dated observation. Attractors and reference notes are usually undated — they're accumulating, not point-in-time |
| `source` | source notes | the canonical pointer this note is keyed on (see below) |
| `supports` | evidence notes | one or more `"[[attractor-title]]"` links — the structural rule, see below |
| `processed` | source notes | a YAML list of stamps; see Source note |
| `domain` | promoted notes only, in the receiving graph | the source graph's `graph.name`, plain text, never a link |

**Tags: 2–5 per note, and always a genuine hierarchy candidate.** A tag is worth having only if it
would be useful as a retrieval axis at every level someone might search it — `pruning`, not
`pruning-technique-notes-2026`. If a piece of metadata doesn't need to support hierarchical
retrieval — it's a fact you'd look up, not a category you'd browse — it belongs as a frontmatter
field, not a tag. `date:` is a field because nobody browses "all notes tagged 2026-06-02"; `pruning`
is a tag because someone will ask "what do we know about pruning."

**`source:` is canonical and stable**, not just descriptive: a chronicle file's repo-relative path
(`docs/chronicle/2026-06-02-early-summer-thinning.md`), a recording URL, a thread permalink. It's
the key the ledger is keyed on — re-running `process` on the same input has to resolve back to the
same source note by matching this field.

**`domain:` never resolves.** It's a plain string naming the graph a promoted note came from, not a
wikilink and not a path. A promoted note's other wikilinks (`supports:`, body links) must resolve
inside the *target* graph — a promoted claim that still links back into its origin graph hasn't
actually generalized.

## Note shapes

### Source note

Raw and preserved — this is the one note type that keeps its source's own words rather than
distilling them. It carries the ledger stamp: a list of `processed` runs, so a source's history
accumulates instead of being overwritten each time `process` touches it again.

```yaml
# sources/2026-06-02-early-summer-thinning.md
---
genitor: "[[sources]]"
tags: [chronicle]
date: 2026-06-02
source: docs/chronicle/2026-06-02-early-summer-thinning.md
processed:
  - date: 2026-06-03
    ran: [observations, pattern-updates]
    skipped: [cider-block section — no durable content]
    errored: []
---
Thinned the Gala and Honeycrisp rows this week, three days ahead of petal fall on the Galas and
right at it on the Honeycrisps. Gala drop in the June self-thin looked noticeably lighter than last
year's rows, which were thinned about a week later. Didn't get to the cider block — next pass.
```

A later re-run against a grown version of the same chronicle file appends a second entry to
`processed` (with its own `date:` and `ran:` list) rather than replacing the first — the stamp is a
history, not a status.

### Evidence note

Atomic and provenanced. One observation, one claim, one paragraph — and a `supports:` link, because
an evidence note that supports nothing is a dead end (see the structural rule below).

```yaml
# observations/thinning before petal fall halved the june drop.md
---
genitor: "[[observations]]"
tags: [pruning, timing]
date: 2026-06-02
supports: ["[[thin before petal fall not after]]"]
---
Gala rows thinned in the three days before petal fall dropped roughly half as much fruit in the June
self-thin as the same rows thinned about a week later last season. Consistent across the five rows
checked this pass; Honeycrisp wasn't compared since both years were thinned at petal fall.
```

### Attractor note

Accumulates evidence and states the payoff up front. Two required sections: `## so what` (the
actionable consequence, one or two sentences) and `## evidence` (a bullet list of the notes that
back it).

```yaml
# patterns/thin before petal fall not after.md
---
genitor: "[[patterns]]"
tags: [pruning]
---
## so what
Schedule thinning passes to land before petal fall; a pass that slips past it does less work for the
same labor.

## evidence
- [[thinning before petal fall halved the june drop]]
```

**In a receiving graph — the commons, or any graph an attractor was promoted into — evidence
entries carry a domain annotation** so a reader can see at a glance how many domains back the claim:

```yaml
# principles/timing beats technique for seasonal work.md
---
genitor: "[[principles]]"
tags: [method]
---
## so what
Schedule the work window first; refine the method inside it.

## evidence
- [[mulching before the first freeze cuts winter loss]] (orchard)
- [[deploy freezes before the holiday sale beat better runbooks]] (shopcraft)
```

The `(domain)` suffix only appears where evidence arrived by promotion. Inside the orchard graph
itself, every entry is already local, so there's nothing to annotate.

### Question note

Where a claim that doesn't yet support any attractor lands, so it's captured without forcing a
premature attractor into existence.

```yaml
# questions/fixed calendar window vs triggered timing.md
---
genitor: "[[questions]]"
tags: [method]
---
## question
Some domains describe good timing as a fixed calendar window ("before the first freeze"); this one
claim describes it as event-triggered ("after three consecutive frost-risk nights"). One data point
isn't enough to say whether the triggered framing generalizes better, or whether it's just how this
particular domain happens to talk about the same thing.

## evidence
- [[three consecutive frost warnings beat a fixed date for cover crop timing]] (orchard)
```

A question note reads like a thin attractor — same two-part shape, `## question` standing in for
`## so what` — because that's what it is: an attractor that hasn't earned its name yet. When enough
evidence accumulates (typically once a second domain's claim lands under it), it's promoted in place
to a proper attractor.

### Entity and synthesis notes (domain-optional)

Two type roles some graphs declare and some don't, so their shapes are set per domain rather than here:

- **Entity notes** name the nouns a graph keeps returning to. They're retrieved by lookup (you know the
  name you want), never by association — but they may accumulate curated context sections and a dated
  interaction log where the domain calls for it. Entities never promote across graphs.
- **Synthesis notes** are an optional intermediate between a rich bounded source (a call, a meeting) and
  the atomic evidence extracted from it: one note distilling the event, carrying `source:` provenance as
  a wikilink to the source note, and listing what was extracted. Thin transactional sources skip this
  tier entirely.

### Reference note

Lookup-only, unbounded, never an association surface — nothing should ever `supports:` a reference
note, and a reference note never sits in an attractor's `## evidence` list.

```yaml
# reference/usda hardiness zone lookup by zip.md
---
genitor: "[[reference]]"
tags: [tool]
---
USDA plant hardiness zones are looked up by ZIP code at planthardiness.ars.usda.gov. The zone gives
the average annual minimum winter temperature band — useful for sanity-checking a frost-date
assumption against the wrong region.
```

## Naming

**Filenames are lowercase natural language, because the filename is the link target.** A note titled
"Thin Before Petal Fall Not After" would force every wikilink to it to reproduce that exact casing;
lowercase avoids the friction entirely. Spaces are fine in filenames — `[[thin before petal fall not
after]]` is a valid, readable wikilink.

**Date prefixes are for notes that are themselves a dated event**, not a stamp added out of habit.
A source note tied to a specific day's chronicle file earns the prefix
(`2026-06-02-early-summer-thinning.md`) because the date is part of what the note *is*. An
observation, a pattern, a claim — none of these are dated events, so none of them get a date prefix,
even though some carry a `date:` field in frontmatter.

**Maps are named for their concept, not their mechanism** — `patterns.md`, not `pattern-index.md` or
`pattern-map.md`. The map file's own title is what appears as the link text everywhere it's
referenced.

## Changelog

`changelog.md` at the graph root records why the graph looks the way it does — not what content it
holds (the maps already show that), but the sequence of decisions and sessions that shaped it.

**One entry per session that changed the graph.** Each entry names the date, what changed (notes
created, maps split, a promotion sent or received), what was decided along the way and why, what was
learned that isn't obvious from the notes themselves, and any open question the session left behind.

The current month's entries live directly in `changelog.md`. At the start of a new month, the prior
month's entries move to `changelog/YYYY-MM.md`, and `changelog.md` keeps a one-line pointer at the
top listing the archived months. A session reading `changelog.md` at the start of its work sees only
the current month plus the archive index — not the graph's entire history inline.

## Writing principles

- **Check before creating.** Search the graph before writing a new note; if something close already
  exists, update or link it instead of duplicating.
- **Link, don't duplicate.** If two notes are saying the same thing from different angles, that's a
  signal to merge them or to make one `supports:` the other, not to let both stand alone.
- **Every note is reachable.** A note with no path back to the atlas — per Navigation, above — isn't
  part of the graph, whatever it says on disk. Worth a check before ending a session.
- **Capture the non-obvious.** A fact trivially re-derivable from its source isn't worth its own
  note — the source note already preserves it. A note earns its place by adding interpretation,
  pattern, or judgment the raw source doesn't state.
- **Durable over ephemeral.** Operational facts — amounts, dates, statuses, anything that changes on
  its own schedule — live in the operational system that owns them (a task tracker, a calendar, a
  ledger), not in the graph. The graph holds what stays true after the operational fact has changed
  or expired.
- **Atomic notes.** One idea per note. A note that's really two ideas stapled together is two notes
  that happen to share a file.
- **The one structural rule: evidence must support at least one attractor, in two places at once.**
  The evidence note's `supports:` frontmatter names the attractor, and the attractor's `## evidence`
  section names the evidence note back. Both directions have to be true — a `supports:` link with no
  matching entry in the attractor, or an evidence entry with no `supports:` field, is a broken edge.
  This one convention is the difference between a graph that accumulates lateral connections and a
  vault that's quietly become a taxonomy: every other convention here is about navigation and shape,
  but this is the one that keeps notes actually talking to each other.
