# Undocumented Features

Features mentioned in Claude Code release notes but not yet covered in official documentation. Information is based on release note descriptions and observed behavior. Details may be incomplete or subject to change.

**Latest Release**: v2.1.81

---

## Permission Prompt Feedback

**What it is**: Ability to provide feedback when accepting permission prompts

**Introduced**: v2.1.7

**What we know**:
- Users can now provide feedback when accepting permission prompts
- Helps improve permission system based on user experience
- Likely integrated into permission dialog UI

**Use cases**:
- Report overly restrictive permissions
- Suggest better permission defaults
- Help Anthropic improve permission UX

---

## Agent Final Response in Task Notifications

**What it is**: Display of agent's final response inline in task completion notifications

**Introduced**: v2.1.7

**What we know**:
- Task notifications now show the agent's final response inline
- Provides context without needing to check task details separately
- Improves visibility into what agents accomplished

**Expected behavior**:
- Background task completes
- Notification shows both completion status and agent's summary
- Reduces need to navigate to task details

---

## OAuth/API Console URL Update

**What it is**: URL change for OAuth and API Console from anthropic.com to platform.claude.com

**Introduced**: v2.1.7

**What we know**:
- OAuth and API Console URLs now point to platform.claude.com
- Previously used anthropic.com domain
- Likely part of infrastructure consolidation

**Updated URLs**:
- OAuth: platform.claude.com/oauth
- API Console: platform.claude.com/console

---

## Session URL Attribution in Git

**What it is**: Automatic attribution of session URLs to commits and PRs from web sessions

**Introduced**: v2.1.9

**What we know**:
- Web sessions now add session URL attribution to commits and PRs
- Helps trace git activity back to originating web session
- Improves audit trail for web-based workflows

**Expected format**:
- Commit/PR includes URL to originating claude.ai session
- Enables jumping from git history to conversation context

---

## Trust Warning for Plugin Installation in VSCode

**What it is**: Warning dialog when installing plugins via VSCode extension

**Introduced**: v2.1.10

**What we know**:
- VSCode extension shows trust warning before plugin installation
- Improves security awareness when adding third-party plugins
- Aligns with VSCode security best practices

---

## Startup Keystroke Capture Improvement

**What it is**: Enhanced startup to capture keystrokes before REPL is fully ready

**Introduced**: v2.1.10

**What we know**:
- Startup improved to capture keystrokes earlier
- Prevents lost input during Claude Code initialization
- Improves responsiveness during startup phase

**Benefits**:
- No need to wait for full REPL readiness before typing
- Faster perceived startup time
- Better user experience for quick commands

---

## File Suggestions as Removable Attachments

**What it is**: Enhanced display of file suggestions as removable attachments in the UI

**Introduced**: v2.1.10

**What we know**:
- File suggestions now display as removable attachments
- Improves clarity of which files are included in context
- Allows easy removal before sending prompt

**Expected behavior**:
- Suggest files with @-mention
- Files appear as attachment chips
- Click to remove unwanted suggestions before submit

---

## Per-User Temp Directory Isolation

**What it is**: Isolated temporary directories for each user to prevent permission conflicts

**Introduced**: v2.1.23

**What we know**:
- Fixed per-user temp directory isolation preventing permission conflicts on shared systems
- Each user gets their own isolated temp directory
- Prevents conflicts when multiple users run Claude Code on same system

---

## TaskStop tool result improvement

**What it is**: Improved TaskStop tool to display the stopped command/task description in the result line instead of a generic 'Task stopped' message

**Introduced**: v2.1.30

**What we know**:
- TaskStop results now show the specific task that was stopped
- Provides better feedback about which background task was terminated
- Clearer output when managing multiple background tasks

---

## Extended Thinking Interruption Handling

**What it is**: Improved handling for extended thinking interruption

**Introduced**: v2.1.33

**What we know**:
- Improved robustness when extended thinking is interrupted
- Better error handling during thinking phase
- More graceful fallback to standard reasoning

---

## Heredoc Delimiter Parsing Security Improvement

**What it is**: Improved heredoc delimiter parsing to prevent command smuggling

**Introduced**: v2.1.38

**What we know**:
- Enhanced security in bash command parsing
- Prevents potential command injection via heredoc delimiters
- Protects against sophisticated shell command attacks

---

## Blocked Writes to .claude/skills in Sandbox Mode

**What it is**: Blocked writes to .claude/skills directory in sandbox mode for security

**Introduced**: v2.1.38

**What we know**:
- Sandbox mode now prevents writing to .claude/skills directory
- Prevents potential skill injection attacks from sandboxed code
- Improves security isolation in sandboxed environments

---

## File Resolution for @-mentions with Anchor Fragments

**What it is**: Improvements to file resolution for @-mentions with anchor fragments

**Introduced**: v2.1.41

**What we know**:
- Enhanced resolution of @-mentions when using anchor fragments
- Allows more precise file and location references
- Improves file suggestion accuracy

