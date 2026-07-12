# Note Formats

The on-disk contract for every file in a knowledge commons graph. `knowledge-graph` writes to it;
`commons-check` validates against it; `process` proposes plans in its terms.

Notes are markdown files with YAML frontmatter. Links are Obsidian-style wikilinks (`[[Note title]]`),
resolved by filename within the graph root.

**All examples below are fresh-authored and illustrative.**

## Filenames

- **The filename is the note title.** `principles/Execution beats review for validating configuration.md`
  is linked as `[[Execution beats review for validating configuration]]`.
- **Evidence filenames are prefixed `YYYY-MM `** — space-separated:
  `claims/2026-07 A dry run caught a config error that review missed.md`. Because wikilinks resolve by
  filename, the prefix is part of the link target:
  `[[2026-07 A dry run caught a config error that review missed]]`. Attractors carry **no** date prefix —
  they are long-lived and their titles are stable link targets.
- **Titles must be filesystem-safe, so write them that way in the first place.** A title cannot contain `/`
  or `:`, cannot start with `.`, and should stay well under the filesystem's length limit. Do **not** write a
  title and then mangle it into a filename — the filename *is* the link target, so a mangled filename is a
  broken wikilink. Phrase the title so the question never arises (say "the npm Todoist CLI package", not
  "`@doist/todoist-cli`"), and keep the exact literal in the body where it belongs.
- **The date is the source's, not the processor's.** Both the filename prefix and the `date:` field record
  **when the thing happened** — the month of the session or call the claim was distilled from — not the day
  `/process` got around to reading it. This matters because staleness is measured against evidence dates:
  if `date:` were the processing date, working through a two-year backlog in an afternoon would make every
  attractor look freshly exercised.

  **Exception — a promoted note is dated by its promotion.** It passed through no source, so there is no
  source date to take; and the originating note's date is itself an engagement fact (a timeline), which is
  exactly what a cross-boundary promotion must not carry. Staleness in the receiving graph should measure
  from when the note entered *that* graph anyway.
- Directories come from `.commons.yml` type config, not from this file. `claims/`, `principles/`,
  `questions/`, `reference/` below are the personal-commons defaults.

## Evidence — e.g. `claim`

Atomic, provenanced, **must point at ≥1 attractor**.

```markdown
<!-- claims/2026-07 A dry run caught a config error that review missed.md -->
---
type: claim
date: 2026-07-08
domain: homelab                # provenance only — set by the processor, confirmed at plan approval;
                               # never a link, never content
supports:                      # ≥1 REQUIRED — enforced by knowledge-graph at write time
  - "[[Execution beats review for validating configuration]]"
---
One self-contained paragraph of substance. If it needs its source to make sense, it has not generalized.
```

The body is **one self-contained paragraph**. Not a bulleted list, not a section tree — a claim is one thing
someone could stand behind.

## Attractor — e.g. `principle`

Accumulates evidence. Has a "so what." Has a lifecycle.

```markdown
<!-- principles/Execution beats review for validating configuration.md -->
---
type: principle
status: provisional            # provisional | held | stale
---
## so what
Run the artifact in the environment it will actually run in before trusting any textual audit of it.

## evidence
- [[2026-07 A dry run caught a config error that review missed]]   (homelab)
```

- `## so what` is **one clause of consequence** — what changes because this is true. It is what the index
  renders. An attractor without a "so what" is a topic, not an attractor.
- `## evidence` is a bulleted list of wikilinks to evidence notes, each annotated with its `(domain)`.

**The claim's own `domain:` frontmatter is authoritative.** The `(domain)` on the bullet is a convenience for
a human reading the attractor — a cache, not the record. Count domains for graduation by **reading the
claims**, never by counting the annotations: the two can drift, and a stale annotation would otherwise
graduate an attractor that has not earned it. `commons-check` should treat a mismatch as a structural finding
and correct the annotation.

## Attractor — e.g. `question`

```markdown
<!-- questions/When is a checklist better than automation.md -->
---
type: question
status: open                   # open | graduated | abandoned  (positions 0 | 1 | 2)
---
## why I care
Automating a step removes the judgment that made it work, and the failures are quiet.

## partial answers
- [[2026-07 A dry run caught a config error that review missed]]   (homelab)
```

