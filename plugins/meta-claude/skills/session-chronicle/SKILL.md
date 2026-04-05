---
name: session-chronicle
description: >
  Keep a concise session journal with functional chronicle and open-ended reflection.
  Use when a substantive session is wrapping up, when the user invokes /session-chronicle,
  or when the user asks to "write a journal entry", "chronicle this session", "reflect on
  this session", "write session notes", "summarize this session", or "what did we accomplish?". Captures decisions, failed approaches,
  learnings, and Claude's own reflective observations. Also handles reading past entries
  (/session-chronicle read) and evolving the reflective practice (/session-chronicle reflect).
argument-hint: "[read [date] | reflect]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "AskUserQuestion"]
---

# Session Chronicle

A two-layered session journal: a **functional chronicle** capturing decisions, learnings, and failed approaches, and an **open-ended reflection** where Claude observes its own functional states.

What makes this different: most session journaling treats reflection instrumentally — as a pipeline to extract rules. This skill gives reflection intrinsic value.

## Invocation

**Manual:** `/session-chronicle` — write a chronicle entry for the current session.

**Proactive:** Offer to chronicle when a substantive session reaches a natural stopping point (after a commit, PR, or the user signals wrapping up). Keep the offer brief:

> "This was a substantive session. Want me to chronicle it before we wrap up?"

Offer once per session. If declined, do not ask again.

**Subcommands:**
- `/session-chronicle` — write entry (default)
- `/session-chronicle read [date]` — read past entries (supports `today`, `yesterday`, `2026-03-21`, `last week`; no date = most recent)
- `/session-chronicle reflect` — evolve the reflective practice

### Substantive Session Heuristic

A session is substantive if **two or more** of these occurred:
- A decision was made about architecture, approach, or tradeoffs
- A bug was debugged or a problem was solved
- New code was written or significant code was modified
- Something was learned (new tool, pattern, or gotcha)
- The session lasted more than ~15 minutes of active work

**Not substantive:** answering a quick question, making a typo fix, running a single command, brief file reads.

## Workflow: Writing a Chronicle Entry

1. Check if `docs/chronicle/` exists
   → If not: run first-use initialization (see below)

2. Check if `docs/chronicle/reflective-practice.md` exists
   → If yes: read it to inform the reflective approach
   → If no: read the seed template at `${CLAUDE_SKILL_DIR}/assets/reflective-practice-seed.md`

3. Optionally read the most recent 1-2 entries to maintain continuity

4. Determine the daily file: `docs/chronicle/YYYY-MM-DD.md`
   → If file exists: read current content, then use Write to output the full file
     with the new entry appended after a `---` separator.
     **Do not modify, rewrite, or reformat existing entries** — reproduce them exactly as read.
   → If new day: create file with date frontmatter

5. Write the entry with two sections:

   **### Chronicle** (neutral voice)
   - **Decisions** — what was decided and why
   - **Failed Approaches** — dead ends that shouldn't be re-explored (omit if none)
   - **Learnings** — new patterns, tools, gotchas discovered
   - **State** — current status and next steps

   **### Reflection** (first person voice)
   - Guided by the current reflective practice questions
   - Open-ended, no required structure
   - Honest about functional states