---

## Windows ARM64 Native Binary Support

**What it is**: Added Windows ARM64 (win32-arm64) native binary support

**Introduced**: v2.1.41

**What we know**:
- Native binary support for Windows running on ARM64 processors
- Previously required emulation on ARM-based Windows systems
- Improves performance on modern ARM-based Windows devices

---

## Startup Performance Improvements

**What it is**: Improved startup performance by deferring Zod schema construction

**Introduced**: v2.1.42

**What we know**:
- Startup process optimized with deferred schema validation
- Reduces initialization time for sessions
- Particularly beneficial for frequently-started sessions

---

## Prompt Cache Hit Rate Optimization

**What it is**: Improved prompt cache hit rates by moving date out of system prompt

**Introduced**: v2.1.42

**What we know**:
- System prompt refactored to improve cache efficiency
- Date moved to user context instead of system prompt
- Increases cache hit rates and reduces API costs
- Results in better token usage for sessions

---

## One-time Opus 4.6 Callout for Eligible Users

**What it is**: One-time Opus 4.6 callout for eligible users

**Introduced**: v2.1.42

**What we know**:
- One-time notification for users eligible to use Opus 4.6
- Appears in Claude Code when user qualifies
- Informs users about new model availability

---

## Guard Against Launching Claude Code Inside Another Session

**What it is**: Added guard against launching Claude Code inside another Claude Code session

**Introduced**: v2.1.41

**What we know**:
- Detects when Claude Code is launched from within another Claude Code session
- Prevents accidental nested session launch
- Shows warning or error to prevent user confusion

---

## SDKRateLimitInfo and SDKRateLimitEvent types

**What it is**: Added SDKRateLimitInfo and SDKRateLimitEvent types to SDK

**Introduced**: v2.1.45

**What we know**:
- New SDK types for handling rate limit information and events
- Based on release notes, specific documentation not yet available
- Provides structured way to handle rate limiting in SDK applications

---

## VS Code plan preview auto-updates

**What it is**: Improved VS Code plan preview with auto-updates and persistence

**Introduced**: v2.1.47

**What we know**:
- Plan preview feature in VS Code now auto-updates while working
- Maintains persistence across interactions
- Provides real-time feedback during planning phase

---

## added_dirs in statusline JSON workspace section

**What it is**: Added added_dirs to statusline JSON workspace section

**Introduced**: v2.1.47

**What we know**:
- New field added_dirs appears in statusline JSON workspace section
- Indicates additional directories added via --add-dir flag
- Enables status line customization to display working directories

---

## supportsEffort, supportedEffortLevels, supportsAdaptiveThinking SDK fields

**What it is**: SDK now includes supportsEffort, supportedEffortLevels, and supportsAdaptiveThinking fields

**Introduced**: v2.1.49

**What we know**:
- New SDK fields for detecting model adaptive effort capabilities
- Based on release notes, specific documentation not yet available
- Enables SDK applications to check model thinking mode support

---

## HTTP Hooks

**What it is**: Hooks that POST JSON to URLs and receive JSON responses

**Introduced**: v2.1.63

**What we know**:
- Hooks can now send HTTP POST requests to external URLs
- Supports JSON request/response format
- Enables integration with external webhook services
- Use cases: notifications, CI/CD integrations, monitoring

---

## Local Slash Command Output as System Messages

**What it is**: Local slash command output now appears as system messages rather than user-sent messages

**Introduced**: v2.1.63

**What we know**:
- Output from local slash commands displayed as system messages
- Better visual distinction from user inputs
- Improves clarity of command execution flow

---

## ENABLE_CLAUDEAI_MCP_SERVERS Environment Variable

**What it is**: Environment variable to opt out of Claude.ai MCP servers

**Introduced**: v2.1.63

**What we know**:
- Set to control whether MCP servers from Claude.ai are available
- Allows disabling Claude.ai-configured MCP servers
- Useful for restricted environments

---

## Worktree Field in Status Line Hook Commands

**What it is**: Status line hook commands now include worktree field with metadata

**Introduced**: v2.1.69

**What we know**:
- New worktree field added to status line hook command data
- Provides metadata about current worktree
- Enables worktree-aware status line customization

---

## /plan Optional Description Argument

**What it is**: Optional description argument added to /plan command

**Introduced**: v2.1.72

**What we know**:
- /plan now accepts optional description argument
- Allows providing context for planning phase
- Improves planning focus and direction

---

## CLAUDE_CODE_DISABLE_CRON Environment Variable

**What it is**: Environment variable to stop scheduled cron jobs

**Introduced**: v2.1.72

**What we know**:
- Set `CLAUDE_CODE_DISABLE_CRON=1` to stop cron job execution
- Disables scheduled/recurring tasks
- Useful for controlled execution environments

---

## Additional Bash Auto-approval Allowlist Items

**What it is**: Added lsof, pgrep, tput, ss, fd, fdfind to bash auto-approval list

**Introduced**: v2.1.72

