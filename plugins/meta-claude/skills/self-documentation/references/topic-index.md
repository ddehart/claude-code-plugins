# Topic Index

Lightweight keyword-to-file mapping for efficient reference lookups. Load this file first to identify which reference file(s) to read.

## Keyword Mapping

| Keywords | Reference File | Description |
|----------|----------------|-------------|
| skill, skills, SKILL.md, allowed-tools, user-invocable, skill hooks | core-features.md | Skills system |
| agent, subagent, Task tool, delegate, fork, context | core-features.md | Agents and subagents |
| mcp, server, protocol, tool, mcp server, model context protocol | core-features.md | MCP servers |
| plugin, marketplace, install plugin, plugin update | core-features.md | Plugins |
| slash command, /command, user-defined command | core-features.md | Slash commands |
| hook, hooks, PreToolUse, PostToolUse, Stop, Notification | core-features.md | Hooks system |
| CLAUDE.md, memory, context, project instructions | configuration.md | Memory management |
| rules, .claude/rules, modular rules | configuration.md | Modular rules |
| permission, permissions, allow, deny, tool access | configuration.md | Permission management |
| sandbox, sandboxing, docker, isolation | configuration.md | Sandboxing |
| model, claude-sonnet, claude-opus, haiku, model selection | configuration.md | Model configuration |
| output, style, streaming, markdown | configuration.md | Output styles |
| status line, statusLine, prompt | configuration.md | Status line customization |
| vscode, vs code, ide, extension | integrations.md | VS Code extension |
| azure, foundry, enterprise | integrations.md | Azure AI Foundry |
| keyboard, shortcut, interactive, ctrl, alt, readline | workflows.md | Interactive mode |
| checkpoint, rewind, undo, restore | workflows.md | Checkpointing |
| cost, usage, tokens, spending | workflows.md | Cost tracking |
| git, branch, commit, pr, pull request | workflows.md | Git automation |
| parallel, concurrent, background | workflows.md | Parallel execution |
| session, named session, resume | workflows.md | Named sessions |
| should I use, when to use, vs, versus, difference, compare, choose | decision-guide.md | Feature decisions |
| skill vs, agent vs, mcp vs, slash command vs | decision-guide.md | Feature comparisons |
| release notes, undocumented, new feature, recent | undocumented.md | Undocumented features |
| explore subagent, LSP, desktop, chrome extension | undocumented.md | Specific undocumented features |
| observation, discovered, tested, behavior, found that | observations.md | User observations |

## Cross-Theme Questions

Some questions span multiple themes. Load multiple files when keywords match different categories:

- "How do skills work with MCP servers?" → core-features.md (both topics)
- "Should I use a skill or subagent for this?" → decision-guide.md + core-features.md
- "What permissions does my MCP server need?" → core-features.md + configuration.md

## File Purposes

| File | Primary Use |
|------|-------------|
| `core-features.md` | "How does X work?" for fundamental features |
| `configuration.md` | "How do I configure/customize X?" |
| `integrations.md` | IDE and platform-specific questions |
| `workflows.md` | Productivity and workflow optimization |
| `decision-guide.md` | "Should I use X or Y?" comparisons |
| `undocumented.md` | Features not yet in official docs |
| `observations.md` | User-discovered behaviors |
