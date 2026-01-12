# pm-workflow Plugin Spec

## Overview

A Claude Code plugin for product management workflows, initially containing a `prd-writing` skill for creating product one-pagers to kick off product development initiatives.

### Purpose

The `prd-writing` skill interviews users to transform rough product ideas into comprehensive one-pagers that:
- Support go/no-go decisions
- Align cross-functional teams (design, eng, marketing, support)
- Frame initiatives within company strategy
- Surface assumptions and open questions early

### Key Differentiation from spec-writing

| Aspect | spec-writing | prd-writing |
|--------|--------------|-------------|
| Focus | Technical implementation | Business justification |
| Audience | Engineers | Cross-functional stakeholders |
| Output | Implementation-ready spec | Decision-support document |
| Question depth | Edge cases, APIs, data models | Assumptions, success criteria, scope |
| Codebase use | Always explore | Optional (may run in separate workspace) |

## Plugin Structure

```
plugins/
  pm-workflow/
    .claude-plugin/plugin.json
    skills/
      prd-writing/
        SKILL.md
```

## prd-writing Skill

### Triggers

Activate when user says:
- "write a PRD"
- "one-pager"
- "product brief"
- "kick-off doc"
- "help me write a PRD for..."

### Tools

```yaml
allowed-tools:
  - AskUserQuestion
  - Read
  - Glob
  - Grep
  - Write
  - WebSearch
```

- `AskUserQuestion`: Core interview tool
- `Read/Glob/Grep`: Codebase exploration (when available)
- `Write`: Output the PRD
- `WebSearch`: Market/competitive research (on user request only)

### Interview Flow

**Problem-first approach:** Deep dive on problem and impact before any solution discussion.

1. **Understand the Input**
   - Accept via file reference (`@path/to/prd.md`) or inline description
   - If existing PRD has content, enter iteration mode

2. **Optional Codebase Exploration**
   - If in a codebase, check for related features and existing patterns
   - Skip if running in a separate PRD workspace

3. **Conduct the Interview**
   - Start with problem/impact (the "why")
   - Progress to hypothesis/solution (the "how")
   - Probe assumptions and success criteria
   - Explore scope boundaries
   - Check stakeholder impacts

4. **Write the PRD**
   - Ask where to write if not specified
   - Write directly without preview
   - Mark gaps from early exit explicitly

### Question Strategy

**Priority question types:**

1. **Assumption Challenging**
   - "What if users don't actually want this?"
   - "What makes you confident in [X assumption]?"
   - "What would need to be true for this to fail?"

2. **Scope Boundaries**
   - "Why is [Y] out of scope?"
   - "What would make you include [Z]?"
   - "Is this the smallest version that delivers value?"

3. **Success Definition**
   - "How would you know this failed?"
   - "What metric moves if this succeeds?"
   - "What does 'good' look like in 6 months?"

**Stakeholder probing:** Systematically ask about impacts on:
- Finance/accounting
- Customer support
- Legal/compliance
- Operations
- Other teams running experiments

### Handling Unknowns

**Supporting Data gaps:**
- Identify what data would strengthen the case
- Suggest specific research to conduct
- Mark as TBD with clear research questions

**Analytics gaps:**
- Focus on what to measure (high-level metrics)
- Don't go deep on implementation (event names, dashboards)
- Note measurement approach, not technical spec

**Stakeholder requirement gaps:**
- Capture as questions to ask specific teams
- Don't require resolution before writing

### Scope Management

When initiative is too big for a one-pager:
- Push user to pick the highest-impact slice
- Help identify the smallest valuable scope
- Ask: "What's the one thing that must ship first?"

Don't suggest splitting into multiple PRDs - help narrow to one focused initiative.

### Output Format

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

### Iteration Mode

When pointed at existing PRD with content:

1. Read and analyze existing sections
2. Identify thin areas or gaps
3. Interview specifically about gaps (don't re-ask resolved questions)
4. Update the PRD with new information

### Web Search

- **Not proactive:** Don't automatically search for market data
- **On request:** If user asks for competitive context or market size, offer to search
- **Cite sources:** When using web data, note where it came from

### Constraints

- **Must run in main conversation context** - `AskUserQuestion` requires interactive engagement
- **No `context: fork`** - interview is inherently interactive
- **No follow-up outputs** - PRD is the final deliverable (no research agendas or stakeholder checklists)

## Implementation Checklist

- [ ] Create `plugins/pm-workflow/.claude-plugin/plugin.json`
- [ ] Create `plugins/pm-workflow/skills/prd-writing/SKILL.md`
- [ ] Update `.claude-plugin/marketplace.json` to include new plugin
- [ ] Update `README.md` with pm-workflow documentation
- [ ] Test activation triggers
- [ ] Test iteration mode with existing PRD