**What we know**:
- More system tools automatically approved for bash execution
- Includes: lsof (open files), pgrep (process grep), tput (terminal control), ss (socket stats), fd/fdfind (file finder)
- Reduces permission prompts for common commands

---

## Cron Scheduling Tools

**What it is**: Tools for recurring prompts within sessions

**Introduced**: v2.1.71

**What we know**:
- New tools for scheduling recurring prompts or slash commands
- Supports interval-based execution
- Enables time-based automation within sessions

---

## Last-modified Timestamps on Memory Files

**What it is**: Memory files now include last-modified timestamps

**Introduced**: v2.1.75

**What we know**:
- Timestamps added to memory files for tracking purposes
- Helps identify recently updated memories
- Improves memory management and organization

---

## Hook Source Display in Permission Prompts

**What it is**: Permission prompts now show hook source (settings/plugin/skill)

**Introduced**: v2.1.75

**What we know**:
- Displays where a hook came from when requesting permissions
- Shows if hook is from settings, plugin, or skill
- Improves transparency of hook sources

---

## ExitWorktree Tool

**What it is**: Tool to leave EnterWorktree sessions

**Introduced**: v2.1.72

**What we know**:
- New tool for exiting worktree isolation
- Complements EnterWorktree functionality
- Enables clean exit from isolated sessions

---

## MCP Elicitation Support

**What it is**: Support for structured input via interactive dialogs in MCP

**Introduced**: v2.1.76

**What we know**:
- MCP servers can request structured input via interactive dialogs
- Enables more sophisticated MCP tool interactions
- Supports multi-field forms and complex inputs

---

## worktree.sparsePaths Setting

**What it is**: Setting for large monorepos using git sparse-checkout

**Introduced**: v2.1.76

**What we know**:
- Configuration for sparse-checkout paths in worktrees
- Useful for monorepos with selective file loading
- Improves performance with large repositories

---

## Show Turn Duration Toggle

**What it is**: Toggle to show turn duration in /config menu

**Introduced**: v2.1.79

**What we know**:
- Setting to control display of turn duration metrics
- Can be toggled via /config
- Helps users track session timing

---

## rate_limits Field in Statusline

**What it is**: Statusline scripts can now display Claude.ai rate limit usage data

**Introduced**: v2.1.80

**What we know**:
- New rate_limits field available in statusline JSON
- Shows rate limit information
- Enables rate-limit-aware status displays

---

## source: 'settings' Plugin Marketplace Source

**What it is**: Plugin marketplace source for inline plugin declarations via settings

**Introduced**: v2.1.80

**What we know**:
- Plugins can be declared directly in settings.json
- New source type for settings-based plugin configuration
- Enables configuration-driven plugin installation

---

## CLI Tool Usage Detection for Plugin Tips

**What it is**: Plugin tips now use CLI tool usage detection alongside file pattern matching

**Introduced**: v2.1.80

**What we know**:
- Plugin tips triggered by CLI tool usage
- Complements file pattern-based detection
- More sophisticated plugin recommendation system

---

## Parallel Tool Results Restoration on Resume

**What it is**: Resume now fully restores parallel tool results

**Introduced**: v2.1.80

**What we know**:
- Parallel tool execution results properly restored on session resume
- Maintains tool execution state across resume
- Improves state preservation for complex operations

---

## MCP OAuth Client ID Metadata Document (CIMD) Support

**What it is**: MCP OAuth now supports Client ID Metadata Document for servers without Dynamic Client Registration

**Introduced**: v2.1.81

**What we know**:
- Alternative OAuth approach for MCP servers
- Supports servers without Dynamic Client Registration capability
- Improves MCP OAuth compatibility

---

## --bare Flag for Scripted Calls

**What it is**: Flag to skip hooks, LSP, plugin sync, and skill directory walks for scripted calls

**Introduced**: v2.1.81

**What we know**:
- `--bare` flag for minimal initialization
- Disables hooks, LSP, plugin sync, and skill discovery
- Useful for lightweight scripted execution

---

## Plugin Freshness with Ref-tracked Plugins

**What it is**: Ref-tracked plugins re-clone on every load for improved plugin freshness

**Introduced**: v2.1.81

**What we know**:
- Plugins tracked by git ref are re-cloned on each load
- Ensures latest version from ref is always used
- Improves plugin update freshness for development

---

## MCP Read/Search Tools Collapse

**What it is**: MCP read/search tools collapse into single lines (expandable with Ctrl+O)

**Introduced**: v2.1.81

**What we know**:
- MCP read and search tool output collapsed by default
- Expandable with Ctrl+O for verbose mode
- Reduces visual clutter of tool output

---

## Resumed Sessions Switch to Original Worktree

**What it is**: Resumed sessions automatically switch back to their original worktree

**Introduced**: v2.1.81

**What we know**:
- Sessions resume in the worktree they were created in
- Automatic worktree switching on resume
- Better state preservation for worktree-specific sessions
