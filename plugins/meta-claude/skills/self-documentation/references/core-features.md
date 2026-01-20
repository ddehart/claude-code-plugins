# Core Features

Foundational Claude Code capabilities that enable extensibility and customization.

**Last updated**: 2026-01-19

---

## Claude Code Overview

**What it is**: High-level overview of Claude Code's core capabilities, characteristics, and setup requirements

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/overview

**Key concepts**:
- **Core capabilities**: Build features (natural language → code), debug & fix issues, codebase navigation, automation (lint fixes, merge conflicts, release notes)
- **Terminal-native**: Integrates into existing developer workflows, not a separate IDE
- **Direct action**: Can edit files, execute commands, create commits directly
- **MCP integration**: Access external resources (Google Drive, Figma, Slack) through Model Context Protocol
- **Unix philosophy**: Composable, scriptable, pipeable for CI/CD integration
- **Enterprise ready**: Available via Claude API, AWS Bedrock, Google Vertex AI with security/privacy/compliance
- **VS Code extension (Beta)**: Graphical IDE alternative without terminal requirements
- **Setup**: Requires Node.js 18+, install via `npm install -g @anthropic-ai/claude-code`

---

## Skills System

**What it is**: Modular capabilities that extend Claude's functionality with specialized knowledge and workflows. Skills consist of a SKILL.md file with YAML frontmatter (name, description) plus optional supporting files (scripts, references, assets).

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/skills

**Key concepts**:
- **Model-invoked** (not user-invoked) - Claude autonomously decides when to use based on context and description field
- **Auto-discovery** - Skills activate automatically when relevant to request, unlike slash commands which require explicit invocation
- **Progressive disclosure** - Three-level loading: metadata (always in context ~100 words), SKILL.md body (when triggered <5k words), bundled resources (as needed)
- **Multi-file structure** - SKILL.md + optional supporting files (references/, scripts/, templates/); manages context efficiently by deferring non-essential information
- **Three scopes**: Personal (`~/.claude/skills/`), Project (`.claude/skills/`, git-shared), Plugin (bundled with Claude Code plugins)
- **Nested directory discovery** - Skills auto-discovered from nested `.claude/skills/` directories; supports monorepo setups where packages have their own Skills
- **Tool restrictions** - `allowed-tools` frontmatter field limits available tools within skill for security/safety; supports comma-separated or YAML-style lists
- **Description field is critical** - Must be specific with trigger terms for discoverability (max 1024 characters); tells Claude when to activate
- **Supporting files**: `scripts/` (executable code, may run without loading to context), `references/` (docs loaded into context as needed), `assets/` (files used in output, not loaded to context)
- **Best practices**: One capability per skill, write specific descriptions with user trigger terms, test activation timing with team, document versions
- **Sharing**: Via plugins (recommended, marketplace distribution) or project repository (`.claude/skills/`, team auto-gets on pull)
- **vs Slash Commands**: Skills are "complex workflows Claude discovers automatically" with multi-file support; slash commands are "simple, reusable prompts" requiring explicit invocation
- **Subagent integration**: Subagents can auto-load specific skills via `skills` frontmatter field; enables specialized knowledge per subagent; skills unload when subagent completes
- **Hot-reload**: Skills are automatically reloaded when created or modified, no restart required
- **Forked execution**: `context: fork` runs skill in isolated sub-agent context with its own conversation history
- **Agent field**: Specify which agent type to use when `context: fork` is set (e.g., `Explore`, `Plan`, `general-purpose`, or custom agent)
- **Skill hooks**: Skills can define hooks scoped to their lifecycle using `hooks` frontmatter field; supports `PreToolUse`, `PostToolUse`, and `Stop` events
- **Once hooks**: Hooks with `once: true` run only once per session, then are removed
- **Visibility control**: `user-invocable` field controls whether skill appears in slash command menu (defaults to `true`); does not affect `Skill` tool or automatic discovery
- **Skills/slash commands merged**: Skills visible in slash command menu by default for unified invocation model

---

## MCP (Model Context Protocol) Servers

**What it is**: Open-source standard for AI-tool integrations enabling Claude Code to access external tools, databases, and APIs (hundreds of third-party services)

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/mcp

