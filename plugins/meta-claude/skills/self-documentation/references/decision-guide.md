# Decision Guide

This guide helps you decide when to use Skills vs other Claude Code features. Based on the [Skills Explained blog post](https://www.claude.com/blog/skills-explained) and official documentation.

## Mental Model

**Skills are specialized training materials** that Claude dynamically discovers and loads when relevant. They teach Claude portable expertise without requiring re-explanation in each conversation.

Think of Skills as:
- Reference manuals Claude consults when needed
- Domain expertise that persists across conversations
- Self-contained packages of knowledge + tools

## When to Create a Skill

### The Core Heuristic

> **"If you find yourself typing the same prompt repeatedly across multiple conversations, it's time to create a Skill."**

### Good Skill Use Cases

**Organizational Procedures:**
- Brand guidelines and design systems
- Compliance requirements
- Document templates and formatting standards
- Code review checklists
- Release procedures

**Domain-Specific Expertise:**
- Excel formula reference and best practices
- PDF manipulation workflows
- Data analysis methodologies
- API integration patterns
- Testing strategies

**Personal Preferences:**
- Note-taking systems
- Coding conventions and patterns
- Commit message formats
- Documentation styles
- Project structure preferences

### When NOT to Use Skills

**One-off tasks:** If you'll only need the instruction once, use a regular prompt instead.

**Explicit user control needed:** Use slash commands for operations that require deliberate user invocation.

**Independent task execution:** Use subagents when you need context isolation and specific tool restrictions.

**Data access:** Use MCP servers to connect to external data sources (combine with Skills to teach what to do with the data).

## Skills vs Other Features

### Skills vs Slash Commands

| Aspect | Skills | Slash Commands |
|--------|--------|----------------|
| **Invocation** | Claude discovers automatically | User types `/command` |
| **Purpose** | Teach expertise, complex workflows | Quick, reusable prompts |
| **Structure** | Multi-file (SKILL.md + resources) | Single Markdown file |
| **Best for** | Team workflows, shared expertise | Explicit user-directed operations |
| **Example** | Automated code review standards | `/review` to trigger review |

**Decision question:** Does Claude need to recognize when to use this automatically?
- **Yes** → Skill
- **No** → Slash Command

### Skills vs Subagents

| Aspect | Skills | Subagents |
|--------|--------|-----------|
| **Purpose** | Teach portable expertise | Execute independent tasks |
| **Context** | Shares main conversation context | Separate context window |
| **Tools** | Can restrict via `allowed-tools` | Configurable tool access |
| **Best for** | Knowledge that applies everywhere | Specialized, isolated work |
| **Example** | Brand guidelines skill | code-reviewer subagent |

**Decision question:** Does this need its own isolated context and tool restrictions?
- **Yes** → Subagent
- **No** → Skill

### Skills vs MCP Servers

| Aspect | Skills | MCP Servers |
|--------|--------|-------------|
| **Purpose** | Teach what to do with data | Connect to data sources |
| **Function** | Instructions and workflows | Tools for data access |
| **Best for** | Domain expertise | External integrations |
| **Example** | "How to analyze Linear issues" | Linear MCP server (data access) |

**Recommended:** Use both together! MCP provides the data, Skills teach how to use it.

**Decision question:** Do you need to access external data or teach Claude what to do with it?
- **Access data** → MCP Server
- **Teach usage** → Skill
- **Both** → Use together

### Skills + Subagents (Integration Pattern)

| Aspect | Skills Alone | Skills + Subagents |
|--------|--------------|-------------------|
| **Purpose** | Teach expertise in main conversation | Provide expertise to specific subagent tasks |
| **Loading** | Auto-discovered by description | Auto-loaded when subagent activates |
| **Context** | Main conversation context | Subagent's separate context |
| **Best for** | General-purpose knowledge | Task-specific specialized expertise |
| **Example** | Code review standards (always available) | npm-update-advisor (only for package-updater) |

**Integration Pattern** (v2.0.43+):
Subagents can auto-load skills using the `skills` frontmatter field, combining knowledge (skill) with execution (subagent).

**When to use this pattern:**
- Knowledge useful in BOTH main conversation AND automation
- Subagent needs specialized domain expertise
- Want to avoid duplicating logic between main and subagent contexts
- Context efficiency matters (skill loads only when needed)

**Example: npm-update-advisor + package-updater**
```yaml
# Skill: Contains npm diagnostic logic
name: npm-update-advisor
description: Analyzes npm update strategies based on semver, lock files...

# Subagent: Orchestrates package updates, loads skill
name: package-updater
skills: npm-update-advisor
tools: Bash, Read
```

**Result:**
- User asks npm questions → Skill triggers in main conversation
- Security automation runs → Subagent loads skill for smart decisions
- Single source of truth, dual contexts

### Context: Fork Pattern

**What it is**: Skills can run in isolated execution contexts using `context: fork` frontmatter field, creating a hybrid between traditional skills and subagents.

| Aspect | Traditional Skills | `context: fork` Skills |
|--------|-------------------|------------------------|
| **Execution** | Runs in main conversation | Runs in isolated subagent context |
| **Context** | Shares conversation history | Fresh context window per invocation |
| **Tool access** | Restricted via `allowed-tools` | Restricted via `allowed-tools` |
| **Agent type** | N/A | Specify with `agent` field |
| **Best for** | Continuous guidance in main flow | Isolated, repeatable tasks |

**When to use `context: fork`:**
- Skill performs self-contained task that shouldn't pollute main context
- Need repeatability without accumulated conversation history
- Want skill behavior but with subagent-style isolation
- Task requires clean slate each invocation

**Agent field with fork:**
When using `context: fork`, specify which agent type to use:
```yaml
context: fork
agent: Explore  # Options: Explore, Plan, general-purpose, or custom agent name
```

**Comparison of execution contexts:**
- **Traditional skill**: Loads instructions into current conversation, sees all prior context, accumulates in conversation history
- **Skill with `context: fork`**: Creates temporary subagent for execution, no access to main conversation history, context discarded after completion
- **Traditional subagent (via Task tool)**: Persistent agent definition that can be invoked multiple times, maintains its own ongoing context window

**Example: diagnostic-check skill**
```yaml
name: diagnostic-check
description: Run system diagnostics when user reports issues
context: fork
agent: Explore
allowed-tools: ["Bash", "Read", "Grep"]
```

**Result:** Each diagnostic run starts fresh, previous diagnostic history doesn't interfere.

### Skills vs Prompts

| Aspect | Skills | Prompts |
|--------|--------|---------|
| **Persistence** | Across all conversations | Current conversation only |
| **Discovery** | Automatic when relevant | Manual entry each time |
| **Structure** | Organized files + resources | Plain text |
| **Best for** | Recurring needs | One-off instructions |

**Decision question:** Will you need this in future conversations?
- **Yes** → Skill
- **No** → Prompt

## Practical Examples

### Example 1: Repetitive Code Reviews

**Scenario:** You want Claude to always check for security issues, test coverage, and accessibility in PRs.

**Solution:** Create a `code-review-standards` skill
- **Why skill?** Applies to every code review across multiple conversations
- **Why not slash command?** You want Claude to recognize review context automatically
- **Why not subagent?** Doesn't need isolated context; guidance applies to main conversation

### Example 2: Linear Workflow Automation

**Scenario:** You want Claude to fetch Linear issues and analyze them for patterns.

**Solution:** MCP Linear server + `linear-analysis` skill
- **MCP for:** Fetching issue data (mcp__linear__list_issues)
- **Skill for:** Teaching analysis patterns, reporting format, insights to look for
- **Together:** MCP provides data, skill teaches what to do with it

### Example 3: Quick PR Template

**Scenario:** You want to generate PR descriptions in a specific format.

**Solution:** Create `/pr-template` slash command
- **Why slash command?** Explicit user action, not automatic discovery
- **Why not skill?** User deliberately triggers it when creating PRs
- **Why not subagent?** Doesn't need isolated context

### Example 4: Security Vulnerability Analysis

**Scenario:** You want dedicated analysis of security issues with limited tool access.

**Solution:** Create `security-analyzer` subagent
- **Why subagent?** Needs isolated context to focus only on security concerns
- **Tool restrictions:** Only Read, Grep, WebFetch for CVE lookup
- **Why not skill?** Needs separate context window and strict tool boundaries

## Quick Decision Tree

```
Need expertise across multiple conversations?
├─ No → Use regular prompt
└─ Yes → Continue...

    Does Claude need to discover this automatically?
    ├─ No → Use slash command
    └─ Yes → Continue...

        Need isolated context or tool restrictions?
        ├─ Yes → Use subagent (or skill with context: fork)
        └─ No → Continue...

            Need to access external data?
            ├─ Yes → Use MCP server (+ skill for usage patterns)
            └─ No → Use skill
```

## Summary Heuristics

**Create a Skill when:**
- You're repeating the same instruction across conversations
- You want Claude to automatically recognize when to apply knowledge
- You need to package expertise with reference files
- You want team members to automatically get standardized guidance

**Use Slash Command when:**
- You want explicit user control over invocation
- The operation is simple and doesn't need auto-discovery
- You prefer typing `/command` rather than having Claude guess

**Use Subagent when:**
- You need isolated context for focused work
- You want to restrict which tools are available
- You're delegating independent task execution
- You want to preserve main conversation context

**Use MCP Server when:**
- You need to access external data or services
- You want to integrate third-party tools
- Combine with Skills to teach Claude how to use the data

**Use `context: fork` when:**
- Need skill behavior with isolated execution
- Task should start fresh each time without conversation history
- Want repeatability without context accumulation
- Self-contained task that shouldn't impact main flow

---

**Last updated:** 2026-01-09

**Sources:**
- [Skills Explained Blog Post](https://www.claude.com/blog/skills-explained)
- [Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Sub-agents Documentation](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Slash Commands Documentation](https://docs.anthropic.com/en/docs/claude-code/slash-commands)
- [MCP Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp)
