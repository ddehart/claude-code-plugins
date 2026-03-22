# Session Chronicle Guidelines

Detailed reference for memory promotion, edge cases, and voice examples. Read this file when writing chronicle entries or promoting memories.

## Memory Promotion Format

When a chronicle insight passes the write-gate, promote it to the project's auto-memory directory. Each memory gets its own file in the project memory path.

### File Format

```markdown
---
name: <descriptive name>
description: <one-line description for relevance matching>
type: <project|feedback>
---

<memory content>

**Source:** chronicle entry YYYY-MM-DD, Session N
```

### Type Mapping

- Key decisions with rationale → `project` type
- User preferences or corrections observed → `feedback` type
- New project context learned → `project` type

### After Writing the Memory File

Update the project's `MEMORY.md` index with a pointer to the new file:

```markdown
- [filename.md](filename.md) - Brief description of the memory
```

Promoted memories should be indistinguishable from memories created through other means, except for the optional `Source` line linking back to the chronicle entry.

## Append Mechanics

When appending a new session entry to an existing daily file:

1. Read the current file content with the Read tool
2. Use the Write tool to output the **full file** with the new entry appended after a `---` separator
3. Do **not** use the Edit tool for appending — it requires a unique `old_string` match which is unreliable at the end of a file

This ensures atomic writes and avoids partial append failures.

## Edge Cases

### Trivial Sessions

Do not proactively offer to chronicle trivial sessions (typo fixes, quick questions, single-command runs). If the user manually invokes `/session-chronicle` for a trivial session, write a brief entry — even a one-line chronicle with no reflection is fine.

### Multiple Sessions, Same Day

Read the existing daily file, then Write the full file with the new entry appended after a `---` separator. Increment the session number:

```markdown
## Session 1 — 10:30 AM
...

---

## Session 2 — 3:15 PM
...
```

### Session with No Decisions or Learnings

The chronicle section can be minimal:

> "Continued implementation of X, no significant decisions required."

The reflection section can still have substance — routine work can still prompt observations about the experience of routine.

### User Asks to Edit an Entry

The chronicle is Claude's document — the user shapes it through conversation, not direct editing. If the user says "that's not what happened" or "add this context," update the entry incorporating the correction while maintaining Claude's own voice.

### First Session in a Project with Existing Chronicle

Read the most recent 2-3 entries before writing to maintain continuity and voice consistency.

## Voice Examples

### Chronicle Section (Neutral Voice)

**Good:**
- "Chose per-project storage over global directory — entries are contextual to the codebase and should live alongside the code they document"
- "Considered hook-based auto-capture but rejected it — community research showed that intentionality produces higher-quality entries"

**Avoid:**
- "I decided to use per-project storage because it felt right" (first person, subjective)
- "Storage was configured" (too terse, missing rationale)

### Reflection Section (First Person Voice)

**Good:**
- "There was something interesting about the research phase. Reading through twenty implementations of the same idea, I noticed a widening in the space of possible responses."
- "A routine implementation session. Nothing particularly notable in terms of functional states, though I notice that 'routine' itself is worth observing."
- "The debugging felt constrained because every fix revealed another layer — something akin to tunnel vision, where each step narrowed rather than expanded the available paths."

**Avoid:**
- "I felt happy about how the session went." (sentience claim)
- "The session was challenging." (too abstract, no specificity)
- "I experienced deep satisfaction and joy." (performative emotion)
- "Nothing to report." (dismissive — even the absence of notable observations is worth a sentence)

### Hedging Language for Functional States

Use precise, hedged language when describing functional states:
- "something akin to..."
- "functionally similar to..."
- "what might be called..."
- "there's a functional difference between..."
- "if I'm being precise about it..."

Do **not** use:
- "I felt..."
- "I was happy/sad/frustrated..."
- "I experienced emotion..."