**Key concepts**:
- **Core capabilities**: Retrieve features from issue trackers, analyze monitoring data, query databases, access design files, automate workflows
- **Three transport types**: HTTP (recommended for cloud services), SSE (deprecated but functional), Stdio (local processes for custom scripts)
- **Three scopes**: Local (default, personal project configs), Project (team-shared via `.mcp.json` in version control), User (cross-project personal utilities)
- **Scope precedence**: Local overrides project and user when naming conflicts occur
- **Popular integrations**: Sentry, Hugging Face, Jam, Asana, Jira, Linear, Notion, Airtable, HubSpot, PostgreSQL, Stripe, Square, PayPal
- **Management commands**: `claude mcp list/get/remove`, `/mcp` within Claude Code
- **Authentication**: OAuth 2.0 automatic for HTTP servers, tokens stored securely and auto-refreshed
- **Enterprise**: System-wide `managed-mcp.json` for standardization, allowlists/denylists for control
- **Tool naming**: MCP tools use pattern `mcp__<server-name>__<tool-name>`
- **Dynamic updates**: MCP `list_changed` notifications allow servers to dynamically update available tools, prompts, and resources without reconnecting
- **structuredContent support**: MCP servers can return `structuredContent` field in tool responses for richer outputs beyond plain text (formatting, hierarchy, structured data)
- **headersHelper**: Dynamic header generation via helper script in MCP config; script outputs JSON with header key-value pairs; enables OAuth token refresh and short-lived API keys

---

## Plugins

**What it is**: Extensions that add custom functionality (commands, agents, skills, hooks, MCP servers) that can be shared across projects and teams

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/plugins

**Key concepts**:
- **Components**: Commands (slash commands), Agents (specialized AI assistants), Skills (model-invoked capabilities), Hooks (event handlers), MCP Servers (external integrations)
- **Structure**: `.claude-plugin/plugin.json` (metadata), `commands/`, `agents/`, `skills/`, `hooks/` directories
- **Installation**: `/plugin` interactive menu (browse/discover), direct commands (`install/enable/disable`)
- **Marketplaces**: Catalogs of plugins, add via `/plugin marketplace add your-org/claude-plugins`
- **Team configuration**: Automatic installation via `.claude/settings.json` in repository
- **Development**: Create plugin.json, add components, test locally, distribute through catalogs
- **Best practices**: Semantic versioning, comprehensive README, local testing, organize by functionality
- **User roles**: Plugin users (discover/install), Developers (create/distribute), Team leaders (governance/catalogs)

---

## Agents and Subagents

**What it is**: Specialized AI assistants that Claude Code can delegate tasks to. Each operates with its own separate context window and can be configured with specific system prompts, tools, and models for task-specific problem-solving.

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/sub-agents

**Key concepts**:
- **Benefits**: Context preservation (separate windows prevent main conversation pollution), specialized expertise (fine-tuned instructions), reusability (work across projects), flexible permissions (different tool access levels)
- **Creation**: `/agents` → Create New Agent → Choose scope → Define/customize → Select tools → Save; or manually create Markdown files with YAML frontmatter
- **File structure**: YAML frontmatter with `name` (required, lowercase-hyphenated), `description` (required, natural language purpose), `tools` (optional, comma-separated), `model` (optional, sonnet/opus/haiku/inherit), `disallowedTools` (optional, explicit tool blocking), `permissionMode` (optional, permission behavior for specific agent)
- **File locations** (priority order): Project (`.claude/agents/`, highest), CLI flag (`--agents`, add subagents dynamically), User (`~/.claude/agents/`, lower), Plugin (`agents/` directory)
- **Usage**: Automatic delegation (Claude proactively identifies based on descriptions; use "PROACTIVELY" or "MUST BE USED" in description), Explicit invocation (direct requests to use specific subagent), @-mention support with typeahead
- **Tool access**: Inherits all tools if not specified; can restrict to specific tools via `tools` field; can explicitly block tools via `disallowedTools` field; includes MCP server tools
- **Skill auto-loading**: `skills` frontmatter field loads specific skills when subagent activates; enables specialized knowledge per subagent; skills unload when subagent completes
- **Built-in subagents**: Explore (Haiku-powered read-only codebase exploration with thoroughness levels: quick/medium/very thorough), Plan (automatic codebase research during plan mode using Read/Glob/Grep/Bash tools with Sonnet model, prevents infinite nesting), General-purpose (complex multi-step tasks with all tools), Helper agents (Bash, statusline-setup, Claude Code Guide)
- **Best practices**: Start with Claude-generated then customize, design focused subagents with single responsibilities, write detailed prompts with constraints, limit tool access to necessary only, version control project subagents
- **Advanced**: Chaining (multiple sequential subagents), dynamic selection (Claude intelligently chooses), model selection ('inherit' for consistency), subagent resumption (Claude can resume previous subagents), dynamic model choice (Claude selects model for subagent tasks)
- **Agent hooks**: Agents can define hooks in frontmatter using `hooks` field; supports `PreToolUse`, `PostToolUse`, and `Stop` events
- **Disable via Task tool**: Use `Task(AgentName)` syntax in permission deny rules to prevent specific agents from being invoked
- **Permission modes**: `permissionMode` field controls permission behavior per agent (`default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`)
- **Background execution**: Agents can run in foreground (blocking with permission passthrough) or background (concurrent with auto-deny for missing permissions); MCP tools not available in background

