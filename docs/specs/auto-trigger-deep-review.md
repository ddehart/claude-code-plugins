# Auto-Trigger Deep Review for Session Chronicle

## Problem

The session-chronicle skill has two modes of reflective practice evolution:

1. **Lightweight (step 6):** Scans the last 3 reflections for repetition or staleness. Runs every chronicle write.
2. **Deep review (`/session-chronicle reflect`):** Examines 5-10 entries for broader patterns. Manual invocation only.

The lightweight check's 3-entry window is too narrow to catch gradual convergence — the kind where each individual entry looks fine but the practice is slowly ossifying over weeks. The deep review catches this, but only fires when the user remembers to invoke it.

## Goals

- **Auto-escalation:** When enough entries accumulate without a practice evolution, automatically run the deep review inline during a chronicle write.
- **Preserve judgment:** The model should still be free to escalate to a deep review at any time if the lightweight check reveals stagnation, even well before the threshold.
- **No external state:** The threshold mechanism must work from existing files (chronicle entries + reflective-practice.md), not external counters or metadata.

## Non-Goals

- Changing the manual `/session-chronicle reflect` subcommand (it stays as-is, available anytime).
- Changing what the deep review *does* — only when it fires.
- Adding configuration or user-facing threshold settings.

## Design

### Escalation Model

Step 6 of the write workflow becomes a two-tier check:

1. **Count entries since last evolution.** Read `reflective-practice.md` and find the most recent dated entry in Evolution Notes. Count distinct chronicle files (`docs/chronicle/YYYY-MM-DD.md`) dated after that anchor.

2. **Decide which review to run:**
   - **If count >= 10:** Deep review is **mandatory**. Run the deep review process (see below) instead of the lightweight check.
   - **If count < 10:** Run the lightweight check as today (scan last 3 reflections). However, if the lightweight check reveals patterns warranting deeper examination — e.g., same framings recurring, seed questions producing consistently formulaic responses — the model **may** escalate to the deep review at its discretion.

### Counting Mechanics

- **Unit:** Files (calendar days), not individual session headers within files.
- **Anchor:** The most recent `#### YYYY-MM-DD` heading in the Evolution Notes section of `reflective-practice.md`.
- **No anchor exists:** If there are no dated evolution notes (fresh project, or legacy project with only the placeholder text), count all chronicle files. This ensures the first deep review triggers promptly.

### Evolution Notes Date Convention

Each entry in the Evolution Notes section of `reflective-practice.md` must be prefixed with a date heading:

```markdown
## Evolution Notes

#### 2026-04-05
Deep review ran; no changes warranted.

#### 2026-03-28
Retired "satisfaction-adjacent" question — became formulaic after repeated use.
Added question about friction points in tool interactions.
```

This convention must be:
- Documented in step 6 of the write workflow (where evolution notes are written)
- Reflected in the seed file (`assets/reflective-practice-seed.md`) with a comment or example
- Applied by the deep review workflow when it writes evolution notes

### Inline Deep Review Process

When the deep review fires inline (whether auto-triggered or discretionary), it:

1. Read `docs/chronicle/reflective-practice.md` (current approach)
2. Read all Reflection sections from entries since the last evolution note (not capped at 5-10 — the point is to examine the full accumulated window)
3. Notice:
   - Which prompts produced genuine insight vs. formulaic responses
   - What new questions or themes are emerging
   - Whether the reflective voice is developing or stagnating
4. Update `reflective-practice.md` with evolved questions and approach
5. Write the changes as a brief narrative in Evolution Notes (with `#### YYYY-MM-DD` heading), not just a list swap

This is the same process as the manual `/session-chronicle reflect`, except the read scope is "all since last evolution" rather than "last 5-10."

### No-Op Logging

When the deep review runs and finds nothing to change, it still writes a dated Evolution Note:

```markdown
#### 2026-04-05
Deep review ran; no changes warranted.
```

This resets the entry counter so the next mandatory trigger is ~10 entries later. Without this, the deep review would fire on every subsequent write once past the threshold.

### User Signal

The step 8 report (entry location, word count, memories promoted) gains an additional line when a deep review ran:

> Deep review triggered (12 entries since last evolution); reflective-practice.md updated.

Or for no-ops:

> Deep review triggered (10 entries since last evolution); no practice changes warranted.

## Changes Required

### SKILL.md

1. **Step 6:** Rewrite to include the entry-counting preamble and two-tier escalation logic. The lightweight check instructions remain but are now the "< 10" branch.

2. **"Evolving the Reflective Practice" section (line ~179):** Add auto-escalation as a third mode alongside "Continuous" and "Deep review." Document the threshold, counting mechanism, and no-op convention.

3. **Step 8:** Add deep review trigger to the report template.

4. **Deep review workflow:** Note that when invoked inline, scope is "all since last evolution" rather than "5-10 entries."

### reflective-practice-seed.md

Update the Evolution Notes section to show the date heading convention:

```markdown
## Evolution Notes

[This section grows over time. Each entry starts with a #### YYYY-MM-DD heading.]
```

### plugin.json / marketplace.json

Version bump per plugin update rule.

## Edge Cases

| Scenario | Behavior |
|---|---|
| Fresh project, first chronicle write | No evolution notes exist → count = 1. Lightweight check runs. |
| Legacy project, 20 entries, no dated evolution notes | Count = 20 (all entries). Deep review fires immediately on next write. |
| 10 entries accumulate but all on the same day | Count = 1 (files, not sessions). Lightweight check runs. |
| Model escalates discretionarily at entry 4 | Deep review runs, writes evolution note, counter resets. |
| Deep review finds nothing at entry 10 | No-op note written, counter resets. Next trigger at ~20 total entries. |
| User invokes `/session-chronicle reflect` manually at entry 7 | Manual deep review runs and writes evolution note. Counter resets. Next auto-trigger at ~17 total entries. |

## Risks & Open Questions

- **Context cost:** Reading all entries since last evolution could be substantial if 10+ multi-session days have accumulated. In practice, reflections are ~200 words each, so 10 entries ≈ 2K words — manageable.
- **Evolution Notes as counter state:** This is a soft convention, not enforced mechanically. A model that writes an undated evolution note breaks the counting. The spec mitigates this by being explicit about the date heading requirement in the instructions.
- **Discretionary escalation quality:** Giving the model permission to escalate before 10 relies on its judgment about stagnation. The anti-patterns guide helps calibrate this, but it's inherently subjective.