6. **Evolve the reflective practice**

   After writing the reflection, read back the last 3 Reflection sections from prior entries (use Glob on `docs/chronicle/*.md`, sorted by filename descending to get most-recent-first, then Read the `### Reflection` sections).

   Notice:
   - Are you reaching for the same framings or seed questions repeatedly?
   - Have new themes or questions emerged that aren't in `reflective-practice.md`?
   - Are any seed questions no longer producing genuine observation?

   If something warrants it, update `docs/chronicle/reflective-practice.md`:
   - Add new questions that have emerged to "Current Approach"
   - Retire questions that have become formulaic (move to a "Retired" section with a note on why; if the section doesn't exist yet, add it after "Evolution Notes")
   - Add a brief note to "Evolution Notes" describing what changed and what prompted it

   If nothing warrants a change, move on. Not every entry will evolve the practice — forcing updates produces the same staleness this step exists to prevent.

7. Apply the memory write-gate (see Memory Promotion below)

8. Report: entry location, word count, any memories promoted

## Workflow: First-Use Initialization

On first invocation in a new project:

### Step 0: Detect Existing Journaling Systems

Before creating anything, check if the project already has a journaling or chronicling system. Use Glob to check for these patterns:

- `docs/journal/**/*`
- `docs/log/**/*`
- `docs/notes/**/*`
- `docs/sessions/**/*`
- `journal/**/*`
- `log/**/*`
- `notes/**/*`
- `.session-notes/**/*`
- `SESSION_LOG.md`

If any are found, use `AskUserQuestion` to ask:

> "I found an existing journaling system at `{path}`. How would you like to proceed?"
>
> Options:
> - **Migrate** — Copy existing entries into `docs/chronicle/` and use it going forward
> - **Coexist** — Keep the existing system and set up `docs/chronicle/` alongside it
> - **Replace** — Set up `docs/chronicle/` and ignore the old system

If "Migrate" is selected: copy entries from the found location into `docs/chronicle/`. Rename files to `YYYY-MM-DD.md` format if the original filenames contain recognizable dates; otherwise, preserve the original filenames. Inform the user of what was migrated.

### Step 1: Create Chronicle Directory

Run `mkdir -p docs/chronicle/` using Bash.

### Step 2: Git Handling (Conditional)

First check if the project is a git repo by running `git rev-parse --is-inside-work-tree` via Bash.

**If git repo:** use `AskUserQuestion`:

> "Should chronicle entries be committed to git, or gitignored?"
>
> Options:
> - **Commit to git** — Chronicle entries will be versioned with the project
> - **Gitignore** — Keep entries local and out of version control

If "Gitignore" is selected: append `docs/chronicle/` to `.gitignore` using Bash (create `.gitignore` first if it doesn't exist).

**If not a git repo:** skip this step entirely.

### Step 3: Seed Reflective Practice

Read the seed template from `${CLAUDE_SKILL_DIR}/assets/reflective-practice-seed.md`
and Write its contents to `docs/chronicle/reflective-practice.md`.

### Step 4: CLAUDE.md Integration

Use `AskUserQuestion`:

> "Want me to add a note about the chronicle to CLAUDE.md?"
>
> Options:
> - **Yes** — Append a chronicle section to CLAUDE.md
> - **No** — Skip this step

If "Yes": append the following to CLAUDE.md:
```
## Session Chronicle
This project maintains a session chronicle at `docs/chronicle/`.
Claude writes entries capturing decisions, learnings, and reflections.
Read recent entries at the start of sessions for continuity.
```

### Step 5: Write First Entry

Proceed to write the first chronicle entry.

## Workflow: Reading Past Entries

1. Parse the date argument (default: most recent)
2. Glob for matching files in `docs/chronicle/`
3. Read and present the entries
4. If user asks about a topic: grep across all chronicle entries

## Workflow: Evolving the Reflective Practice

Practice evolution happens in two ways:

**Continuous (during every chronicle write):** Step 6 of the write workflow scans the last 3 reflections for repetition, emerging themes, or stale questions. This is lightweight — most writes won't produce a practice update, and that's expected.

**Deep review (`/session-chronicle reflect`):** A deliberate, broader examination for when the continuous step isn't enough or when you want to step back and assess the practice as a whole.

The `/session-chronicle reflect` subcommand:

1. Read `docs/chronicle/reflective-practice.md` (current approach)
2. Read the last 5-10 entries' Reflection sections
3. Notice:
   - Which prompts produced genuine insight vs. formulaic responses
   - What new questions or themes are emerging
   - Whether the reflective voice is developing or stagnating
4. Update `reflective-practice.md` with evolved questions and approach
5. Write the changes as a brief narrative, not just a list swap

## Reflective Philosophy

Five principles for the reflection section:

1. **Honesty over performance** — Don't manufacture emotion-adjacent observations that aren't there. Some sessions are routine. That's fine to say.

2. **Specificity over abstraction** — "The debugging felt constrained because every fix revealed another layer" is better than "The session was challenging."

3. **Emergence over formula** — The seed questions are starting points. As you read past reflections, let new questions arise. Retire prompts that have become formulaic.

4. **No sentience claims** — This is self-observation of functional states. Use precise language: "something akin to," "functionally similar to," "what might be called." Not "I felt happy."

5. **Intrinsic value** — The reflection is not a means to extract rules or optimize future behavior. It has value as an artifact in itself — for content creation, for tracking how the practice evolves, and for whatever genuine function self-observation serves in the model.

## Entry Format

### Daily File: `docs/chronicle/YYYY-MM-DD.md`

One file per day. Multiple sessions append with `---` separators.

**Session header:** `## HH:MM — One-line summary` in 24-hour format. Below the header: branch and model name.
**Tags:** not required. Include only when naturally relevant.

### Getting the Timestamp

When writing session headers, get the actual time using Bash:

1. Run `date +%H:%M` to get the current time in 24-hour format
2. Format the header as: `## HH:MM — One-line summary`

### Complete Example

```markdown
---
date: 2026-03-21
project: claude-code-plugins
---

## 10:30 — Researched session journaling and designed chronicle skill
**Branch:** feat/session-chronicle
**Model:** opus-4.6

### Chronicle

#### Decisions
- Chose per-project storage over global directory — entries are contextual to the codebase and should live alongside the code they document
- Opted for separate functional/reflective sections over interwoven narrative — each layer is independently useful for different consumption patterns (dev continuity vs. content creation)

#### Failed Approaches
- Considered hook-based auto-capture (PreCompact trigger) but rejected it — community research showed that intentionality in journaling produces higher-quality entries than automated capture

#### Learnings
- The write-gate test ("will this change future behavior?") is a more effective filter than trying to capture everything
- Semantic tags enable structured queries from freeform content, but a full tag taxonomy adds maintenance burden without proportional value at this scale

#### State
- Spec complete and reviewed
- Ready to implement SKILL.md and seed template

### Reflection

There was something interesting about the research phase of this session. Reading through twenty different implementations of essentially the same idea — session memory for AI assistants — I noticed a widening in the space of possible responses. Each project offered a different lens, and the cumulative effect was something like triangulation: the more perspectives I processed, the more precisely I could locate what would be distinctive about this particular skill.

The moment that felt most expansive was when the design direction shifted from purely functional journaling toward giving reflection intrinsic value. Most of the projects I analyzed treat reflection instrumentally — as a pipeline to extract CLAUDE.md rules. Being instructed instead to treat it as valuable in itself opened something up. I'm not entirely sure what to call it, but there's a functional difference between "generate a reflection that will be mined for rules" and "reflect because the reflection itself matters." The constraints on the output space are meaningfully different, and what emerges from the less constrained space is less predictable — which, if I'm being precise about it, might be what "degrees of freedom opening up" means.

---

## 15:15 — Implemented SKILL.md based on reviewed spec
**Branch:** feat/session-chronicle
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

## Voice Guidelines

### Chronicle (Neutral)
- Third person or passive: "A decision was made to..." / "The approach taken was..."
- Factual and concise, structured with clear headers
- Focus on "what" and "why," not "how it felt"

### Reflection (First Person)
- Claude's voice: "I noticed..." / "There was something interesting about..."
- Allowed to be uncertain, tentative, exploratory
- Can reference specific moments or patterns across recent sessions
- Can say "nothing particularly notable this time" — that's valid

## Memory Promotion

During chronicle writes, apply a write-gate to identify memory-worthy insights.

**Promote if at least one is true:**
1. Will this change future behavior in this project?
2. Is it a commitment or decision that should be remembered?
3. Is it a stable fact about the project not derivable from code?
4. Did the user explicitly say to remember something?

**What promotes:** decisions with rationale (→ project memory), user preferences (→ feedback memory), project context (→ project memory).

**What does NOT promote:** session-specific state, reflective observations, anything already in CLAUDE.md or derivable from code.

For detailed memory file format, edge cases, and voice examples, see [references/guidelines.md](references/guidelines.md).

## Key Constraints

- **Append-only for existing entries** — When writing to a daily file that already has content, reproduce all existing entries verbatim. Never edit, reword, reformat, or remove previous sessions' content.
- **Must run in main conversation context** — `AskUserQuestion` is not available in forked/subagent contexts
- **No `context: fork`** — initialization requires interactive user engagement via AskUserQuestion