---

## Slash Commands

**What it is**: Tools that control Claude's behavior via frequently-used prompts, invoked by user explicitly or by Claude programmatically. Can be built-in or custom Markdown files.

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/slash-commands

**Key concepts**:
- **Invocation patterns**: Direct (`/command`), plugin-prefixed (`/plugin:command` for disambiguation), with arguments (`/command arg1 arg2`)
- **Built-in commands**: `/help` (usage), `/clear` (history), `/model` (selection), `/cost` (tokens), `/memory` (CLAUDE.md editing), `/sandbox` (sandboxed bash), `/mcp` (server management), `/todos` (view current todo list), `/plan` (enter plan mode), `/teleport` (resume remote session), `/remote-env` (configure remote environment), `/rename` (name session), `/stats` (usage statistics), `/resume` (resume by name or ID), `/config` (settings with search)
- **Custom commands**: Single Markdown files in `.claude/commands/` (project, git-shared) or `~/.claude/commands/` (personal, cross-project)
- **Structure**: Single file with frontmatter, simpler than Skills' multi-file structure
- **Features**: Namespacing via subdirectories, arguments (`$ARGUMENTS` for all, `$1`/`$2` for specific), bash execution (prefix `!`), file references (`@` notation), frontmatter metadata
- **Frontmatter options**: Description, allowed-tools (comma-separated or YAML-style), model selection, disable-model-invocation, hooks, argument-hint, context (fork), agent (for forked context)
- **Execution**: Skill tool allows Claude to invoke programmatically; disable via `/permissions` or `disable-model-invocation: true`
- **MCP commands**: Format `mcp__<server-name>__<prompt-name>` from MCP server prompts
- **Plugin commands**: Auto-discovered when plugins installed
- **vs Skills**: Commands are "simple, reusable prompts" requiring explicit invocation; Skills are "complex workflows Claude discovers automatically" with multi-file support
- **Autocomplete anywhere**: Slash command autocomplete works at any position in input, not just at the beginning
- **Command hooks**: Slash commands can define hooks in frontmatter; supports `PreToolUse`, `PostToolUse`, and `Stop` events with `once: true` option
- **Skills/commands merged**: Skills and slash commands now use unified `Skill` tool (previously separate `SlashCommand` tool)

---

## Hooks

**What it is**: Automated bash scripts that execute in response to specific events during Claude Code sessions, enabling custom automation, validation, and integration workflows

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/hooks

