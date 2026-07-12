---
name: commons-check
description: >
  Run the health check on a knowledge commons graph and regenerate its index. Checks structural integrity
  (every claim points at an attractor that exists), link containment, attractor graduation and demotion,
  staleness, and orphans. Use when asked to check the graph, audit the commons, find broken links or orphan
  notes, or regenerate index.md. Flags problems and lifecycle transitions; never applies them.
argument-hint: "[--index]"
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash"]
---

# Commons Check

The health check. It **enforces the structure** the mechanism depends on — and it does so by *reporting*,
not by fixing.

Read the contract first:

- `${CLAUDE_PLUGIN_ROOT}/references/mechanism.md` — the invariant, lifecycles, graduation rules
- `${CLAUDE_PLUGIN_ROOT}/references/note-formats.md` — note formats and the `index.md` line format

Load `.commons.yml` to resolve role → type name → directory. Never assume type names.

## The governing rule: flag, never apply

**`index.md` is the only file this skill writes.**

Every problem found and every lifecycle transition earned is **reported as a flag**. Flags are applied
during the next `/process` run, under plan approval — because a status change is a claim about what the
graph *means*, and those go through the human.

A check that silently repaired the graph would be a check you stop reading.

## Checks

Run all of them; collect and report together.

### Structural integrity

- Every evidence note carries ≥1 `supports:` entry. **Zero-support evidence is the cardinal violation** —
  report it loudly.
- Every `supports:` target resolves to an existing attractor file. Report dangling links with both ends.
- Every note has the frontmatter its type requires (`type:`, plus `date:`/`domain:` for evidence,
  `status:` for attractors, `domain:`/`verified:` for reference).
- **Every `(domain)` annotation on an attractor's evidence bullet matches that claim's own `domain:`.** The
  claim's frontmatter is authoritative; the annotation is a cache. Count domains from the claims. A drifted
  annotation is a structural finding — and a dangerous one, since counting the annotation instead of the
  claim would graduate an attractor that has not earned it.
- Filename matches the note's title, and evidence carries its `YYYY-MM ` prefix.

### Link containment

No wikilink resolves outside the graph root. A link that escapes is a structural boundary leak — report it
as such, not as a broken link.

### Lifecycle transitions

**The rules live in `mechanism.md` § Lifecycles. Apply them from there; do not restate them here** — a
second copy is a second thing to fix.

Two things that copy will not do for you, and that are the usual source of wrong flags:

- **Resolve every status by position, never by name.** The rules are stated as position 0 (proposed) → 1
  (earned) → 2 (retired), and each attractor type names those positions itself in its `lifecycle:` list. A
  `principle` calls position 1 `held`; a `question` calls it `graduated` and has no `held` at all. Flagging
  a question for promotion to `held` is a status the type cannot hold. **Read the name out of the type's own
  list.**
- **Honor `graduates-to:`.** If the graduating type declares it, graduation is not a status flip — it also
  derives a new attractor of the target type. Flag *both* halves, or the reasoning is stranded in a note
  that has just been marked resolved.

Two domains is the bar because a pattern that has only ever appeared in one domain is a local habit, not a
principle. Staleness is not wrongness — it is unexercisedness; the flag prompts a review, not a deletion.

**An attractor at position 0 on one domain is not a finding.** It is unearned, which is the normal state of
most attractors. Do not flag it. The flag vocabulary is closed (`note-formats.md`) — do not invent new ones.

**Report an inert lifecycle once, about the graph, not per note.** If every source tier declares the same
`domain:`, no attractor in the graph can ever reach position 1. Say that plainly at the top of the report —
once — rather than decorating every attractor with a flag that is really a property of the config.

### Orphans

An attractor **at position 0** with **zero** evidence. Either it was created speculatively, or its evidence
was never linked. Report it; the plan decides. No transition.

**Only position 0.** A graduated or retired attractor is finished, not orphaned — flagging it would mark
every graduated note as a defect forever.

## `--index` — regenerate the index

Rewrite `index.md` at the graph root, **wholesale**. Do not patch it; do not preserve hand edits (there
should be none — it is generated, and says so in its own header).

- **One line per attractor.** `**Bold title** — the "so what" in one clause — ` then the domains its
  evidence spans.
- **Attractors only.** Claims and reference notes **never** appear. This is what keeps the index a distilled
  corpus small enough to read whole, which is what makes association at `/process` time possible at all.
- Group by attractor type; render each attractor's flags inline, from the **closed vocabulary** in
  `note-formats.md` (`⚠️ graduation-pending`, `⚠️ single-domain`, `⚠️ stale`, `⚠️ orphan`). Do not invent a
  flag for a state the vocabulary lacks — if you need one, the vocabulary is wrong and should be fixed there.

Exact format is in `note-formats.md`.

Index size is a **smoke alarm, not a wall**. If it is growing uncomfortably, the answer is that attractors
are being promoted too readily — not that the index needs a budget. Growth is controlled epistemically.

## Report

Group findings by severity, and be concrete — every finding names its file:

1. **Violations** — zero-support evidence, dangling links, containment leaks. These break the mechanism.
2. **Transitions earned** — graduations, demotions. These are proposals for the next `/process`.
3. **Review prompts** — staleness, orphans.

Close by stating plainly where they go: *"These transitions are applied on the next `/process` run under
plan approval."* Do not offer to apply them here.

## Out of scope

The **LLM contradiction pass** — attractors that conflict with each other, evidence that undercuts the
attractor it supports — is a later phase (spec Phase 4). It is not implemented here. If asked for it, say
so rather than improvising a partial version: a contradiction check that misses contradictions is worse
than none, because it will be trusted.
