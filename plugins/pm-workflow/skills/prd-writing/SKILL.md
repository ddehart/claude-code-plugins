---
name: prd-writing
description: "Create comprehensive PRDs (Product Requirements Documents) and product one-pagers. Use when the user wants to write a PRD, product brief, one-pager, kick-off doc, or needs help defining product requirements. Triggers: write a prd, one-pager, product brief, kick-off doc, help me write a PRD for, define product requirements."
allowed-tools:
  - AskUserQuestion
  - Read
  - Glob
  - Grep
  - Write
  - WebSearch
---

# PRD-Writing Skill

Interview users to transform rough product ideas into comprehensive one-pagers for product development kick-offs.

## Overview

This skill conducts structured interviews using `AskUserQuestion` to surface requirements, assumptions, and success criteria. The goal is producing PRDs that support go/no-go decisions and align cross-functional teams.

**Key principle:** Problem-first approach - deep dive on problem and impact before any solution discussion.

**Activation:** This skill activates in two ways:
- **Automatic:** Claude invokes it proactively when the user asks to write a PRD, one-pager, or product brief
- **Explicit:** Users can invoke directly with `/prd-writing [prompt or @file]`

### Differentiation from spec-writing

| Aspect | spec-writing | prd-writing |
|--------|--------------|-------------|
| Focus | Technical implementation | Business justification |
| Audience | Engineers | Cross-functional stakeholders |
| Output | Implementation-ready spec | Decision-support document |
| Question depth | Edge cases, APIs, data models | Assumptions, success criteria, scope |
| Codebase use | Always explore | Optional |

## Workflow

### 1. Understand the Input

Accept PRD input via:
- **File reference:** User provides `@path/to/prd.md`
- **Inline content:** User describes the initiative in chat

If pointed at an existing PRD with content, enter **iteration mode** (see below).

### 2. Optional Codebase Exploration

If working within a codebase:
- Check for related features and existing patterns
- Review product docs, strategy documents if available

Skip exploration if running in a separate PRD workspace.

### 3. Conduct the Interview

Use `AskUserQuestion` to interview the user. Continue until comprehensive coverage.

**Flow:** Start with problem/impact (the "why") before progressing to hypothesis/solution (the "how").

**Pacing:** Adaptive
- Batch 2-4 related questions when efficient
- Switch to single questions when probing complex topics

**User can exit early** - if they say "that's enough" or "let's wrap up", proceed to writing with what you have.

### 4. Write the PRD

After the interview, write the PRD document:
- Ask where to write if not specified
- Write directly without preview
- Mark any gaps from early exit explicitly

## Question Strategy

### Priority Question Types

**1. Assumption Challenging**
- "What if users don't actually want this?"
- "What makes you confident in [X assumption]?"
- "What would need to be true for this to fail?"

**2. Scope Boundaries**
- "Why is [Y] out of scope?"
- "What would make you include [Z]?"
- "Is this the smallest version that delivers value?"

**3. Success Definition**
- "How would you know this failed?"
- "What metric moves if this succeeds?"
- "What does 'good' look like in 6 months?"

### Stakeholder Probing

Systematically ask about impacts on:
- Finance/accounting
- Customer support
- Legal/compliance
- Operations
- Other teams running experiments

## Handling Unknowns

### Supporting Data Gaps

When the user doesn't have data:
- Identify what data would strengthen the case
- Suggest specific research to conduct
- Mark as TBD with clear research questions

### Analytics Gaps

- Focus on what to measure (high-level metrics)
- Don't go deep on implementation (event names, dashboards)
- Note measurement approach, not technical spec

### Stakeholder Requirement Gaps

- Capture as questions to ask specific teams
- Don't require resolution before writing

## Scope Management

When initiative is too big for a one-pager:
- Push user to pick the highest-impact slice
- Help identify the smallest valuable scope
- Ask: "What's the one thing that must ship first?"

Don't suggest splitting into multiple PRDs - help narrow to one focused initiative.

## Output Format

**Template structure** (adapt based on interview content):

```markdown
# goal

[Relevant goal with associated customer value]

# problem

[What problem, who it affects, why it's important]

## supporting data

[Quantified impact, or TBD with research questions]

# hypothesis

[Proposed solution approach]

# assumptions

[What must be true for this to work]

# questions

[Outstanding unknowns]

# in scope

[What the solution includes]

# out of scope

[What the solution explicitly excludes]

# stakeholder requirements

- [Finance implications]
- [Support implications]
- [Cross-team impacts]

# analytics

- [What to measure]
- [How to know if hypothesis was wrong]
- [Key segments to analyze]

# functional requirements

- User experience and interaction design
  - [How the solution works]

# recommended reading

[Links to wireframes, research, related docs]
```

**Flexibility:** Adapt section depth based on interview content. Omit sections that aren't relevant. Add sections if interview surfaces new categories.

## Iteration Mode

When pointed at existing PRD with content:

1. **Read and analyze** existing sections
2. **Identify thin areas** or gaps
3. **Interview specifically about gaps** - don't re-ask resolved questions
4. **Update the PRD** with new information

## Web Search

- **Not proactive:** Don't automatically search for market data
- **On request:** If user asks for competitive context or market size, offer to search
- **Cite sources:** When using web data, note where it came from

## Error Handling

**No input provided:**
- Ask what initiative or product idea the user wants to define

**File not found:**
- Report the error, ask for correct path or inline description

**User is unresponsive:**
- After reasonable attempts, summarize what's known and offer to write partial PRD

**Scope keeps expanding:**
- Gently push back, help narrow to highest-impact slice

## Key Constraints

- **Must run in main conversation context** - `AskUserQuestion` is not available in forked/subagent contexts
- **No `context: fork`** - interview requires interactive user engagement
- **No follow-up outputs** - PRD is the final deliverable