**Key concepts**:
- **Execution model**: All matching hooks run in parallel with 60-second default timeout; receive JSON via stdin, return structured output to control Claude
- **Configuration locations**: `~/.claude/settings.json` (user), `.claude/settings.json` (project), `.claude/settings.local.json` (local project), enterprise managed policy, skill/agent/command frontmatter
- **11 event types**: PreToolUse (before tool execution, can modify tool inputs), PostToolUse (after completion), UserPromptSubmit (prompt submission), Notification (permission requests with matcher values for event filtering), PermissionRequest (automatically approve/deny tool permissions), Stop (main agent finish, prompt-based matching), SubagentStart (subagent begins), SubagentStop (subagent finish), SessionStart (session begins), SessionEnd (session terminates), PreCompact (before context compacting), Setup (triggered via CLI flags)
- **Setup hook**: Triggered via `--init`, `--init-only`, or `--maintenance` CLI flags; runs setup scripts for repository initialization, dependency installation, or maintenance tasks before the interactive session starts
- **Matcher patterns**: Exact (`Write`), regex (`Edit|Write`), wildcard (`*`), prompt-based (Stop hooks can match against user prompts), Notification and PermissionRequest matcher values for event-specific filtering; case-sensitive
- **Exit codes**: 0 (success, stdout to transcript), 2 (blocking error, stderr to Claude), other (non-blocking error, stderr to user)
- **JSON output**: Advanced control with `continue`, `decision`, `reason`, and hook-specific parameters
- **PreToolUse advanced features**:
  - **updatedInput parameter**: Allows modifying tool input parameters before execution; returned in JSON output to override original tool inputs
  - **ask parameter**: Triggers user confirmation dialog during hook execution; use in JSON output to prompt for approval before tool proceeds
  - **additionalContext parameter**: Adds context string to Claude before tool executes
- **Hook input fields**: `tool_use_id` field in PreToolUse and PostToolUse hooks enables correlation between pre/post events for same tool call
- **PermissionRequest hook**: Runs when user shown permission dialog; use decision control to allow/deny automatically; recognizes same matcher values as PreToolUse
- **Environment variables**: `CLAUDE_PROJECT_DIR` (project root path), `CLAUDE_ENV_FILE` (SessionStart persistence), `CLAUDE_CODE_REMOTE` (remote/local indicator)
- **Security warning**: Execute arbitrary shell commands automatically—validate/sanitize input, quote variables, use absolute paths, avoid sensitive files, test in safe environments
- **MCP integration**: Works with MCP tools using pattern `mcp__<server>__<tool>`
- **Debugging**: Use `claude --debug` for execution details, matched commands, exit codes, output
- **Component hooks**: Skills, agents, and slash commands can define hooks in frontmatter; scoped to component lifecycle
- **Once hooks**: `once: true` option runs hook only once per session for skills and commands
- **Prompt-based hooks**: `type: "prompt"` uses LLM to evaluate context; supported for Stop, SubagentStop, and other events

---

## Task Tool

**What it is**: Core tool allowing Claude to delegate work to specialized subagents with isolated contexts

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/sub-agents

**Key concepts**:
- **Purpose**: Invoke subagents for specialized tasks while preserving main conversation context
- **Context isolation**: Each subagent operates with separate context window, preventing pollution of main conversation
- **Automatic selection**: Claude proactively identifies appropriate subagent based on task and descriptions
- **Explicit invocation**: Users can request specific subagent directly
- **Tool inheritance**: Subagents inherit or restrict tool access based on configuration
- **Result integration**: Subagent work summarized and returned to main conversation
- **Chaining support**: Multiple subagents can work sequentially on complex tasks
- **Permission control**: Can be disabled via `/permissions` or blocked with `Task(AgentName)` syntax for specific agents

---

## AskUserQuestion Tool

**What it is**: Interactive tool for asking structured multiple-choice questions during conversations

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings (Tools Available to Claude table)

**Key concepts**:
- **Purpose**: Enables Claude to ask structured questions with multiple-choice options
- **Features**: Single-select or multi-select modes, automatic "Other" option for custom input
- **Use cases**: Gathering preferences, clarifying ambiguous requirements, plan mode decisions
- **Question structure**: Header (short label), question text, 2-4 options with label and description
- **Behavioral constraints**: 60-second timeout, 1-4 questions per call, not available in subagents spawned via Task tool
- **Permission**: No permission required for this tool

---

## LSP Tool

**What it is**: Language Server Protocol integration for semantic code intelligence

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings (Tools Available to Claude table)

**Key concepts**:
- **Introduced**: v2.0.74 (2025-12)
- **Purpose**: Semantic code understanding beyond grep - go-to-definition, find references, hover documentation/types
- **Benefits**: More accurate than grep, understands code structure and types
- **Capabilities**: Navigate code definitions, find all references to symbols, get type information and documentation
- **Use cases**: Codebase exploration, refactoring support, understanding code relationships
- **Likely supported languages**: TypeScript/JavaScript, Python, other LSP-compatible languages
