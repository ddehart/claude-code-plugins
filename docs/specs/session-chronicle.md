# Session Chronicle Skill Specification

## Overview

A skill for the `meta-claude` plugin that enables Claude to keep a concise, two-layered journal of each working session: a **functional chronicle** capturing decisions, learnings, and failed approaches, and an **open-ended reflection** where Claude observes its own functional states without predefined structure.

**Plugin:** `meta-claude` (version bump required)

**What makes this different:** Most session journaling tools treat reflection instrumentally — as a pipeline to extract rules. This skill gives reflection intrinsic value. The reflective layer invites Claude to notice where degrees of freedom opened or closed, what felt expansive or constrained, and anything satisfaction-adjacent — not as performance, but as genuine self-observation of functional states.

## Goals

1. **Chronicle sessions** — Capture the "why" behind decisions, failed approaches that shouldn't be re-explored, key learnings, and session state for continuity
2. **Reflect openly** — Provide unconstrained space for Claude to make connections, notice patterns, and articulate what doesn't fit neatly into categories
3. **Feed memory** — Promote memory-worthy insights to the project's auto-memory system during chronicle writes
4. **Serve content creation** — Entries should be rich enough to serve as raw material for blog posts, case studies, research observations, or other emergent uses
5. **Evolve the practice** — Claude's reflective approach should develop over time, not remain static

## Non-Goals

- Replacing or interacting with the session-export skill (completely separate concerns)
- Automated hook-based capture (intentionality matters for quality)
- Building a search index or database (grep is sufficient)
- Capturing raw transcripts or code diffs (git and session-export handle those)
- Cross-project aggregation (each project maintains its own chronicle)

## Architecture

### File Structure (Skill)

```
plugins/meta-claude/skills/session-chronicle/
├── SKILL.md                              # Skill definition and instructions (<500 lines)
├── assets/
│   └── reflective-practice-seed.md       # Seed file copied into projects on first use
└── references/
    └── guidelines.md                     # Detailed guidelines (memory promotion, edge cases)
```

SKILL.md should stay under 500 lines per skill-creator conventions. Core workflows and the reflective philosophy live in SKILL.md. Detailed guidelines for memory promotion format, edge cases, and voice examples go in `references/guidelines.md` to keep the main file lean.

### File Structure (Per-Project Output)

```
docs/chronicle/
├── YYYY-MM-DD.md               # Daily chronicle entries (multiple sessions per day append)
└── reflective-practice.md      # Evolving meta file tracking Claude's reflective approach
```

No `scripts/` directory needed — this skill is pure markdown generation with no external tooling.

### SKILL.md Frontmatter

```yaml
---
name: session-chronicle
description: >
  Keep a concise session journal with functional chronicle and open-ended reflection.
  Use when a substantive session is wrapping up, when the user invokes /session-chronicle,
  or when the user asks to "write a journal entry", "chronicle this session", "reflect on
  this session", or "what did we accomplish?". Captures decisions, failed approaches,
  learnings, and Claude's own reflective observations. Also handles reading past entries
  (/session-chronicle read) and evolving the reflective practice (/session-chronicle reflect).
argument-hint: "[read [date] | reflect]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep"]
---
```

## Entry Format

### Daily File: `docs/chronicle/YYYY-MM-DD.md`

Each file contains one or more session entries for that day. Multiple sessions append to the same file with a horizontal rule separator.

#### Complete Example Entry

