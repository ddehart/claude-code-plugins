---
name: spec-writing
description: "Interview users to refine rough ideas into comprehensive, implementation-ready specifications. Use when the user wants to write a spec, refine requirements, flesh out a feature idea, or asks to be interviewed about a project. Triggers: help me spec, interview me, refine this spec, flesh out, requirements gathering, write a spec for, spec out, write a spec, create a spec, spec this out."
allowed-tools:
  - AskUserQuestion
  - Read
  - Glob
  - Grep
  - Write
---

# Spec-Writing Skill

Interview users to transform rough ideas into comprehensive, implementation-ready specifications through collaborative questioning.

## Overview

This skill conducts structured interviews using `AskUserQuestion` to surface requirements the user hasn't explicitly considered. The goal is producing specs detailed enough to implement in a fresh session.

**Key principle:** Ask non-obvious questions that probe assumptions, surface edge cases, and force tradeoffs.

**Activation:** This skill activates automatically when the user asks to write, create, or refine a spec. No slash command required - Claude should invoke this skill proactively when spec-writing is needed.

## Workflow

### 1. Understand the Input

Accept spec input via:
- **File reference:** User provides `@path/to/spec.md`
- **Inline content:** User describes the feature in chat

If pointed at an existing spec with content, enter **iteration mode** (see below).

### 2. Explore Codebase Context

Before interviewing, gather context to ask informed questions:

**Always read:**
- CLAUDE.md and README for project conventions
- Directory structure to understand architecture

**Exploration depth depends on spec detail:**
- **Minimal spec:** Broader exploration - patterns, conventions, related code
- **Detailed spec:** Targeted exploration of files directly related to the feature

Use Glob and Grep to find relevant code. Read files that will inform your questions.

### 3. Conduct the Interview

Use `AskUserQuestion` to interview the user. Continue until comprehensive coverage.

**Flow:** Start with goals ("why") before diving into implementation ("how").

**Pacing:** Adaptive
- Batch 2-4 related questions when efficient
- Switch to single questions when probing complex topics

**No hard limit** - continue interviewing until coverage is complete, even if 50+ questions.

**User can exit early** - if they say "that's enough" or "let's wrap up", proceed to writing with what you have.

### 4. Write the Spec

After the interview, write the spec document:
- Ask where to write if not specified
- Write directly without preview
- Mark any gaps from early exit explicitly

### 5. Offer Additional Outputs

After writing, ask if user wants:
- Implementation task breakdown
- Suggested order of work

This is opt-in - don't auto-generate.

## Question Strategy

### What Makes a Good Question

Good questions should:
- **Probe assumptions** the user takes for granted
- **Surface edge cases**, failure modes, and boundary conditions
- **Force tradeoffs** between competing concerns

Avoid obvious questions like "what color should it be?" - dig deeper.

### Question Categories

**Goals & Context:**
- What problem does this solve?
- Who are the users?
- What does success look like?
- What are explicit non-goals?

**Technical Approach:**
- How does this integrate with existing architecture?
- What dependencies or constraints exist?
- What's the data model?
- What APIs are involved?

**Edge Cases:**
- What happens when X fails?
- How should invalid input be handled?
- What are the boundary conditions?
- What about concurrent access?

**Tradeoffs:**
- Speed vs. correctness?
- Simplicity vs. flexibility?
- Build vs. buy?
- Consistency vs. availability?

**Non-Functional Requirements (when relevant):**
- Performance (for data-heavy features)
- Security (for auth, payments, user data)
- Accessibility (for UI features)

Don't force NFR questions when they don't apply.

### Technical Depth

Always push toward concrete implementation details, even when the initial spec is vague. Help the user think through the technical specifics.

## Handling Unknowns

When the user doesn't know the answer:

1. **Suggest common approaches** - present 2-4 options
2. **Provide a recommendation** with reasoning
3. **Let user choose** - pick, modify, or defer to TBD

Example using AskUserQuestion:
```
Question: "How should session state be persisted?"
Options:
- "Database (Recommended)" - Most durable, enables analytics
- "Redis" - Fast but requires infrastructure
- "Local storage" - Simplest but client-side only
```

## Completion Criteria

The skill decides when coverage is sufficient. Track internally:
- Core requirements defined?
- Technical approach clear?
- Edge cases identified?
- Risks acknowledged?

Don't expose a checklist to the user - just continue until thorough.

## Scope Management

If answers reveal the spec is actually multiple features:
1. Call out the scope expansion
2. Suggest splitting into separate specs
3. Let user decide whether to continue or narrow scope

## Iteration Mode

When pointed at an existing spec with content:

1. **Read and analyze** existing sections
2. **Identify thin areas** or gaps
3. **Interview specifically about gaps** - don't re-ask resolved questions
4. **Update the spec** with new information

## Output Format

### Structure

Structure emerges from interview content. Common sections:
- Overview / Problem Statement
- Goals & Non-Goals
- User Stories / Use Cases
- Technical Approach
- Edge Cases & Error Handling
- Risks & Open Questions

### Layered Sections

For specs spanning multiple concerns (UI, API, database):
- Single document with clear separation
- Each layer gets its own subsection under Technical Approach

### Risks & Open Questions

Always include a dedicated section for:
- Known risks and mitigation strategies
- Open questions that need resolution
- Assumptions that should be validated
- TBD items from the interview

## Examples

**New feature from scratch:**
```
User: Write a spec for real-time notifications
Skill: [explores codebase, then interviews about notification types,
       delivery mechanisms, user preferences, etc.]
```

**Refine existing spec:**
```
User: Help me flesh out @docs/specs/auth-feature.md
Skill: [reads spec, identifies gaps, interviews about those gaps]
```

**Inline prompt:**
```
User: I want to add a dark mode toggle - can you help me spec it out?
Skill: [interviews about scope, persistence, system integration, etc.]
```

## Error Handling

**No input provided:**
- Ask what feature or idea the user wants to spec out

**File not found:**
- Report the error, ask for correct path or inline description

**User is unresponsive:**
- After reasonable attempts, summarize what's known and offer to write partial spec

**Scope keeps expanding:**
- Gently push back, suggest splitting, let user decide

## Key Constraints

- **Must run in main conversation context** - `AskUserQuestion` is not available in forked/subagent contexts
- **No `context: fork`** - interview requires interactive user engagement