**`## why I care` is written by the processor** — the stake the source material shows, not a blank left for
the human to fill. It is proposed in the plan like everything else and confirmed at approval. A question with
an empty `## why I care` is a topic, and topics do not accumulate evidence.

A `question` declares `graduates-to: principle`, so reaching position 1 (`graduated`) does **not** merely
flip its status — it **derives a new `principle`** carrying the stance the question arrived at, and
re-points this note's evidence at it. The question then records what it became:

```markdown
---
type: question
status: graduated
---
## why I care
…
## became
[[Execution beats review for validating configuration]]
```

Flipping the status without deriving the principle strands the reasoning in a note now marked resolved.
See `mechanism.md` § Graduation may derive a new attractor.

## Reference

Lookup-retrieved facts. **Unbounded, never indexed, exempt from the attractor requirement.**

```markdown
<!-- reference/Wrangler config uses jsonc not toml.md -->
---
type: reference
domain: wellstead             # where it was learned — provenance, same as evidence
verified: 2026-07-08
---
Body: the fact, and how it was verified.
```

No `supports:` field. Reference notes do not point at attractors and are never rendered in the index — that
is exactly what lets them grow without bound.

They **do** carry `domain:`. It is not counted toward anything (reference has no lifecycle and never
graduates), but a fact you cannot trace to where you learned it is a fact you cannot re-verify when it goes
stale — and tool facts go stale constantly. Dropping provenance from an entire type would be a silent loss,
not a simplification.

## `index.md` — graph root

**Generated by `commons-check --index`. Committed. Never hand-edited.**

One line per attractor: **bold title** — the "so what" in one clause — `[domains]`. Claims and reference
**never appear**.

```markdown
# Index

_Generated by `commons-check --index` on 2026-07-12. Do not hand-edit._

## principles
- **Execution beats review for validating configuration** — run the artifact in the environment it will
  actually run in before trusting a textual audit. `[homelab, wellstead]`
- **A guard must be mechanical at the trigger point, not knowledge held** — knowing a rule does not make it
  fire. `[devbox, homelab]` ⚠️ graduation-pending
- **Confirmation is not authorization** — alignment on *what* does not license action on *when*. `[devbox]`

## questions
- **When is a checklist better than automation** — open. `[devbox, homelab]`
```

*Confirmation is not authorization* carries **no flag**: it is at position 0 on one domain, which is simply
unearned, not defective. The `graduation-pending` note has met the ≥2-domain bar and awaits the next
`/process` run to apply it.

Flags from `commons-check` are rendered inline. **The flag vocabulary is closed** — a generated file whose
vocabulary each run improvises is not a stable artifact, so do not invent new ones:

| Flag | Meaning |
|---|---|
| `⚠️ graduation-pending` | at **position 0** with evidence from ≥2 domains — has earned promotion, not yet applied |
| `⚠️ single-domain` | at **position 1** on evidence from one domain — was promoted early; flagged for demotion |
| `⚠️ stale` | no new evidence in N months |
| `⚠️ orphan` | at **position 0** with zero evidence |

Note that `⚠️ single-domain` is a **position 1** condition — it means an attractor was promoted on evidence
that did not earn it. A *position 0* attractor with single-domain evidence is not flagged at all: it simply
has not earned promotion yet, which is the normal, healthy state of most attractors and not a defect.

`⚠️ graduation-pending` exists because that state is real and lasts a whole cycle: `commons-check` flags
graduation, `/process` applies it on the next run, and in between the index must be able to say so.

Graduated and retired attractors carry no flag; they render their status (`graduated`) and, where they have
one, what they became.

Index size is a smoke alarm, not a wall: growth is controlled epistemically (graduation requires ≥2 domains),
not budgetarily.

## `changelog.md` — graph root

One dated bullet per **graph-shaping event**: what changed and why. Not a commit log — a record of why the
graph looks the way it does.

```markdown
# Changelog

## 2026-07
- **2026-07-12** — Promoted *Execution beats review for validating configuration* to `held`: a second domain
  (wellstead) produced supporting evidence, meeting the ≥2-domain graduation bar.
- **2026-07-08** — Opened *When is a checklist better than automation* after two claims pulled in opposite
  directions on the same question.
```

The current month lives in `changelog.md`. At month rollover the prior month is archived to
`changelog/YYYY-MM.md` and `changelog.md` starts fresh.
