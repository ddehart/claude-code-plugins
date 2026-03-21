# Core Features

Foundational Claude Code capabilities that enable extensibility and customization.

**Last updated**: 2026-03-21

---

## Claude Code Overview

**What it is**: High-level overview of Claude Code's core capabilities, characteristics, and setup requirements

**Documentation**: https://code.claude.com/docs/en/overview

**Key concepts**:
- **Core capabilities**: Build features (natural language to code), debug and fix issues, codebase navigation, automation (lint fixes, merge conflicts, release notes)
- **Terminal-native**: Integrates into existing developer workflows, not a separate IDE
- **Direct action**: Can edit files, execute commands, create commits directly
- **MCP integration**: Access external resources (Google Drive, Figma, Slack) through Model Context Protocol
- **Unix philosophy**: Composable, scriptable, pipeable for CI/CD integration
- **Enterprise ready**: Available via Claude API, AWS Bedrock, Google Vertex AI with security/privacy/compliance
- **VS Code extension (Beta)**: Graphical IDE alternative without terminal requirements
- **Setup**: Requires Node.js 18+, install via `npm install -g @anthropic-ai/claude-code`

---

## Skills (Unified with Slash Commands)

**What it is**: The extensibility system for Claude Code. Skills are SKILL.md files with YAML frontmatter that extend Claude's capabilities. Custom slash commands have been merged into skills - both `.claude/commands/review.md` and `.claude/skills/review/SKILL.md` create `/review` and work the same way.

**Documentation**: https://code.claude.com/docs/en/skills

