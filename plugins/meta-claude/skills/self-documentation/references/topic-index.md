# Topic Index

Lightweight keyword-to-file mapping for efficient reference lookups. Load this file first to identify which reference file(s) to read.

## Keyword Mapping

| Keywords | Reference File | Description |
|----------|----------------|-------------|
| skill, skills, SKILL.md, allowed-tools, user-invocable, skill hooks, hot-reload, context fork, agent field, once hooks | core-features.md | Skills system |
| agent, subagent, Task tool, delegate, fork, context, agent hooks, SubagentStart | core-features.md | Agents and subagents |
| mcp, server, protocol, tool, mcp server, model context protocol, list_changed | core-features.md | MCP servers |
| plugin, marketplace, install plugin, plugin update | core-features.md | Plugins |
| slash command, /command, user-defined command, autocomplete, /plan, /teleport, /remote-env, /rename, /stats, /resume, /todos | core-features.md | Slash commands |
| hook, hooks, PreToolUse, PostToolUse, Stop, SubagentStart, SubagentStop, Notification, once, prompt-based hooks, updatedInput, ask confirmation | core-features.md | Hooks system |
| CLAUDE.md, memory, context, project instructions | configuration.md | Memory management |
| rules, .claude/rules, modular rules, path-specific rules | configuration.md | Modular rules |
| permission, permissions, allow, deny, tool access, wildcard patterns, unreachable warnings, Task(AgentName), disable agents | configuration.md | Permission management |
| sandbox, sandboxing, docker, isolation | configuration.md | Sandboxing |
| model, claude-sonnet, claude-opus, haiku, model selection | configuration.md | Model configuration |
| output, style, streaming, markdown | configuration.md | Output styles |
| status line, statusLine, prompt | configuration.md | Status line customization |
| language, japanese, spanish, french, i18n, response language | configuration.md | Language setting |
| respectGitignore, gitignore, file picker, @ file suggestions | configuration.md | respectGitignore setting |
| file read, token limit, CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS | configuration.md | File read token limit |
| attribution, commit, pr, co-authored-by | configuration.md | Attribution setting |
| thinking, extended thinking, Alt+T, MAX_THINKING_TOKENS, alwaysThinkingEnabled, opus 4.5 | configuration.md | Thinking mode |
| release channel, beta, stable, /config | configuration.md | Release channel toggle |
| --tools flag, interactive mode, tool restrictions | configuration.md | Tools interactive mode flag |
| vscode, vs code, ide, extension | integrations.md | VS Code extension |
| azure, foundry, enterprise | integrations.md | Azure AI Foundry |
| keyboard, shortcut, interactive, ctrl, alt, readline, Vim motions | workflows.md | Interactive mode |
| checkpoint, rewind, undo, restore | workflows.md | Checkpointing |
| cost, usage, tokens, spending | workflows.md | Cost tracking |
| git, branch, commit, pr, pull request | workflows.md | Git automation |
| parallel, concurrent, background, Ctrl+B, CLAUDE_CODE_DISABLE_BACKGROUND_TASKS | workflows.md | Parallel execution and background agents |
| session, named session, resume, /rename, /teleport, /remote-env | workflows.md | Named sessions and remote management |
| /stats, statistics, usage patterns, streaks | workflows.md | Stats command |
| /plan, plan mode, planning | workflows.md | Plan command |
| should I use, when to use, vs, versus, difference, compare, choose | decision-guide.md | Feature decisions |
| skill vs, agent vs, mcp vs, slash command vs | decision-guide.md | Feature comparisons |
| release notes, undocumented, new feature, recent | undocumented.md | Undocumented features |
| explore subagent, LSP, desktop, chrome extension, IS_DEMO | undocumented.md | Specific undocumented features |
| observation, discovered, tested, behavior, found that | observations.md | User observations |
| sdk, agent-sdk, behavioral, limitations | sdk-behavioral-bridges.md | SDK documentation that explains CLI behavior |
| timeout, 60 seconds, canUseTool | sdk-behavioral-bridges.md | Tool and callback timeouts |
| permission flow, evaluation order, deny first | sdk-behavioral-bridges.md | How permissions are evaluated |
| fork session, forkSession, session branch | sdk-behavioral-bridges.md | Session forking behavior |
| checkpoint scope, rewind scope, tracked changes | sdk-behavioral-bridges.md | File checkpointing limitations |
| mcp naming, tool naming, mcp__ | sdk-behavioral-bridges.md | MCP tool naming convention |
| subagent depth, nested subagent, Task in subagent | sdk-behavioral-bridges.md | Subagent spawning constraints |
| streaming mode, single message, image upload | sdk-behavioral-bridges.md | Input mode requirements |
| TypeScript-only, Python SDK limitations | sdk-behavioral-bridges.md | SDK platform differences |

## Cross-Theme Questions

Some questions span multiple themes. Load multiple files when keywords match different categories:

- "How do skills work with MCP servers?" → core-features.md (both topics)
- "Should I use a skill or subagent for this?" → decision-guide.md + core-features.md
- "What permissions does my MCP server need?" → core-features.md + configuration.md
- "How do I configure thinking mode?" → configuration.md + workflows.md
- "What keyboard shortcuts are available?" → workflows.md
- "How do skill hooks work?" → core-features.md (skills and hooks sections)

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
| `sdk-behavioral-bridges.md` | Behavioral constraints from SDK docs |