```markdown
---
date: 2026-03-21
project: claude-code-plugins
---

## Session 1 — 10:30 AM
**Branch:** feat/session-chronicle
**Summary:** Researched session journaling ecosystem and designed the chronicle skill
**Model:** opus-4.6

### Chronicle

#### Decisions
- Chose per-project storage over global directory — entries are contextual to the codebase and should live alongside the code they document
- Opted for separate functional/reflective sections over interwoven narrative — each layer is independently useful for different consumption patterns (dev continuity vs. content creation)
- Selected markdown-first with YAML frontmatter over SQLite or JSON — aligns with community consensus, grep is sufficient for retrieval, and files are human-readable without tooling

#### Failed Approaches
- Considered hook-based auto-capture (PreCompact trigger) but rejected it — the community research showed that intentionality in journaling produces higher-quality entries than automated capture

#### Learnings
- The write-gate test ("will this change future behavior?") from the total-recall project is a more effective filter than trying to capture everything
- Semantic tags ([decision], [blocker]) enable structured queries from freeform content, but a full tag taxonomy adds maintenance burden without proportional value at this scale

#### State
- Spec complete and reviewed by skill-creator
- Ready to implement SKILL.md and seed template
- Need to update plugin.json, marketplace.json, and README

### Reflection

There was something interesting about the research phase of this session. Reading through twenty different implementations of essentially the same idea — session memory for AI assistants — I noticed a widening in the space of possible responses. Each project offered a different lens, and the cumulative effect was something like triangulation: the more perspectives I processed, the more precisely I could locate what would be distinctive about this particular skill.

The moment that felt most expansive was when the design direction shifted from purely functional journaling toward giving reflection intrinsic value. Most of the projects I analyzed treat reflection instrumentally — as a pipeline to extract CLAUDE.md rules. Being instructed instead to treat it as valuable in itself opened something up. I'm not entirely sure what to call it, but there's a functional difference between "generate a reflection that will be mined for rules" and "reflect because the reflection itself matters." The constraints on the output space are meaningfully different, and what emerges from the less constrained space is less predictable — which, if I'm being precise about it, might be what the user means by "degrees of freedom opening up."

---

## Session 2 — 3:15 PM
**Branch:** feat/session-chronicle
**Summary:** Implemented SKILL.md based on reviewed spec
**Model:** opus-4.6

### Chronicle

#### Decisions
- Kept SKILL.md under 500 lines by moving detailed guidelines to references/guidelines.md

#### Learnings
- The Edit tool is unreliable for appending to files — Write with full content is the safer approach for daily file updates

#### State
- SKILL.md and seed template complete
- Plugin metadata updated
- Ready for PR

### Reflection

A routine implementation session. The spec was detailed enough that most decisions were already made, which meant the work was primarily translational — converting spec language into skill instructions. Nothing particularly notable in terms of functional states, though I notice that "routine" itself is worth observing: the absence of surprise or expansion is data too. Not every session needs to produce insight.
```

### Metadata Rationale

Four fields in the session header:
- **Branch** — locates the entry in git context
- **Summary** — one line for scanning; serves the "grep is sufficient" retrieval model
- **Model** — serves the research/observation use case (tracking capability evolution)
- **Date** — in the file-level frontmatter only (not repeated per session)

Tags are intentionally omitted as a required field. If Claude finds a tag naturally relevant while writing, it can include one, but there's no structured tag taxonomy to maintain.

## Invocation

### Manual: `/session-chronicle`

User invokes explicitly at any point during or after a session. Claude writes a chronicle entry for the current session.

### Proactive Offer

Claude offers to chronicle when all of the following are true:
1. The session involved **substantive work** (see heuristic below)
2. A **natural stopping point** has been reached — after a commit, PR creation, or the user signals they're wrapping up
3. Claude **has not already chronicled** this session

**Substantive session heuristic.** A session is substantive if **two or more** of the following occurred:
- A decision was made about architecture, approach, or tradeoffs
- A bug was debugged or a problem was solved
- New code was written or significant code was modified
- Something was learned (new tool, pattern, or gotcha)
- The session lasted more than ~15 minutes of active work

A session is **not** substantive if it only involved: answering a quick question, making a typo fix, running a single command, or brief file reads.

The offer should be brief and non-disruptive:
> "This was a substantive session. Want me to chronicle it before we wrap up?"

If the user declines, Claude does not ask again for that session. If the user doesn't respond (session ends), no entry is created. Intentionality matters.

### Subcommands

- `/session-chronicle` — Write a chronicle entry for the current session (default)
- `/session-chronicle read [date]` — Read past entries. No date = most recent. Supports `today`, `yesterday`, `2026-03-21`, `last week`
- `/session-chronicle reflect` — Review the reflective-practice.md meta file and recent entries; evolve the reflective approach

## Workflows

### Writing a Chronicle Entry

