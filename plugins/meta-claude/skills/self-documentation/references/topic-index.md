# Topic Index

Lightweight keyword-to-file mapping for efficient reference lookups. Load this file first to identify which reference file(s) to read.

## Keyword Mapping

| Keywords | Reference File | Description |
|----------|----------------|-------------|
| skill, skills, SKILL.md, allowed-tools, user-invocable, skill hooks, hot-reload, context fork, agent field, once hooks, ${CLAUDE_SESSION_ID}, session id substitution, permission-free skills, skill character budget scaling, nested directory discovery, effort frontmatter support | core-features.md | Skills system |
| agent, subagent, Task tool, delegate, fork, context, agent hooks, SubagentStart, task metrics, token count, duration, tool uses, agent teams, teammate sessions, TeammateIdle, TaskCompleted, sub-agent spawning restrictions, background: true, worktree isolation, effort, maxTurns, disallowedTools frontmatter | core-features.md | Agents and subagents |
| mcp, server, protocol, tool, mcp server, model context protocol, list_changed, ENABLE_TOOL_SEARCH, tool search, auto MCP, claude.ai MCP connectors, elicitation, structured input, CIMD, Client ID Metadata | core-features.md, configuration.md | MCP servers and Auto MCP Tool Search |
| plugin, marketplace, install plugin, plugin update, search plugins, filter plugins, settings.json, default configuration | core-features.md | Plugins |
| slash command, /command, user-defined command, autocomplete, /plan, /teleport, /remote-env, /rename, /stats, /resume, /todos, /keybindings, /debug, /agents, claude agents command, /copy, /context, /effort, /color, /reload-plugins, /extra-usage | core-features.md, workflows.md | Slash commands |
| hook, hooks, PreToolUse, PostToolUse, Stop, SubagentStart, SubagentStop, Notification, once, prompt-based hooks, updatedInput, ask confirmation, additionalContext, TeammateIdle, TaskCompleted, ConfigChange, last_assistant_message, WorktreeCreate, WorktreeRemove, InstructionsLoaded, Elicitation, ElicitationResult, PostCompact, StopFailure | core-features.md | Hooks system |
| AskUserQuestion, Ctrl+G, external editor in AskUserQuestion | core-features.md | AskUserQuestion tool |
| $ARGUMENTS, $0, $1, $2, argument syntax, bracket syntax, indexed arguments | core-features.md | Command argument substitution |
| agents process user messages, background agents, foreground agents, subagent execution modes | core-features.md | Agents process user messages while working |
| CLAUDE.md, memory, context, project instructions, auto memory, automatic memory recording, autoMemoryDirectory | configuration.md, core-features.md | Memory management |
| rules, .claude/rules, modular rules, path-specific rules | configuration.md | Modular rules |
| permission, permissions, allow, deny, tool access, wildcard patterns, unreachable warnings, Task(AgentName), disable agents, Bash(*) | configuration.md | Permission management |
| sandbox, sandboxing, docker, isolation, allowRead | configuration.md | Sandboxing |
| model, claude-sonnet, claude-opus, haiku, model selection, Opus 4.6, fast mode, Sonnet 4.6, 1M context, extended context, modelOverrides, ANTHROPIC_CUSTOM_MODEL_OPTION, effort level, medium effort | configuration.md, core-features.md | Model configuration |
| output, style, streaming, markdown | configuration.md | Output styles |
| status line, statusLine, prompt, rate_limits | configuration.md | Status line customization |
| language, japanese, spanish, french, i18n, response language | configuration.md | Language setting |
| respectGitignore, gitignore, file picker, @ file suggestions | configuration.md | respectGitignore setting |
| file read, token limit, CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS | configuration.md | File read token limit |
| attribution, commit, pr, co-authored-by | configuration.md | Attribution setting |
| thinking, extended thinking, Alt+T, MAX_THINKING_TOKENS, alwaysThinkingEnabled, opus 4.5 | configuration.md | Thinking mode |
| release channel, beta, stable, /config | configuration.md | Release channel toggle |
| --tools flag, interactive mode, tool restrictions | configuration.md | Tools interactive mode flag |
| CLAUDE_CODE_ENABLE_TASKS, task system, disable tasks, TODO list | configuration.md | Task system toggle |
| --add-dir, add directory, additional directories, monorepo, enabledPlugins, extraKnownMarketplaces | configuration.md, workflows.md | Additional working directories |
| config backup, backup rotation, timestamped backup | configuration.md | Config backup rotation |
| reduced motion, accessibility, motion sensitivity, animation, prefersReducedMotion | configuration.md | Reduced motion mode |
| bash timeout, BASH_DEFAULT_TIMEOUT_MS, timeout duration display | configuration.md | Bash timeout duration display |
| spinner tips, spinnerTipsOverride, spinner customization | configuration.md | Spinner tips customization |
| CLAUDE_CODE_SIMPLE, simple mode, minimal configuration, disable MCP | configuration.md | Simple mode enhancements |
| CLAUDE_CODE_DISABLE_1M_CONTEXT, disable extended context, 1M context window | configuration.md | 1M context window toggle |
| vscode, vs code, ide, extension, plugin management, remote sessions | integrations.md | VS Code extension |
| chrome, browser, automation, --chrome, /chrome | integrations.md | Claude in Chrome |
| azure, foundry, enterprise | integrations.md | Azure AI Foundry |
| jetbrains, intellij, pycharm, webstorm | integrations.md | JetBrains IDEs |
| desktop, native app, download | integrations.md | Desktop application |
| python environment, usePythonEnvironment, virtual environment, venv | integrations.md | Python environment activation |
| install count, plugin listings, installation counts, VSCode plugins | integrations.md | Install count display in VSCode |
| keyboard, shortcut, interactive, ctrl, alt, readline, Vim motions, Ctrl+T, task list toggle, real-time thinking, transcript mode, verbose mode, Ctrl+F, kill background agents, chat:newline, multiline input | workflows.md | Interactive mode |
| keybindings, customize shortcuts, /keybindings, chord, keystroke, rebind, voice:pushToTalk | workflows.md | Customizable keyboard shortcuts |
| checkpoint, rewind, undo, restore | workflows.md | Checkpointing |
| cost, usage, tokens, spending | workflows.md | Cost tracking |
| git, branch, commit, pr, pull request | workflows.md | Git automation |
| parallel, concurrent, background, Ctrl+B, CLAUDE_CODE_DISABLE_BACKGROUND_TASKS | workflows.md | Parallel execution and background agents |
| session, named session, resume, /rename, /teleport, /remote-env, --from-pr, auto-generate session name, session name display, -n, --name, /remote-control | workflows.md | Named sessions and remote management |
| /stats, statistics, usage patterns, streaks | workflows.md | Stats command |
| /plan, plan mode, planning, /plan description | workflows.md | Plan command |
| task management, TaskCreate, TaskUpdate, TaskGet, TaskList, task dependencies, Ctrl+T, CLAUDE_CODE_TASK_LIST_ID | workflows.md | Task management system |
| history autocomplete, bash mode, tab completion, ! prefix | workflows.md | History-based autocomplete in bash mode |
| PR review status, prompt footer, review indicator, green, yellow, red, gray, purple, merged | workflows.md | PR review status indicator |
| full-width, zenkaku, Japanese IME | workflows.md | Japanese IME support |
| /debug, debug command, troubleshoot, session debugging, session debug log | workflows.md | Debug command |
| summarize from here, message selector, conversation summary | workflows.md | Summarize from here feature |
| --add-dir, add directory, enabledPlugins, marketplaces, monorepo | workflows.md | Additional working directories CLI flag |
| @-mention, file suggestions, autocomplete performance, session caching | workflows.md | File suggestions performance |
| --worktree, -w flag, isolated worktree, git worktree, switch to original | workflows.md | Worktree flag |
| remote control, /remote-control, server mode, headless, optional name, --console | workflows.md | Remote control and authentication |
| /context, context usage, optimization suggestions, memory bloat | workflows.md | Context visualization |
| /copy, code picker, write mode, w key, optional index, Nth-latest | workflows.md | Copy command and variations |
| /effort, effort level, low, medium, high, max, auto, Sonnet, Opus, Haiku | workflows.md | Effort level command |
| /color, prompt bar color, red, blue, green, yellow, purple, orange, pink, cyan | workflows.md | Color command |
| session name, /rename, prompt bar display | workflows.md | Session naming |
| --channels, MCP channels, research preview, async messages | workflows.md | Channel notifications |
| CLI authentication, --console, --email, --sso, Anthropic Console | workflows.md | Claude auth commands |
| skills, /simplify, /batch, /loop, /claude-api | workflows.md, core-features.md | Built-in skills |
| voice, STT, speech-to-text, 20 languages, dictation | core-features.md, workflows.md | Voice STT support |
| should I use, when to use, vs, versus, difference, compare, choose | decision-guide.md | Feature decisions |
| skill vs, agent vs, mcp vs, slash command vs | decision-guide.md | Feature comparisons |
| release notes, undocumented, new feature, recent | undocumented.md | Undocumented features |
| explore subagent, LSP, desktop, chrome extension, IS_DEMO | undocumented.md | Specific undocumented features |
| token count, metrics, tool uses, duration, Task tool results, task metrics | undocumented.md, core-features.md | Task tool metrics |
| TaskStop, task stopping, background task termination | undocumented.md | TaskStop improvement |
| extended thinking interruption, thinking interrupted, interruption handling | undocumented.md | Extended thinking interruption handling |
| heredoc, delimiter, command smuggling, bash security | undocumented.md | Heredoc security improvement |
| sandbox security, .claude/skills, blocked writes, skill injection | undocumented.md | Blocked writes in sandbox mode |
| anchor fragments, @-mentions, file resolution | undocumented.md | File resolution with anchor fragments |
| Windows ARM64, win32-arm64, native binary, ARM processor | undocumented.md | Windows ARM64 native binary support |
| startup performance, performance improvement, schema construction | undocumented.md | Startup performance improvements |
| prompt cache, cache hit rate, optimization, system prompt | undocumented.md | Prompt cache hit rate optimization |
| Opus 4.6 callout, notification, user eligible | undocumented.md | One-time Opus 4.6 callout |
| nested session, guard, launch, Claude Code inside | undocumented.md | Guard against nested sessions |
| SDKRateLimitInfo, SDKRateLimitEvent, rate limit types | undocumented.md | Rate limit SDK types |
| VS Code plan preview, auto-update, persistence | undocumented.md | VS Code plan preview updates |
| added_dirs, statusline, workspace section | undocumented.md | Statusline added_dirs field |
| supportsEffort, supportedEffortLevels, supportsAdaptiveThinking, effort, adaptive thinking | undocumented.md, sdk-behavioral-bridges.md | Model adaptive effort support |
| HTTP hooks, POST JSON, webhook | undocumented.md | HTTP hooks feature |
| local slash command, system messages, output | undocumented.md | Local command output display |
| ENABLE_CLAUDEAI_MCP_SERVERS, opt out, Claude.ai MCP | undocumented.md | Claude.ai MCP servers opt-out |
| worktree field, status line, metadata | undocumented.md | Worktree field in statusline |
| cron, scheduling, recurring tasks, /loop | undocumented.md, core-features.md | Cron scheduling and recurring execution |
| lsof, pgrep, tput, ss, fd, fdfind, allowlist | undocumented.md | Bash auto-approval additions |
| last-modified, timestamps, memory files | undocumented.md | Memory file timestamps |
| hook source, permission prompts, settings, plugin, skill | undocumented.md | Hook source display |
| ExitWorktree, worktree exit, isolation exit | undocumented.md | ExitWorktree tool |
| worktree.sparsePaths, sparse-checkout, monorepo | undocumented.md | Sparse checkout setting |
| turn duration, /config, toggle, display | undocumented.md | Turn duration toggle |
| source: 'settings', inline plugin, marketplace | undocumented.md | Settings-based plugins |
| CLI tool usage, plugin tips, detection | undocumented.md | Plugin tip detection |
| parallel tool results, resume, restoration | undocumented.md | Parallel tool restoration |
| line-by-line streaming, response text | undocumented.md | Response streaming |
| terminal notifications, tmux, outer terminal | undocumented.md | Tmux notifications |
| LSP startup, startupTimeout, configuration | core-features.md, undocumented.md | LSP startup timeout |
| ${CLAUDE_SKILL_DIR}, skill directory, bundled resources | core-features.md | Skill directory variable |
| ${CLAUDE_PLUGIN_DATA}, plugin persistent state, dependencies | core-features.md | Plugin data directory |
| observation, discovered, tested, behavior, found that | observations.md | User observations |
| sdk, agent-sdk, behavioral, limitations | sdk-behavioral-bridges.md | SDK documentation that explains CLI behavior |
| best practices, effective, failure pattern, verification, validate, verify, explore plan code, prompt crafting, session management, context management, kitchen sink, correction loop, intuition, when to clear | best-practices.md | Effective usage patterns |
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

