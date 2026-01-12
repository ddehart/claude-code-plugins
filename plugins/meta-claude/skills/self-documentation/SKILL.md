---
name: self-documentation
description: Explain Claude Code features, capabilities, and tools. Use for questions like "how do skills work?", "what can you do?", "what's the difference between X and Y?", "should I use a skill or slash command?". Also handles recording observations about undocumented behaviors. Invoke with /self-documentation or ask naturally.
allowed-tools: ["Read", "Glob", "Grep", "WebFetch", "Bash", "Write"]
---

# Self-Documentation Skill

Enable Claude Code to explain its own features, guide capability decisions, and track undocumented observations discovered through usage.

## When to Activate

This skill activates for:
- **Direct questions**: "How do skills work?", "What can you do?", "What are your capabilities?"
- **Decision questions**: "Should I use a skill or slash command?", "Is this a good use case for X?"
- **Comparison questions**: "What's the difference between X and Y?", "When should I use X vs Y?"
- **Best practices**: "What's the right way to do X?", "How should I structure Y?"
- **Observation recording**: User reports discovering undocumented behavior

## Reference Files

The skill uses thematic reference files for token-efficient progressive disclosure:

| File | Content |
|------|---------|
| `topic-index.md` | Keyword-to-file mapping (load first) |
| `decision-guide.md` | Feature comparisons and decision trees |
| `core-features.md` | Skills, agents, MCP, plugins, hooks, slash commands |
| `configuration.md` | Settings, permissions, CLAUDE.md, sandboxing |
| `integrations.md` | VS Code, IDE extensions, plugin marketplace |
| `workflows.md` | Keyboard shortcuts, checkpointing, git automation |
| `undocumented.md` | Features from release notes without official docs |
| `observations.md` | User-discovered behaviors |
| `sdk-behavioral-bridges.md` | Behavioral constraints from Agent SDK docs |

## Workflow: Answering Questions

### Step 1: Load Topic Index

Read `references/topic-index.md` to identify which reference file(s) contain relevant information.

### Step 2: Identify Relevant Files

Match the user's question keywords to the topic index. For cross-theme questions (e.g., "How do skills work with MCP servers?"), identify multiple relevant files.

### Step 3: Load Reference Files

Read the identified reference file(s). Only load what's needed - avoid loading all files.

### Step 4: Fetch Official Docs (If Needed)

If the reference file includes a documentation URL and more detail is needed:
1. Use WebFetch to retrieve the official documentation
2. Synthesize with reference file content

**For behavioral constraints:** Check `sdk-behavioral-bridges.md` for authoritative information from the Agent SDK docs (e.g., tool limitations, permission flow, subagent constraints).

### Step 5: Respond

Provide a conversational response that:
- Directly answers the user's question
- Highlights key concepts
- Makes opinionated recommendations for decision questions (don't present all options as equal)
- Does NOT proactively suggest related topics

### Step 6: Update Reference (If New Info Learned)

If WebFetch revealed new information, update the reference file's "Key concepts" section with today's date.

## Workflow: Decision Questions

For questions about choosing between features ("Should I use X or Y?"):

1. Load `references/decision-guide.md`
2. Find the relevant comparison section
3. **Make a specific recommendation** based on the user's context
4. Explain **why** this choice is best
5. Provide actionable next steps

**Response pattern:**
> "For your use case, I recommend **[specific choice]**. Here's why:
>
> [Reasoning based on user's context]
>
> Next step: [Concrete action to take]"

## Workflow: Recording Observations

When a user discovers undocumented behavior (e.g., "I found that AskUserQuestion can't be delegated to subagents"):

### Step 1: Confirm Value

Verify this is a new observation worth recording:
- Is it about Claude Code behavior?
- Is it not already documented?
- Is it reproducible or specific enough to be useful?

### Step 2: Check for Duplicates

Before creating an issue, check if this observation already exists:

1. **Check local cache**: Read `~/.claude/plugin-observations/meta-claude.json` if it exists
2. **Check repo observations**: Read `references/observations.md` in this skill

**If a similar observation exists:**
- Inform the user: "This observation appears similar to an existing one: [description]"
- Ask if they want to:
  - Update the existing observation with new context
  - Create a new issue anyway (if sufficiently different)
  - Skip recording

**If no duplicate found:** Proceed to Step 3.

### Step 3: Propose Issue Creation

Ask the user:
> "This seems like a valuable observation. Would you like me to create a GitHub issue in the plugin repo to track it?"

Wait for user confirmation.

### Step 4: Create GitHub Issue

Use `gh` CLI to create an issue in `ddehart/claude-code-plugins`:

```bash
gh issue create --repo ddehart/claude-code-plugins \
  --title "[Observation] <brief description>" \
  --body "<formatted body>" \
  --label "observation"
```

**Issue format:**
```markdown
## Observation
<description of the behavior>

## Reproduction Context
- Discovered: <date>
- Context: <what the user was trying to do>
- Version: <Claude Code version if known>

## Related
- Feature area: <e.g., tools, subagents, skills>
```

### Step 5: Handle gh CLI Failure

If `gh` is unavailable or authentication fails:

1. Format the issue content
2. Display to user:
   > "I couldn't create the issue automatically. Here's the formatted content you can paste into a new issue at: https://github.com/ddehart/claude-code-plugins/issues/new"
3. Continue to Step 6

### Step 6: Offer Additional Actions

Ask the user:
> "Would you also like me to:
> - Cache this observation locally (at ~/.claude/plugin-observations/meta-claude.json)?
> - Create a PR to add it to the skill's observations.md?"

Based on user choice:
- **Cache locally**: Write to `~/.claude/plugin-observations/meta-claude.json`
- **Create PR**: Branch from main, update `observations.md`, create PR via `gh pr create`
- **Neither**: Done

### Local Cache Schema

```json
{
  "observations": [
    {
      "id": "obs-001",
      "description": "...",
      "context": "...",
      "discovered": "YYYY-MM-DD",
      "feature_area": "...",
      "issue_url": "https://github.com/...",
      "status": "submitted"
    }
  ],
  "last_updated": "YYYY-MM-DD"
}
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Reference file not found | Fall back to topic-index, report which file is missing |
| WebFetch fails | Use cached key concepts from reference file |
| gh CLI unavailable | Provide formatted issue for manual creation |
| Cross-theme question unclear | Load topic-index, ask user to clarify if needed |
| Observation already exists | Check local cache, inform user, offer to update |

## Plugin Repo

Issues and PRs go to: `ddehart/claude-code-plugins`

This skill is part of the `meta-claude` plugin in that marketplace.