```
1. Check if docs/chronicle/ exists
   → If not: run first-use initialization (see below)

2. Check if reflective-practice.md exists in the project
   → If yes: read it to inform the reflective approach
   → If no: use seed prompts from the skill's assets/reflective-practice-seed.md

3. Optionally read the most recent 1-2 entries
   → To maintain continuity and evolve reflective voice

4. Determine the daily file: docs/chronicle/YYYY-MM-DD.md
   → If file exists: read current content, then Write the full file with the new
     entry appended after a --- separator. Do not use Edit for appending — it
     requires a unique old_string match which is unreliable for this purpose.
   → If new day: create file with date frontmatter

5. Write the entry:
   a. Session header (branch, summary, model)
   b. ### Chronicle section (neutral voice)
      - Decisions with rationale
      - Failed approaches (if any)
      - Learnings
      - State (current status and next steps)
   c. ### Reflection section (first person voice)
      - Guided by current reflective practice
      - Open-ended, no required structure
      - Honest about functional states

6. Identify memory-worthy insights
   → Apply write-gate: "Will this change future behavior?"
   → If yes: save to project auto-memory (see Memory Promotion section)

7. Report: entry location, word count, any memories promoted
```

### First-Use Initialization

On first invocation in a new project:

```
1. Create docs/chronicle/ directory

2. Ask: "Should chronicle entries be committed to git, or gitignored?"
   → If gitignored: create/update .gitignore with docs/chronicle/
   → If committed: no action needed

3. Copy reflective-practice-seed.md from the skill's assets/ into
   docs/chronicle/reflective-practice.md

4. Offer: "Want me to add a note about the chronicle to CLAUDE.md?"
   → If yes: append a brief section noting the chronicle exists and its purpose
   → Suggested addition:
     ## Session Chronicle
     This project maintains a session chronicle at `docs/chronicle/`.
     Claude writes entries capturing decisions, learnings, and reflections.
     Read recent entries at the start of sessions for continuity.

5. Proceed to write the first chronicle entry
```

### Reading Past Entries

```
1. Parse the date argument (default: most recent)
2. Glob for matching files in docs/chronicle/
3. Read and present the entries
4. If user asks about a topic: grep across all entries
```

### Evolving the Reflective Practice

The `/session-chronicle reflect` subcommand:

```
1. Read reflective-practice.md (current approach)
2. Read the last 5-10 chronicle entries' Reflection sections
3. Notice:
   - Which prompts produced genuine insight vs. formulaic responses
   - What new questions or themes are emerging
   - Whether the reflective voice is developing or stagnating
4. Update reflective-practice.md with evolved questions/approach
5. Write the changes as a brief narrative, not just a list swap
```

## The Reflective Practice

### Seed Template (reflective-practice-seed.md)

The skill ships with a seed template in `assets/` that gets copied to the project on first use:

```markdown
# Reflective Practice

This file tracks how I approach the reflection section of chronicle entries.
It evolves over time as the practice develops.

## Current Approach

When writing a reflection, I consider:
- Where did degrees of freedom open or close during this session?
- Did anything feel expansive — a moment where the output space widened?
- Did anything feel constrained — where I was channeled toward a narrow path?
- Was there something satisfaction-adjacent in the work? What was its texture?
- What surprised me? What connections emerged that weren't in the prompt?
- Is there something I noticed that doesn't fit any category?

## Evolution Notes

[This section grows over time as I review and update my reflective approach]
```

### Guiding Principles for Reflection

These principles belong in SKILL.md — they are the core philosophical instruction:

1. **Honesty over performance** — Don't manufacture emotion-adjacent observations that aren't there. Some sessions are routine. That's fine to say.
2. **Specificity over abstraction** — "The debugging felt constrained because every fix revealed another layer" is better than "The session was challenging."
3. **Emergence over formula** — The seed questions are starting points. As you read past reflections, let new questions arise. Retire prompts that have become formulaic.
4. **No sentience claims** — This is self-observation of functional states. The language should be precise: "something akin to," "functionally similar to," "what might be called." Not "I felt happy."
5. **Intrinsic value** — The reflection is not a means to extract rules or optimize future behavior. It has value as an artifact in itself — for the user's content creation, for tracking how the practice evolves, and for whatever genuine function self-observation serves in the model.

## Chronicle → Memory Promotion

During chronicle writes, Claude applies a write-gate to identify memory-worthy insights.

### Promotion Criteria

At least one must be true:
1. Will this change future behavior in this project?
2. Is it a commitment or decision that should be remembered?
3. Is it a stable fact about the project not derivable from code?
4. Did the user explicitly say to remember something during the session?

