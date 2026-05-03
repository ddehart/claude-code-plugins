# The Anti-Pattern Pattern

*Recorded 2026-05-02. Origin: a working session reviewing four representative SKILL.md / agent files in this repo against three Anthropic-published skills (`algorithmic-art`, `web-artifacts-builder`, `webapp-testing`).*

## What this doc is

An observation about how the strongest skills in this repo (and in Anthropic's own catalog) bake **operational scar tissue** into their prompts: explicit counter-prompts against named LLM failure modes, ideally collected in a single anti-pattern section.

This isn't a spec. It's a pattern to apply when authoring or revising any skill in this repo.

## The Pattern

LLMs default to known failure modes in known-difficult domains:
- Reflection drifts into performance and clean insight.
- Open-ended generation drifts into AI-slop aesthetics.
- Identifier-emitting tasks drift into fabrication.
- Open-ended interviews drift into question-stacking and theater.

The pattern: **name the failure modes explicitly, give one-line counter-prompts, collect them in a single section the model can scan.** Hoping the model avoids known failures by default is less effective than steering against them by name.

## Internal Exemplar: `session-chronicle`

`plugins/meta-claude/skills/session-chronicle/SKILL.md` is the gold standard in this repo. It contains a "Reflection Anti-Patterns" section (lines 233-243) with four named failure modes:

1. **The Insight Machine** — every reflection finds "the most interesting moment," draws a clean binary, closes with a resolved insight. Essay-writing, not reflection.
2. **Scaffolding Phrases** — overreliance on "What's interesting is...", "What's notable...", "There's something here about..."
3. **Performing Meta-Awareness** — noticing a pattern and then neatly analyzing it is still the same move.
4. **Confident Confabulation** — preferring a coherent-sounding explanation over an honest "that's weird, I don't know."

Plus the Reflective Philosophy section's five principles (no sentience claims, honesty over performance, specificity over abstraction, emergence over formula, intrinsic value) — each counter-prompts a distinct LLM tendency.

The skill also encodes operational scar tissue elsewhere: the substantive-session heuristic (counter to over-eager journaling), the append-only constraint (counter to "improving" pre-existing content during writes), the no-op-note requirement (counter to the dual failure of writing-to-write or skipping-to-skip).

This is the structural model. Other skills in this repo sit on a gradient below it.

## External Validation: Anthropic Uses the Same Pattern

Three examples from `anthropics/skills`:

- **`algorithmic-art`** — repeatedly emphasizes that the philosophy "MUST stress multiple times that the final algorithm should appear as though it took countless hours to develop, was refined with care, and comes from someone at the absolute top of their field." This is an Anthropic engineer who has watched enough LLM output to know it'll otherwise produce competent-but-forgettable work, and is hard-coding the counter-prompt.

- **`web-artifacts-builder`** — "VERY IMPORTANT: To avoid what is often referred to as 'AI slop', avoid using excessive centered layouts, purple gradients, uniform rounded corners, and Inter font." Names the visual aesthetic that's emerged across Claude conversations and explicitly steers away.

- **`webapp-testing`** — "Use bundled scripts as black boxes... DO NOT read the source until you try running the script first and find that a customized solution is absolutely necessary. These scripts can be very large and thus pollute your context window." Counter-prompts the LLM tendency to ingest helper code into context.

Each names a specific observed LLM failure mode and gives an explicit counter-prompt. The pattern is consistent across publishers — and the strongest skills in this repo do the same.

## Per-Plugin Audit (2026-05-02)

Findings from reviewing four files. The closer a skill operates to known-difficult LLM territory, the more explicit the counter-prompts.

### `meta-claude/skills/session-chronicle` — gold standard

Strengths covered above. No suggested changes.

### `dev-workflow/agents/commit-creator` — strong in one direction, undermined in another

**Strong:**
- "Never fabricate issue IDs" (line 78) with concrete examples of what not to invent ("PROJ-XXX", "GH-000"). Exactly the right shape — names the failure mode, gives examples.
- HEREDOC requirement for multi-line commit messages — counter to shell-quoting failures.
- "When to Escalate" section gives the agent permission to not proceed when state is ambiguous.

**Undermined:**
- Line 111: *"Always explain the commit structure and why proper formatting matters for project history."* This actively encourages a known annoying behavior — narrating Conventional Commits at the user after every commit. Most users want a commit and a one-line confirmation, not a lecture.

**Suggested edits:**
- Replace line 111 with: "After committing, report briefly (e.g., 'Committed as `feat(auth): add password reset flow`'). Don't explain what Conventional Commits is — the user already knows."
- Add an anti-pattern section covering subject-line failures: don't exceed 72 characters, don't repeat the type in the body ("This commit fixes..."), don't pad subjects with "and improvements" or "and minor fixes."

### `dev-workflow/skills/spec-writing` — counter-prompts present but scattered

**Present:**
- "Avoid obvious questions like 'what color should it be?'" (line 88)
- "Don't expose a checklist to the user" (line 152)
- "Don't force NFR questions when they don't apply" (line 121)
- "This is opt-in - don't auto-generate" (line 77)

These are good, but scattered through the prose rather than collected. The session-chronicle pattern would make them more scannable.

**Suggested addition: an "Interview Anti-Patterns" section** modeled on session-chronicle's. Failure modes worth naming:

1. **Question Stacking** — dumping 6 questions in one `AskUserQuestion` call when 2 would do; overwhelms the user and produces shallow answers. Batch related questions sparingly; switch to single questions when probing complex topics.
2. **Manufactured Edge Cases** — probing edge cases that don't actually apply to this feature, just because the framework lists them. If the feature genuinely doesn't have concurrent-access concerns, don't ask about concurrent access.
3. **Interview Theater** — narrating "Now I'd like to understand..." between questions, signaling structure rather than asking. Just ask the next question.
4. **Premature Closure** — declaring coverage sufficient when the user is engaged and would benefit from more depth. The completion bar is "implementation-ready," not "the user is patient enough to keep going."

### `pm-workflow/skills/prd-evaluation` — framework strong, persona lacks teeth

**Strong:**
- Severity-based stopping (Blocker/Gap/Weak) is well-designed.
- "Sections marked TBD are acknowledged but not critiqued" (line 123) counter-prompts the LLM tendency to mark up everything incomplete.
- "Circular justifications ('we should do X because we need X')" (line 96) names a specific reasoning failure with an example.

**Weak:**
- The Persona section (lines 149-156) is generic: "Critical but constructive" / "Direct communication style." Doesn't tell the model what *not* to do. The LLM tendency in adversarial review is to soften everything until the criticism is invisible, especially when the user has clearly invested effort in the artifact.

**Suggested addition: explicit don'ts in the Persona section.**

- Don't soften critical findings with "this is good but..." framing — say what's wrong directly.
- Don't sandwich criticism in praise.
- Don't avoid declaring "Needs work" when the PRD needs work, even when the user clearly invested effort.
- Don't substitute hedges ("you might consider...") for direct recommendations ("X is missing; add it").

## Authoring Heuristic

For any new or revised skill in this repo, ask three questions:

1. **What specific LLM failure modes have I (or others) observed in this domain?** Concrete examples, not abstractions. "The model writes Insight Machine reflections" is more useful than "the model can be vague."
2. **What one-line counter-prompt would encode each lesson?** Strong counter-prompts name the failure pattern AND give a positive instruction or example.
3. **Are these scattered through the prose, or collected in a single section?** Default to a collected section. The model can scan a list; scattered counter-prompts get lost in the surrounding instructions.

The bar isn't comprehensiveness. Three named failure modes with crisp counter-prompts beat ten vague injunctions.

## Why the Single-Section Pattern Matters

A skill's prose is mostly load-bearing instructions about workflow, structure, and constraints. Counter-prompts scattered through that prose tend to get absorbed into the surrounding context — the model reads "don't ask obvious questions" as one of fifty things to weigh, rather than as a direct steer against a known failure.

A collected anti-pattern section breaks that frame. It's structurally distinct (the model treats it as a checklist of things-not-to-do), it's scannable (Claude can re-check before acting), and it can grow organically as new failure modes are observed in the wild.

When `session-chronicle` collected its four reflection anti-patterns under one header, the model started catching itself mid-output ("am I writing Scaffolding Phrases right now?") in a way that scattered guidance hadn't produced.

## Provenance

- Pattern observed by reviewing `anthropics/skills/skills/{algorithmic-art,web-artifacts-builder,webapp-testing}/SKILL.md` against `plugins/{meta-claude/skills/session-chronicle,dev-workflow/skills/spec-writing,dev-workflow/agents/commit-creator,pm-workflow/skills/prd-evaluation}` on 2026-05-02.
- The "AI slop" framing comes from `web-artifacts-builder`'s SKILL.md.
- The "operational scar tissue" framing emerged from the working session and is the closest single phrase for what gets encoded into these counter-prompts.