**Key concepts**:
- **Dual invocation model**: Skills can be invoked by users (`/skill-name`) OR by Claude automatically when relevant. Both modes enabled by default.
- **User invocation**: Type `/skill-name` to invoke directly; skills appear in slash command autocomplete menu
- **Model invocation**: Claude loads skills automatically when conversation matches the description field
- **Invocation control**: `disable-model-invocation: true` prevents Claude from auto-loading (user-only); `user-invocable: false` hides from menu (Claude-only)
- **Backwards compatibility**: Files in `.claude/commands/` still work with same frontmatter support; if skill and command share a name, skill takes precedence
- **Multi-file structure**: SKILL.md (required) + optional supporting files (references/, scripts/, templates/); manages context efficiently
- **Three scopes**: Personal (`~/.claude/skills/`), Project (`.claude/skills/`, git-shared), Plugin (bundled with Claude Code plugins)
- **Enterprise scope**: Organization-wide skills via managed settings
- **Nested directory discovery**: Skills auto-discovered from nested `.claude/skills/` directories; supports monorepo setups
- **Tool restrictions**: `allowed-tools` frontmatter field limits available tools within skill for security/safety
- **Description field is critical**: Must be specific with trigger terms for discoverability (max 1024 characters); tells Claude when to auto-load
- **Supporting files**: `scripts/` (executable code), `references/` (docs loaded as needed), `assets/` (files used in output)
- **Argument passing**: `$ARGUMENTS` for all args, `$0`/`$1`/`$2` shorthand, `${CLAUDE_SESSION_ID}` for session ID; if `$ARGUMENTS` not in content, args appended automatically
- **Dynamic context**: `!`command`` syntax runs shell commands before skill content is sent to Claude; output replaces placeholder
- **Sharing**: Via plugins (recommended, marketplace distribution) or project repository (`.claude/skills/`, team auto-gets on pull)
- **Subagent pairing**: Skills naturally pair with subagents for context protection. Two patterns:
  - `agent: <agent-name>` spawns subagent with skill loaded into fresh context (ideal for search/research skills using Explore agent)
  - `context: fork` spawns subagent with current conversation context carried over (ideal for parallel operations like memory/summarization that shouldn't pollute main context)
- **Subagent skill loading**: Subagents can auto-load specific skills via `skills` frontmatter field; enables specialized knowledge per subagent; skills unload when subagent completes
- **Hot-reload**: Skills automatically reloaded when created or modified, no restart required
- **Skill hooks**: Skills can define hooks scoped to their lifecycle using `hooks` frontmatter field; supports `PreToolUse`, `PostToolUse`, and `Stop` events
- **Once hooks**: Hooks with `once: true` run only once per session, then are removed
- **Permission-free skills**: Skills without additional permissions or hooks load without requiring user approval; reduces friction for simple skills
- **Unified Skill tool**: Claude invokes skills programmatically via `Skill` tool; control access via `/permissions` rules like `Skill(name)` or `Skill(name:*)`
- **Skills auto-load from additional directories**: Skills now auto-load from additional directories beyond the standard skill locations
- **Effort frontmatter support**: Skills and slash commands now support `effort` frontmatter field to override session effort level

---

## MCP (Model Context Protocol) Servers

**What it is**: Open-source standard for AI-tool integrations enabling Claude Code to access external tools, databases, and APIs (hundreds of third-party services)

**Documentation**: https://code.claude.com/docs/en/mcp

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
- **claude.ai MCP connectors**: If logged into Claude Code with a Claude.ai account, MCP servers configured in Claude.ai are automatically available in Claude Code

---

## Plugins

**What it is**: Extensions that add custom functionality (commands, agents, skills, hooks, MCP servers) that can be shared across projects and teams

**Documentation**: https://code.claude.com/docs/en/plugins

**Key concepts**:
- **Components**: Skills (extensibility, includes legacy commands), Agents (specialized AI assistants), Hooks (event handlers), MCP Servers (external integrations)
- **Structure**: `.claude-plugin/plugin.json` (metadata), `skills/`, `agents/`, `hooks/` directories (legacy `commands/` still supported)
- **Installation**: `/plugin` interactive menu (browse/discover), direct commands (`install/enable/disable`)
- **Marketplaces**: Catalogs of plugins, add via `/plugin marketplace add your-org/claude-plugins`
- **Team configuration**: Automatic installation via `.claude/settings.json` in repository
- **Development**: Create plugin.json, add components, test locally, distribute through catalogs
- **Best practices**: Semantic versioning, comprehensive README, local testing, organize by functionality
- **User roles**: Plugin users (discover/install), Developers (create/distribute), Team leaders (governance/catalogs)
- **Search in installed list**: Type to filter plugins by name or description in the Installed tab
- **Auto-updates**: Toggle per marketplace; official marketplaces auto-update by default
- **SHA pinning**: Pin plugins to specific git commit SHAs for exact version control; use `sha` field in marketplace entry for reproducible builds; useful for enterprise audit trails
- **Plugin settings.json support**: Plugins can ship settings.json for default configuration applied when plugin is enabled

---

## Agents and Subagents

**What it is**: Specialized AI assistants that Claude Code can delegate tasks to. Each operates with its own separate context window and can be configured with specific system prompts, tools, and models for task-specific problem-solving.

**Documentation**: https://code.claude.com/docs/en/sub-agents

**Key concepts**:
- **Benefits**: Context preservation (separate windows prevent main conversation pollution), specialized expertise (fine-tuned instructions), reusability (work across projects), flexible permissions (different tool access levels)
- **Creation**: `/agents` then Create New Agent then Choose scope then Define/customize then Select tools then Save; or manually create Markdown files with YAML frontmatter
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
- **Background: true support**: Agent definitions can include `background: true` to configure agent to always run as a background task
- **Worktree isolation**: Subagents support `isolation: worktree` configuration to run the subagent in a temporary git worktree, giving it an isolated copy of the repository
- **Agent definition isolation**: Agent definitions support `isolation: worktree` in frontmatter to enable isolated working directories
- **Effort, maxTurns, disallowedTools frontmatter**: Plugin agents now support `effort`, `maxTurns`, and `disallowedTools` frontmatter fields for fine-grained control

---

## Built-in Commands

**What it is**: Claude Code's built-in slash commands for session management, configuration, and common operations. For custom commands, see Skills section above.

**Documentation**: https://code.claude.com/docs/en/interactive-mode#built-in-commands

**Key concepts**:
- **Session commands**: `/clear` (history), `/resume` (resume by name or ID), `/rename` (name session), `/teleport` (resume remote session), `/agents` (list configured agents)
- **Configuration**: `/config` (settings with search), `/model` (selection), `/permissions` (tool access), `/keybindings` (customize shortcuts)
- **Context management**: `/memory` (CLAUDE.md editing), `/compact` (reduce context), `/cost` (token usage), `/stats` (usage statistics)
- **Tools**: `/mcp` (server management), `/sandbox` (sandboxed bash), `/todos` (view task list), `/plan` (enter plan mode)
- **Help**: `/help` (usage), `/context` (view loaded context)
- **Remote**: `/remote-env` (configure remote environment)
- **MCP prompts**: Format `mcp__<server-name>__<prompt-name>` from MCP server prompts
- **Autocomplete**: Works at any position in input, not just at the beginning
- **Note**: Custom slash commands (`.claude/commands/`) have been merged into the Skills system; existing command files continue to work

---

## Hooks

**What it is**: Automated bash scripts that execute in response to specific events during Claude Code sessions, enabling custom automation, validation, and integration workflows

**Documentation**: https://code.claude.com/docs/en/hooks

**Key concepts**:
- **Execution model**: All matching hooks run in parallel with 60-second default timeout; receive JSON via stdin, return structured output to control Claude
- **Configuration locations**: `~/.claude/settings.json` (user), `.claude/settings.json` (project), `.claude/settings.local.json` (local project), enterprise managed policy, skill/agent/command frontmatter
- **11+ event types**: PreToolUse (before tool execution, can modify tool inputs), PostToolUse (after completion), UserPromptSubmit (prompt submission), Notification (permission requests with matcher values for event filtering), PermissionRequest (automatically approve/deny tool permissions), Stop (main agent finish, prompt-based matching), SubagentStart (subagent begins), SubagentStop (subagent finish), SessionStart (session begins), SessionEnd (session terminates), PreCompact (before context compacting), Setup (triggered via CLI flags), ConfigChange (configuration file changes), WorktreeCreate (when worktree is created), WorktreeRemove (when worktree is removed)
- **Setup hook**: Triggered via `--init`, `--init-only`, or `--maintenance` CLI flags; runs setup scripts for repository initialization, dependency installation, or maintenance tasks before the interactive session starts
- **Matcher patterns**: Exact (`Write`), regex (`Edit|Write`), wildcard (`*`), prompt-based (Stop hooks can match against user prompts), Notification and PermissionRequest matcher values for event-specific filtering; case-sensitive
- **Exit codes**: 0 (success, stdout to transcript), 2 (blocking error, stderr to Claude), other (non-blocking error, stderr to user)
- **JSON output**: Advanced control with `continue`, `decision`, `reason`, and hook-specific parameters
- **PreToolUse advanced features**:
  - **updatedInput parameter**: Allows modifying tool input parameters before execution; returned in JSON output to override original tool inputs
  - **ask parameter**: Triggers user confirmation dialog during hook execution; use in JSON output to prompt for approval before tool proceeds
  - **additionalContext parameter**: Adds context string to Claude before tool executes; returned in `hookSpecificOutput.additionalContext` field
- **Hook input fields**: `tool_use_id` field in PreToolUse and PostToolUse hooks enables correlation between pre/post events for same tool call
- **PermissionRequest hook**: Runs when user shown permission dialog; use decision control to allow/deny automatically; recognizes same matcher values as PreToolUse
- **Environment variables**: `CLAUDE_PROJECT_DIR` (project root path), `CLAUDE_ENV_FILE` (SessionStart persistence), `CLAUDE_CODE_REMOTE` (remote/local indicator)
- **Security warning**: Execute arbitrary shell commands automatically - validate/sanitize input, quote variables, use absolute paths, avoid sensitive files, test in safe environments
- **MCP integration**: Works with MCP tools using pattern `mcp__<server>__<tool>`
- **Debugging**: Use `claude --debug` for execution details, matched commands, exit codes, output
- **Component hooks**: Skills, agents, and slash commands can define hooks in frontmatter; scoped to component lifecycle
- **Once hooks**: `once: true` option runs hook only once per session for skills and commands
- **Prompt-based hooks**: `type: "prompt"` uses LLM to evaluate context; supported for Stop, SubagentStop, and other events
- **Stop hook last_assistant_message field**: Stop and SubagentStop hook events now include `last_assistant_message` field containing text content of the agent's final response, allowing hooks to access it without parsing transcript
- **WorktreeCreate hook**: Fires when a worktree is being created via --worktree or isolation: worktree; allows replacing default git behavior
- **WorktreeRemove hook**: Fires when a worktree is being removed; allows custom cleanup logic
- **InstructionsLoaded hook event**: Fires when CLAUDE.md or .claude/rules/*.md file is loaded into context
- **Elicitation hook event**: Fires when MCP server requests user input mid-task; hooks can intercept and respond programmatically
- **ElicitationResult hook event**: Fires after user responds to MCP elicitation, before response sent to server
- **PostCompact hook event**: Fires after Claude Code completes a compact operation
- **StopFailure hook event**: Fires when turn ends due to API error instead of normal Stop event

---

## Task Tool

**What it is**: Core tool allowing Claude to delegate work to specialized subagents with isolated contexts

**Documentation**: https://code.claude.com/docs/en/sub-agents

**Key concepts**:
- **Purpose**: Invoke subagents for specialized tasks while preserving main conversation context
- **Context isolation**: Each subagent operates with separate context window, preventing pollution of main conversation
- **Automatic selection**: Claude proactively identifies appropriate subagent based on task and descriptions
- **Explicit invocation**: Users can request specific subagent directly
- **Tool inheritance**: Subagents inherit or restrict tool access based on configuration
- **Result integration**: Subagent work summarized and returned to main conversation
- **Chaining support**: Multiple subagents can work sequentially on complex tasks
- **Permission control**: Can be disabled via `/permissions` or blocked with `Task(AgentName)` syntax for specific agents
- **Token count, tool uses, and duration metrics**: Task tool results now include token count, tool uses, and duration metrics for monitoring subagent efficiency

---

## AskUserQuestion Tool

**What it is**: Interactive tool for asking structured multiple-choice questions during conversations

**Documentation**: https://code.claude.com/docs/en/settings (Tools Available to Claude table)

**Key concepts**:
- **Purpose**: Enables Claude to ask structured questions with multiple-choice options
- **Features**: Single-select or multi-select modes, automatic "Other" option for custom input
- **Use cases**: Gathering preferences, clarifying ambiguous requirements, plan mode decisions
- **Question structure**: Header (short label), question text, 2-4 options with label and description
- **Behavioral constraints**: 60-second timeout, 1-4 questions per call, not available in subagents spawned via Task tool
- **Permission**: No permission required for this tool
- **Ctrl+G support**: External editor (Ctrl+G) now works in AskUserQuestion input field for composing longer responses

---

## LSP Tool

**What it is**: Language Server Protocol integration for semantic code intelligence

**Documentation**: https://code.claude.com/docs/en/settings (Tools Available to Claude table)

**Key concepts**:
- **Introduced**: v2.0.74 (2025-12)
- **Purpose**: Semantic code understanding beyond grep - go-to-definition, find references, hover documentation/types
- **Benefits**: More accurate than grep, understands code structure and types
- **Capabilities**: Navigate code definitions, find all references to symbols, get type information and documentation
- **Use cases**: Codebase exploration, refactoring support, understanding code relationships
- **Likely supported languages**: TypeScript/JavaScript, Python, other LSP-compatible languages

---

## Research Preview Agent Teams

**What it is**: Multi-agent collaboration feature allowing teams of Claude Code sessions to work together with shared tasks and inter-agent messaging

**Documentation**: https://code.claude.com/docs/en/agent-teams

**Key concepts**:
- **Coordination model**: One session acts as team lead, coordinating work, assigning tasks, and synthesizing results
- **Multiple instances**: Coordinate multiple Claude Code instances working together
- **Shared task management**: Tasks can be shared and coordinated across team members
- **Inter-agent messaging**: Agents can send messages to communicate progress and collaborate
- **Research preview**: Feature is still in active development and refinement
- **Use cases**: Large codebase refactoring, coordinated testing, parallel feature development

---

## Automatic Memory Recording and Recall

**What it is**: Claude automatically records and recalls memories as it works across sessions

**Documentation**: https://code.claude.com/docs/en/memory

**Key concepts**:
- **Auto memory directory**: Persistent directory where Claude records learnings, patterns, and insights
- **Distinction from CLAUDE.md**: CLAUDE.md contains instructions you write for Claude; auto memory contains notes Claude writes for itself
- **Session continuity**: Claude automatically recalls relevant memories from previous sessions
- **Pattern learning**: Claude learns and refines patterns from repeated tasks and workflows
- **Automatic updates**: No manual management required; Claude updates memories as it works

---

## Agent Teammate Sessions in Tmux

**What it is**: Agent teammate sessions in tmux now send and receive messages properly

**Documentation**: https://code.claude.com/docs/en/agent-teams

**Key concepts**:
- **Split-pane mode**: Requires either tmux or iTerm2 with it2 CLI
- **Message passing**: Teammates can now properly send and receive messages within split panes
- **Async collaboration**: Enables true asynchronous collaboration between teammates
- **Terminal integration**: Works seamlessly within terminal split-pane workflows

---

## TeammateIdle Hook Event

**What it is**: New TeammateIdle hook event fires when an agent team teammate is about to go idle

**Documentation**: https://code.claude.com/docs/en/hooks

**Key concepts**:
- **Trigger**: Fires when agent team teammate is about to go idle after finishing its turn
- **Use cases**: Enforce quality gates before teammate stops working
- **Team coordination**: Enables custom validation or handoff logic between team members
- **Integration**: Works with standard hook execution model

---

## TaskCompleted Hook Event

**What it is**: New TaskCompleted hook event fires when a task is being marked as completed

**Documentation**: https://code.claude.com/docs/en/hooks

**Key concepts**:
- **Trigger contexts**: Fires in two situations:
  - When any agent explicitly marks a task as completed through TaskUpdate tool
  - When agent team teammate finishes its turn with in-progress tasks
- **Use cases**: Validation, notifications, cleanup, quality assurance
- **Integration**: Works with standard hook execution model and team workflows

---

## Sub-agent Spawning Restrictions with Task(agent_type)

**What it is**: Support for restricting which sub-agents can be spawned via Task(agent_type) syntax in tools field

**Documentation**: https://code.claude.com/docs/en/sub-agents

**Key concepts**:
- **Syntax**: Use `Task(agent_type)` in `tools` field to restrict spawnable subagent types
- **Security**: Limits which specialized agents can be invoked by default
- **Tool field controls**: Agents can specify exactly which subagent types they're allowed to spawn
- **Flexibility**: Enables fine-grained control over agent composition and delegation

---

## Persistent Memory with Configurable Scope

**What it is**: Persistent memory support for agents with configurable scope (user, project, or local)

**Documentation**: https://code.claude.com/docs/en/memory

**Key concepts**:
- **Memory field**: `memory` field in agent frontmatter gives subagent persistent directory surviving across conversations
- **Three scopes**: User (cross-project), Project (team-shared), Local (agent-specific)
- **Scope hierarchy**: Determines how broadly the memory applies and persists
- **Use cases**: Learning patterns, maintaining context across related tasks, team knowledge sharing

---

## Claude Opus 4.6 Availability

**What it is**: Claude Opus 4.6 is now available as a model option in Claude Code

**Documentation**: https://code.claude.com/docs/en/settings

**Key concepts**:
- **Model option**: Opus 4.6 now selectable via `/model opus` or model selection
- **Thinking depth**: For Opus 4.6, thinking depth is controlled by Adjust effort level instead of traditional controls
- **Fast mode**: Fast mode now available for Opus 4.6
- **Configuration**: Can be set as default via settings or environment variables
- **Extended context**: Opus 4.6 supports full 1 million token context window for both plan and execution modes
- **1M context window**: Full million-token context window available for extended context sessions

---

## Skills Auto-load from Additional Directories

**What it is**: Skills now auto-load from additional directories beyond the standard skill locations

**Documentation**: https://code.claude.com/docs/en/skills

**Key concepts**:
- **Automatic discovery**: Claude Code discovers skills from nested `.claude/skills/` directories
- **Monorepo support**: When working with files in subdirectories, Claude Code looks for skills in `packages/frontend/.claude/skills/` etc.
- **Flexible organization**: Enables organizing skills by project structure rather than centralized location
- **Nested directories**: Skills auto-discovered recursively from nested structures

---

## Fast Mode for Opus 4.6

**What it is**: Fast mode is now available for Opus 4.6 model

**Documentation**: https://code.claude.com/docs/en/settings

**Key concepts**:
- **Model support**: Currently supported with Opus 4.6 only
- **Activation**: See Adjust effort level setting
- **Performance**: Faster responses with Opus 4.6 capabilities
- **Use cases**: Quick iterations, rapid prototyping, performance-sensitive workflows

---

## Claude Sonnet 4.6 Support

**What it is**: Introduced Claude Sonnet 4.6 support with full 1M context window

**Documentation**: https://code.claude.com/docs/en/model-config

**Key concepts**:
- **Latest model**: Sonnet 4.6 is now the daily coding model with full 1 million token context window
- **Extended context**: Uses latest Sonnet model (currently Sonnet 4.6) for daily coding tasks
- **1M context support**: Full million-token extended context window for comprehensive code analysis
- **Default choice**: Sonnet 4.6 is the default model for routine development work

---

## MCP OAuth Authentication Step-up Support

**What it is**: Enhanced MCP OAuth authentication with step-up auth and discovery caching

**Documentation**: https://code.claude.com/docs/en/mcp

**Key concepts**:
- **Authentication tokens**: Stored securely and refreshed automatically
- **Step-up authentication**: Support for additional authentication challenges when needed
- **Discovery caching**: MCP server discovery results cached for improved performance
- **Improved UX**: Seamless token refresh without user intervention

---

## ConfigChange Hook Event

**What it is**: Added ConfigChange hook event for security auditing of configuration file changes

**Documentation**: https://code.claude.com/docs/en/hooks

**Key concepts**:
- **Trigger**: Runs when a configuration file changes during a session
- **Use cases**: Audit settings changes, enforce security policies, block unauthorized modifications
- **Security**: Enables monitoring and control of configuration modifications
- **Integration**: Works with standard hook execution model

---

## last_assistant_message Field in Stop and SubagentStop Hooks

**What it is**: Added last_assistant_message field to Stop and SubagentStop hook events

**Documentation**: https://code.claude.com/docs/en/hooks

**Key concepts**:
- **Field content**: Contains text content of the subagent's final response
- **Access without parsing**: Hooks can access final response without parsing transcript file
- **Use cases**: Creating summaries, extracting final results, validation of agent outputs
- **Integration**: Available in both Stop and SubagentStop hook events

---

## /simplify Skill

**What it is**: Skill to review recently changed files for code reuse, quality, and efficiency issues

**Documentation**: https://code.claude.com/docs/en/skills

**Key concepts**:
- Review your recently changed files for code reuse, quality, and efficiency issues
- Spawns three review agents in parallel
- Analyzes modifications for potential improvements and consolidation
- Helps maintain code quality in active development

---

## /batch Skill

**What it is**: Skill to orchestrate large-scale changes across codebase in parallel with background agents

**Documentation**: https://code.claude.com/docs/en/skills

**Key concepts**:
- Orchestrate large-scale changes across a codebase
- Researches the codebase and decomposes work into 5-30 independent units
- Uses parallel background agents for efficient bulk modifications
- Ideal for refactoring, dependency updates, and cross-cutting changes

---

## /loop Command

**What it is**: Command for recurring prompt or slash command execution on an interval

**Documentation**: https://code.claude.com/docs/en/skills

**Key concepts**:
- Run a prompt repeatedly on an interval while session stays open
- Useful for monitoring tasks, periodic checks, and continuous workflows
- Runs within session context with automatic repetition

---

## /claude-api Skill

**What it is**: Skill for building Claude API applications with reference material

**Documentation**: https://code.claude.com/docs/en/skills

**Key concepts**:
- Load Claude API reference material for your project's language
- Supported languages: Python, TypeScript, Java, Go, Ruby, C#, PHP, cURL
- Includes Agent SDK reference material
- Enables API-based Claude integration development

---

## Voice STT Support for 10 New Languages

**What it is**: Speech-to-text support now available for 20 languages total

**Documentation**: https://code.claude.com/docs/en/voice-dictation

**Key concepts**:
- Supported dictation languages: Czech, Danish, Dutch, English, French, German, Greek, Hindi, Indonesian, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, Spanish, Swedish, Turkish, Ukrainian
- 20 languages total supported
- Enables voice input in multiple languages
- Expands accessibility for international users

---

## voice:pushToTalk Keybinding

**What it is**: Customizable voice activation keybinding

**Documentation**: https://code.claude.com/docs/en/voice-dictation

**Key concepts**:
- Push-to-talk key bound to voice:pushToTalk in Chat context
- Defaults to Space key
- Rebindable in ~/.claude/keybindings.json
- Enables flexible voice input activation

---

## Effort Level Display on Logo and Spinner

**What it is**: Current effort level now displays on logo and spinner

**Documentation**: https://code.claude.com/docs/en/model-config

**Key concepts**:
- Displays effort level next to logo and spinner (e.g., "with low effort")
- Visual indicator of current thinking/reasoning level
- Improves awareness of model behavior settings

---

## WorktreeCreate Hook Event

**What it is**: Hook event when creating isolated working copy via --worktree or subagent isolation

**Documentation**: https://code.claude.com/docs/en/hooks

**Key concepts**:
- Fires when creating isolated working copy
- Can be triggered by --worktree flag or subagent isolation
- Allows custom handling of worktree creation
- Enables pre-configuration of isolated environments

---

## WorktreeRemove Hook Event

**What it is**: Hook event when a worktree is being removed

**Documentation**: https://code.claude.com/docs/en/hooks

**Key concepts**:
- Fires when worktree is being removed
- Triggered on session exit or subagent completion
- Allows custom cleanup logic
- Enables post-cleanup operations

---

## isolation: worktree Support in Agent Definitions

**What it is**: Agents now support isolation: worktree to run in isolated git worktree

**Documentation**: https://code.claude.com/docs/en/sub-agents

**Key concepts**:
- Set `isolation: worktree` in agent frontmatter
- Runs subagent in temporary git worktree
- Provides isolated copy of repository
- Enables safe experimentation with separate working directory

---

## LSP Server startupTimeout Configuration

**What it is**: Configuration option for LSP server startup timeout

**Documentation**: https://code.claude.com/docs/en/plugins-reference

**Key concepts**:
- Max time to wait for server startup (milliseconds)
- Configurable per LSP server
- Helps with slow network connections or complex projects
- Improves startup behavior on resource-constrained systems

---

## ${CLAUDE_PLUGIN_DATA} Variable

**What it is**: Variable for plugin persistent state surviving updates

**Documentation**: https://code.claude.com/docs/en/plugins-reference

**Key concepts**:
- Persistent directory for plugin state surviving updates
- Use for installed dependencies (node_modules, virtual environments)
- Storage for generated code, caches, and other persistent files
- Enables plugin state preservation across version updates

---

## ${CLAUDE_SKILL_DIR} Variable for Skills

**What it is**: Variable for skills to reference their own directory

**Documentation**: https://code.claude.com/docs/en/skills

**Key concepts**:
- Directory containing the skill's SKILL.md file
- Use in bash injection commands to reference scripts/files
- Enables bundled resources access
- Supports skill portability across installations

---

## Response Text Streaming Line-by-Line

**What it is**: Response text now streams line-by-line as generated

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- Text streams line-by-line instead of character-by-character
- Improves readability of streamed content
- Enables better parsing of structured outputs
- Better user experience for long-form responses

---

## Terminal Notifications from Tmux

**What it is**: Terminal notifications now reach outer terminal when running inside tmux

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- Notifications properly escape tmux panes
- Reach the outer terminal even in nested tmux sessions
- Improves notification delivery reliability
- Better integration with tmux workflows
