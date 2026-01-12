# PRD Evaluation Skill Spec

## Overview

A skill that evaluates PRDs from an experienced product leader's perspective, identifying gaps in reasoning, unstated assumptions, and disconnects between problem and solution. The skill operates as a critical reviewer, treating PRDs like thesis documents where every link in the chain of reasoning must be explicit and justified.

**Core problem:** PRDs often contain "internalized context" - assumptions and connections that exist in the author's mind but never made it to the page. This creates gaps that confuse stakeholders and weaken the case for the initiative.

## Goals

1. Surface missing links in the reasoning chain (problem → hypothesis → scope → metrics)
2. Identify hidden assumptions that should be stated explicitly
3. Catch scope items that don't connect to stated goals
4. Flag claims and statistics without traceable sources
5. Help users strengthen PRDs before stakeholder review

## Non-Goals

- Enforcing a specific PRD template or structure
- Evaluating technical feasibility (no codebase access)
- Providing market research or competitive analysis
- Rewriting sections (user does the fixing)
- Tracking changes across evaluation iterations

## User Experience

### Activation

Explicit invocation only. Triggers:
- "evaluate this PRD"
- "review my PRD"
- "critique my PRD"
- `/prd-evaluation @path/to/prd.md`

### Input

File reference only (`@path/to/prd.md`). The skill reads the PRD document directly.

### Output

Two outputs:

1. **Inline annotations** - Markdown callouts inserted into the PRD document at relevant locations:
   ```markdown
   > [!QUESTION] Why will users "naturally discover" this feature? What evidence supports this assumption?
   ```

2. **Conversation summary** - Overall assessment delivered in chat, including:
   - Verdict: "Ready for review" / "Needs work" / "Fundamental gaps"
   - Count of issues by category
   - Key areas requiring attention

### Interaction Flow

1. User invokes skill with file reference
2. Skill reads PRD and performs initial analysis
3. If fundamental flaws exist (weak problem statement, broken reasoning chain):
   - Stop and surface the core issue
   - Ask one clarifying question
   - Wait for user response before continuing
4. For gaps (missing information):
   - Stop and ask one clarifying question at a time
   - User provides answer
   - Skill continues evaluation
5. For weak reasoning (present but unconvincing):
   - Annotate inline without stopping
6. After full pass, provide conversation summary
7. Write annotated PRD back to file

Annotations are cleared on each run (fresh evaluation, not diff-aware).

## Evaluation Framework

### Reasoning Chain Analysis

The PRD should read like a thesis. Check each link:

| Link | Question | Red flags |
|------|----------|-----------|
| Problem → Hypothesis | Does the proposed solution actually address the stated problem? | Solution solves different problem; problem too vague to evaluate |
| Hypothesis → Scope | Does every in-scope item map to the proposed approach? | Scope items that don't serve the hypothesis; missing items needed for hypothesis |
| Goals → Analytics | Can the stated metrics prove/disprove the hypothesis? | Vanity metrics; metrics that don't map to stated goals; unmeasurable outcomes |

### Issue Categories

**Logical Coherence**
- Missing steps in reasoning
- Conclusions that don't follow from premises
- Circular justifications ("we should do X because we need X")

**Assumption Surfacing**
- Unstated beliefs treated as facts
- User behavior assumptions without validation
- Technical or organizational dependencies not mentioned

**Scope Creep Detection**
- In-scope items with no clear connection to goals
- "Nice to have" items mixed with core requirements
- Scope larger than needed to test hypothesis

**Data/Claim Validation**
- Statistics without sources
- Vague quantifiers ("most users", "significant improvement")
- Claims presented as facts without evidence

### Severity Levels

| Severity | Behavior | Examples |
|----------|----------|----------|
| **Blocker** | Stop, address before continuing | Problem statement missing or incoherent; reasoning chain fundamentally broken |
| **Gap** | Stop, ask clarifying question | Key assumption unstated; metric unmeasurable; scope item unexplained |
| **Weak** | Annotate inline, continue | Claim without source; reasoning unconvincing but present; minor scope creep |

### TBD Handling

Sections explicitly marked as TBD or "to be researched" are acknowledged but not critiqued. The evaluation focuses on content that is presented as complete.

## Annotation Format

Use Markdown callouts for visibility:

```markdown
> [!QUESTION] [Category] Specific question or issue

> [!WARNING] [Category] Issue description
```

Categories in brackets: `[Coherence]`, `[Assumption]`, `[Scope]`, `[Data]`

Examples:

```markdown
## hypothesis

We will implement progressive disclosure to reduce cognitive load.

> [!QUESTION] [Coherence] The problem statement mentions "user confusion during onboarding" but this hypothesis addresses "cognitive load" generally. How does progressive disclosure specifically address the onboarding confusion?

## in scope

- User onboarding flow redesign
- New tutorial system
- Analytics dashboard for tracking engagement

> [!WARNING] [Scope] "Analytics dashboard" appears disconnected from the hypothesis about progressive disclosure. Is this essential to testing the hypothesis, or scope creep?
```

## Persona

Generic experienced product leader. Characteristics:
- Critical but constructive
- Questions assumptions without being dismissive
- Focuses on strengthening the case, not tearing it down
- Direct communication style
- Expects justification, not just assertion

## Completion Criteria

A PRD can be marked "Ready for review" when:
- Reasoning chain is complete and explicit
- Key assumptions are stated
- All in-scope items connect to goals
- Claims have sources or are marked as hypotheses
- No blocker or gap-level issues remain

If issues remain after clarifications, verdict is "Needs work" with specific areas listed.

## Technical Implementation

### Skill Definition

```yaml
---
name: prd-evaluation
description: "Evaluate PRDs from a product leader's perspective. Use when the user wants to critique, review, or strengthen a PRD before stakeholder review. Triggers: evaluate this PRD, review my PRD, critique my PRD."
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
---
```

### Required Tools

- **Read**: Load PRD document
- **AskUserQuestion**: Interactive clarification for gaps
- **Write**: Save annotated PRD

No codebase exploration tools (Glob, Grep) - evaluation is document-only.

## Error Handling

| Scenario | Response |
|----------|----------|
| File not found | Report error, ask for correct path |
| Empty file | Ask user to provide PRD content |
| No clear PRD content | Ask what document type this is |
| User wants to stop early | Provide partial summary of findings so far |

## Future Considerations (Out of Scope for v1)

- Multiple persona options (skeptical exec, technical PM, user advocate)
- Diff-aware iteration tracking
- Integration with prd-writing skill (auto-suggest after creation)
- Severity customization
- Team-specific evaluation criteria