- "How do skills work with MCP servers?" -> core-features.md (both topics)
- "Should I use a skill or subagent for this?" -> decision-guide.md + core-features.md
- "What permissions does my MCP server need?" -> core-features.md + configuration.md
- "How do I configure thinking mode?" -> configuration.md + workflows.md
- "What keyboard shortcuts are available?" -> workflows.md
- "How do I customize keyboard shortcuts?" -> workflows.md (Customizable Keyboard Shortcuts section)
- "How do skill hooks work?" -> core-features.md (skills and hooks sections)
- "How does Auto MCP Tool Search work?" -> configuration.md + core-features.md (MCP section)
- "How do I manage tasks?" -> workflows.md (task management system)
- "How do I write effective prompts?" -> best-practices.md
- "When should I use /clear?" -> best-practices.md + workflows.md
- "How do I use Claude in Chrome?" -> integrations.md
- "How do I resume remote sessions?" -> integrations.md (VS Code) + workflows.md
- "How do I add multiple directories?" -> configuration.md (--add-dir flag) + workflows.md (--add-dir CLI)
- "How do I resume a session by PR?" -> workflows.md (Named Sessions)
- "What are the latest Claude Code features?" -> undocumented.md
- "What task tools are available?" -> core-features.md (Task Tool section) + workflows.md (Task Management)
- "How do agent teams work?" -> core-features.md (Research Preview Agent Teams)
- "What are the new hooks?" -> core-features.md (Hooks section)
- "How does auto memory work?" -> core-features.md (Automatic Memory Recording) + configuration.md (Auto Memory)
- "What model options do I have?" -> configuration.md (Model Configuration) + core-features.md
- "How does worktree isolation work?" -> core-features.md (Agents and Subagents) + workflows.md (--worktree flag)
- "What new slash commands are available?" -> workflows.md (many /command sections)
- "How do I set up voice?" -> core-features.md (Voice STT Support) + workflows.md (Interactive Mode)
- "What effort levels are available?" -> workflows.md (/effort command) + configuration.md (Model Configuration)

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
| `best-practices.md` | Meta-guidance: when/why to use features, failure patterns |