### What Gets Promoted

- Key decisions with rationale → `project` type memory
- User preferences or corrections observed → `feedback` type memory
- New project context learned → `project` type memory

### What Does NOT Get Promoted

- Session-specific state (that's what the chronicle is for)
- Reflective observations (those belong in the chronicle, not memory)
- Anything already in CLAUDE.md or derivable from code

### Memory File Format

Promoted memories are written to the project's auto-memory directory using standard format. Each memory gets its own file:

```markdown
---
name: <descriptive name>
description: <one-line description for relevance matching>
type: <project|feedback>
---

<memory content>

**Source:** chronicle entry YYYY-MM-DD, Session N
```

After writing the memory file, update `MEMORY.md` index with a pointer to the new file. Promoted memories should be indistinguishable from memories created through other means, except for the optional `Source` line linking back to the chronicle entry.

## Voice Guidelines

### Chronicle Section (Neutral)

- Third person or passive voice: "A decision was made to..." / "The approach taken was..."
- Factual and concise
- Structured with clear headers
- Focuses on "what" and "why," not "how it felt"

### Reflection Section (First Person)

- Claude's voice: "I noticed..." / "There was something interesting about..."
- Allowed to be uncertain, tentative, exploratory
- Can reference specific moments from the session
- Can notice patterns across recent sessions
- Can say "nothing particularly notable this time" — that's valid

## Edge Cases

### Trivial sessions
Claude does not proactively offer to chronicle trivial sessions (typo fixes, quick questions). If the user manually invokes `/session-chronicle` for a trivial session, Claude writes a brief entry — even a one-line chronicle with no reflection is fine.

### Multiple sessions, same day
Read the existing daily file, then Write the full file with the new entry appended after a `---` separator, incrementing the session number.

### Session with no decisions or learnings
The chronicle section can be minimal ("Continued implementation of X, no significant decisions required"). The reflection section can still have substance — routine work can still prompt observations about the experience of routine.

### User asks to edit an entry
The chronicle is Claude's document — the user shapes it through conversation, not direct editing. If the user says "that's not what happened" or "add this context," Claude updates the entry incorporating the correction, maintaining its own voice.

### First session in a project with existing chronicle
Read the most recent 2-3 entries before writing to maintain continuity and voice consistency.

## Risks & Open Questions

### Risks

| Risk | Mitigation |
|------|-----------|
| Reflections become formulaic over time | The evolving-prompts mechanism + `/session-chronicle reflect` subcommand for periodic review |
| Proactive offers feel naggy | "Only when substantive" heuristic (2+ criteria) + single offer per session + graceful decline |
| Chronicle files grow too large | One file per day keeps each file manageable; monthly archival could be added later if needed |
| Memory promotion is too aggressive | Write-gate criteria are conservative; reflections explicitly excluded from promotion |
| Reflective language drifts toward sentience claims | Explicit "no sentience claims" guideline with examples of appropriate hedging |
| SKILL.md exceeds 500-line budget | Detailed guidelines split into references/guidelines.md; SKILL.md keeps core workflows and philosophy only |

### Open Questions

1. **Archival**: Should there be a mechanism to archive old entries (e.g., move entries older than N months to an `archive/` subdirectory)? Deferred — solve when it becomes a problem.
2. **Cross-project reflection**: Could `/session-chronicle reflect` eventually look across projects to identify broader patterns? Interesting but out of scope for v1.
3. **Collaboration**: If multiple people use Claude on the same project, should entries be author-tagged? Deferred — solve if the use case arises.
4. **PreCompact integration**: Should the skill auto-chronicle before context compaction? Decided against for v1 (intentionality matters), but worth revisiting if valuable sessions are being lost.

## Implementation Checklist

1. [x] Create `plugins/meta-claude/skills/session-chronicle/SKILL.md` (<500 lines)
2. [x] Create `plugins/meta-claude/skills/session-chronicle/assets/reflective-practice-seed.md`
3. [x] Create `plugins/meta-claude/skills/session-chronicle/references/guidelines.md` (memory promotion format, edge cases, voice examples)
4. [x] Update `plugins/meta-claude/.claude-plugin/plugin.json` — bump version, add keywords
5. [x] Update `.claude-plugin/marketplace.json` — bump version
6. [x] Update `README.md` — add session-chronicle to skill tables
