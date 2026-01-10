# Spec-Writing Skill Specification

## Overview

A skill that takes a minimal spec or prompt and interviews the user to produce a comprehensive, implementation-ready specification. Inspired by the workflow where Claude asks 40+ questions using `AskUserQuestion` to collaboratively refine requirements.

**Skill name:** `spec-writing`
**Location:** `plugins/dev-workflow/skills/spec-writing/SKILL.md`

## SKILL.md Frontmatter

```yaml
---
name: spec-writing
description: >
  Interview users to refine rough ideas into comprehensive, implementation-ready
  specifications. Use when the user wants to write a spec, refine requirements,
  flesh out a feature idea, or asks to be interviewed about a project. Triggers:
  "help me spec", "interview me", "refine this spec", "flesh out", "requirements
  gathering", "write a spec for", "spec out".
allowed-tools:
  - AskUserQuestion
  - Read
  - Glob
  - Grep
  - Write
---
```

**Field rationale:**
- `name`: Lowercase with hyphen, matches directory name
- `description`: Under 1024 chars, includes trigger terms for auto-discovery
- `allowed-tools`: Enables interviewing, codebase exploration, and spec writing without permission prompts
- No `context: fork` - interview must stay in main conversation (see constraint below)
- No `model` override - use conversation default

### Critical Constraint: No Forked Context

**`AskUserQuestion` is not available in subagent/forked contexts.** This was verified empirically:

1. Created a custom agent with explicit `tools: AskUserQuestion`
2. Invoked the agent via Task tool
3. Agent reported: "No such tool available: AskUserQuestion"

This means the spec-writing skill **cannot** be implemented as:
- A delegated subagent (via Task tool)
- A skill with `context: fork`

The skill **must** run in the main conversation context to conduct interactive interviews. This is a hard platform constraint, not a design preference.

## Core Behavior

### Interview Process

1. **Read initial input** - Accept spec via file reference (`@path/to/spec.md`) or inline content in chat
2. **Explore codebase** - Proactively read relevant project files to generate contextual questions (depth determined by spec needs)
3. **Conduct interview** - Ask questions using `AskUserQuestion` until comprehensive coverage is achieved
4. **Write spec** - Generate structured spec document and write to file

### Question Strategy

**Flow:** Goals first - start with "why" and user outcomes before diving into "how"

**Pacing:** Adaptive
- Batch 2-4 related questions for efficiency
- Switch to single questions when probing deeper on complex topics

**Quality criteria** - Good questions should:
- Probe assumptions the user might take for granted
- Surface edge cases, failure modes, and boundary conditions
- Force tradeoffs between competing concerns

**Technical depth:** Always push toward concrete implementation details, even when the initial spec is vague

**No hard limit** - Continue interviewing until comprehensive coverage, even if 50+ questions

### Handling Unknowns

When the user doesn't know the answer:
- Suggest common approaches/options
- Provide a recommendation with reasoning
- Let user pick, modify, or defer to TBD

### Completion

- **Skill decides** when coverage is sufficient based on internal tracking
- **User can exit early** ("that's enough", "let's wrap up")
- On early exit: write spec from answers so far, mark gaps explicitly

### Scope Management

If answers reveal the spec is actually multiple features:
- Call out the scope expansion
- Suggest splitting into separate specs
- Let user decide whether to continue or narrow scope

## Iteration Support

First-class support for refining existing specs:
- Detect when pointed at an existing spec with content
- Read and analyze existing sections
- Identify thin areas or gaps
- Interview specifically about those gaps (not re-asking resolved questions)

## Output Format

### Structure

**Flexible/emergent** - Sections emerge from interview content rather than a rigid template. Common sections might include:
- Overview / Problem Statement
- Goals & Non-Goals
- User Stories / Use Cases
- Technical Approach (layered by concern when spanning UI/API/DB/etc.)
- Edge Cases & Error Handling
- Risks & Open Questions (dedicated section)

### Layered Sections

For specs spanning multiple concerns (UI, API, database, etc.):
- Single document with clear separation between layers
- Each layer gets its own subsection under Technical Approach

### File Handling

- Interview first, write file only at completion
- Ask user where to write the final spec if not specified
- Write directly without preview (user can request changes after)

## Non-Functional Requirements

Probe NFRs when relevant to the feature domain:
- Performance (for data-heavy or real-time features)
- Security (for auth, payments, user data)
- Accessibility (for UI features)

Don't force NFR questions when they don't apply.

## Additional Outputs

After writing the spec, offer to generate:
- Implementation task breakdown
- Suggested order of work

This is opt-in - ask user if they want it, don't auto-generate.

## Invocation Examples

```
# Point to existing file
/spec-writing @docs/specs/auth-feature.md

# Inline content
/spec-writing I want to add a dark mode toggle to the settings page

# Iterate on existing spec
/spec-writing @docs/specs/auth-feature.md (this already has content, refine the gaps)
```

## Codebase Exploration

Exploration depth is context-dependent:
- **Minimal spec:** Broader exploration to understand project patterns, conventions, related code
- **Detailed spec:** Targeted exploration of files directly related to the feature domain
- **Always read:** CLAUDE.md, README, directory structure for project context

## File Structure

```
plugins/dev-workflow/skills/spec-writing/
├── SKILL.md              # Main skill definition (<500 lines)
└── reference.md          # Optional: detailed examples, edge cases (loaded on demand)
```

**Constraints from Claude Code docs:**
- SKILL.md must stay under 500 lines for optimal context performance
- Supporting files can be linked for progressive disclosure
- No `scripts/` directory needed - this skill is purely instructional

## Success Criteria

A good spec-writing session:
- Surfaces requirements the user hadn't explicitly considered
- Results in a spec detailed enough to implement in a fresh session
- Gives user sense of control and collaboration (not just answering questions)
- Produces actionable technical detail, not just high-level descriptions
