# Workflows

Productivity features, keyboard shortcuts, and workflow automation in Claude Code.

**Last updated**: 2026-03-21

---

## Interactive Mode & Keyboard Shortcuts

**What it is**: Terminal interface controls for navigation, editing, and workflow management with extensive keyboard shortcuts

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- **General controls**: Ctrl+C (interrupt), Ctrl+D (exit), Ctrl+G (external editor), Ctrl+L (clear screen), Ctrl+O (toggle verbose/transcript), Ctrl+R (history search), Ctrl+V/Alt+V (paste images), Shift+Tab/Alt+M (permission modes), Ctrl+T (toggle task list)
- **Multiline entry**: `\` + Enter, Option+Enter (macOS), Shift+Enter (after /terminal-setup)
- **Quick commands**: `#` (add to memory), `/` (slash commands), `!` (direct bash), `@` (file autocomplete)
- **Vim mode**: Standard navigation (h/j/k/l, w, b, f, t) and editing (dd, cc, x) with Esc mode switching; expanded motions for improved navigation; arrow key history navigation when cursor at input boundaries
- **Command history**: Per-directory storage with Ctrl+R interactive search and highlighting
- **Background tasks**: Ctrl+B to run long processes asynchronously with output buffering via TaskOutput tool; unified backgrounding for bash commands and agents
- **Bash mode**: `!` prefix bypasses Claude's interpretation while maintaining conversation context; supports history-based autocomplete (type partial command and press Tab to complete from previous `!` commands in current project)
- **Kill ring**: Ctrl-Y yanks most recent deletion, Alt-Y cycles through older deletions
- **Model switching**: Alt+P (Linux/Windows) or Option+P (macOS) to switch models mid-prompt
- **Thinking toggle**: Alt+T to enable/disable extended thinking mode (requires /terminal-setup); sticky across sessions
- **Slash command autocomplete**: Works anywhere in input, not just at the beginning
- **Real-time thinking**: Ctrl+O verbose/transcript mode now shows thinking blocks as they stream in real-time
- **Ctrl+F keybinding**: Kill all background agents; press twice within 3 seconds to confirm
- **chat:newline action**: Configurable keybinding action for multiline input (Shift+Enter out of the box in iTerm2, WezTerm, Ghostty, and Kitty)

---

## Customizable Keyboard Shortcuts

**What it is**: Configure keybindings per context, create chord sequences, and personalize Claude Code workflow

**Documentation**: https://code.claude.com/docs/en/keybindings

**Key concepts**:
- **Configuration**: Run `/keybindings` to create or open `~/.claude/keybindings.json`; changes auto-detected without restart
- **Contexts**: Bindings apply to specific contexts (Global, Chat, Autocomplete, Confirmation, Transcript, HistorySearch, Task, etc.)
- **Actions**: Follow `namespace:action` format (e.g., `chat:submit`, `app:toggleTodos`); includes `chat:newline` for multiline input
- **Keystroke syntax**: Modifiers use `+` separator (ctrl+k, shift+tab, meta+p); chords are space-separated (ctrl+k ctrl+s)
- **Special keys**: escape/esc, enter/return, tab, space, up/down/left/right, backspace/delete
- **Uppercase letters**: Standalone uppercase implies Shift (K = shift+k); with modifiers treated as stylistic (ctrl+K = ctrl+k)
- **Unbinding**: Set action to `null` to unbind default shortcut
- **Reserved shortcuts**: Ctrl+C (interrupt) and Ctrl+D (exit) cannot be rebound
- **Terminal conflicts**: Ctrl+B (tmux prefix - press twice), Ctrl+A (screen prefix), Ctrl+Z (Unix suspend)
- **Vim mode interaction**: Keybindings handle component-level actions; vim mode handles text input level; Escape in vim switches modes instead of triggering chat:cancel
- **Validation**: Run `/doctor` to see keybinding warnings

**Available contexts**:
- Global, Chat, Autocomplete, Settings, Confirmation, Tabs, Help, Transcript
- HistorySearch, Task, ThemePicker, Attachments, Footer, MessageSelector
- DiffDialog, ModelPicker, Select, Plugin

**Common actions by context**:
- **Global**: app:interrupt, app:exit, app:toggleTodos, app:toggleTranscript
- **Chat**: chat:submit, chat:cancel, chat:cycleMode, chat:modelPicker, chat:thinkingToggle, chat:externalEditor, chat:stash, chat:imagePaste, chat:newline
- **Autocomplete**: autocomplete:accept, autocomplete:dismiss, autocomplete:previous, autocomplete:next
- **Confirmation**: confirm:yes, confirm:no, confirm:cycleMode, confirm:toggleExplanation
- **History**: history:search, history:previous, history:next

---

## Task Management System

**What it is**: Enhanced task system with dependency tracking and tools for creating, updating, and querying tasks

**Documentation**: https://code.claude.com/docs/en/settings (Environment variables), https://code.claude.com/docs/en/interactive-mode (Task list section)

**Key concepts**:
- **Core tools**: TaskCreate (create tasks with dependencies), TaskUpdate (update status/dependencies/details), TaskGet (retrieve full task details), TaskList (list all tasks with status)
- **Task dependencies**: Tasks can specify dependencies on other tasks; helps Claude organize complex multi-step work
- **Persistence**: Tasks persist across context compactions and sessions
- **Task list view**: Press Ctrl+T to toggle task list display; shows up to 10 tasks at a time with status indicators (pending, in progress, complete); dynamically adjusts visible items based on terminal height
- **Shared task lists**: Set `CLAUDE_CODE_TASK_LIST_ID` environment variable to share a task list across sessions using named directory in `~/.claude/tasks/`
- **Management**: Ask Claude directly to "show me all tasks" or "clear all tasks" for full list or cleanup
- **Task deletion**: Tasks can be deleted via the `TaskUpdate` tool

**Expected workflow**:
1. Claude creates tasks with dependencies using TaskCreate
2. Updates task status as work progresses with TaskUpdate
3. Queries task details when needed with TaskGet
4. Lists all tasks and their relationships with TaskList
5. View task status in terminal with Ctrl+T toggle

**Configuration for shared tasks**:
```bash
CLAUDE_CODE_TASK_LIST_ID=my-project claude
```

---

## Checkpointing & Rewind

**What it is**: Automatic file state tracking with ability to rewind conversation and/or code changes to previous points

**Documentation**: https://code.claude.com/docs/en/checkpointing

**Key concepts**:
- **Automatic tracking**: Every user prompt creates a checkpoint; persists across sessions
- **Access**: Press Escape twice or type `/rewind` to open restoration menu
- **Three restoration options**: Conversation only (keeps code), Code only (keeps conversation), Both (full rewind)
- **Use cases**: Experiment with implementations, recover from bugs, iterate while maintaining stable states
- **Limitations**: Does not track Bash command modifications (rm, mv, cp), external file changes, or concurrent session edits
- **Automatic cleanup**: Checkpoints clean up after 30 days (configurable)
- **Complementary to Git**: Designed for quick session-level recovery, not replacement for version control

---

## Git Workflow Automation

**What it is**: Standardized patterns for commit creation and pull request workflows with safety checks

**Key concepts**:
- Uses Conventional Commits format: `type(scope): subject`
- Automatic co-authoring with Claude
- Multiple safety checks and git best practices

**Commit creation workflow**:
1. Run `git status`, `git diff`, `git log` **in parallel** to understand context
2. Analyze all staged changes and draft commit message
3. Validate commit message follows conventions (type, scope, subject)
4. Add untracked files, create commit with heredoc format, run `git status` after
5. If pre-commit hook modifies files, verify safety to amend (authorship check, not pushed)

**PR creation workflow**:
1. Run `git status`, `git diff`, check remote tracking **in parallel**
2. Run `git log` and `git diff [base-branch]...HEAD` to understand full branch history
3. Analyze **all commits** in branch (not just latest)
4. Create PR with format: Summary (1-3 bullets), Test plan (checklist), Claude attribution
5. Session automatically links to PR when created via `gh pr create`

**Safety protocols**:
- Never update git config
- Never force push to main/master (warn if requested)
- Never skip hooks (--no-verify) unless explicitly requested
- Only amend commits if: (1) user explicitly requested OR (2) adding pre-commit edits
- Always check authorship before amending: `git log -1 --format='%an %ae'`
- Never commit unless explicitly asked

---

## PR Review Status Indicator

**What it is**: Display of pull request review status in the prompt footer showing current branch's PR state

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- **Display location**: Clickable PR link in footer (e.g., "PR #446") with colored underline
- **Color meanings**: Green (approved), Yellow (pending review), Red (changes requested), Gray (draft), Purple (merged)
- **Interaction**: Cmd+click (Mac) or Ctrl+click (Windows/Linux) to open PR in browser
- **Auto-update**: Status updates automatically every 60 seconds
- **Requirements**: Requires `gh` CLI installed and authenticated (`gh auth login`)

---

## Parallel Execution

**What it is**: Concurrent execution of multiple independent tool calls or subagents in a single message for efficiency

**Key concepts**:
- Claude sends multiple independent tool calls in one message when safe to do so
- User can request "run agents in parallel" for concurrent subagent execution
- Each parallel call executes concurrently; all must complete before Claude continues
- Critical constraint: Never parallelize dependent operations (e.g., Read before Edit)

**Common patterns**:
- **Git pre-commit**: `git status`, `git diff`, `git log` together
- **Multi-file reads**: Several `Read` calls for different files
- **Parallel agents**: `code-reviewer` + `test-runner` simultaneously
- **Codebase search**: Multiple `Grep` with different patterns

**Constraints**:
- Never use placeholders or guess parameters - wait for actual values
- Sequential dependencies require sequential calls
- Results from all calls needed before continuing

---

## Background Agent Support

**What it is**: Ability for agents to run in the background while you continue working, with asynchronous message passing

**Documentation**: https://code.claude.com/docs/en/sub-agents

**Key concepts**:
- Agents can now run in background while user continues working
- Agents and bash commands can run asynchronously and send messages to wake up the main agent
- Enables true parallel workflows with human and agent working simultaneously
- Ctrl+B works for both bash commands and agents
- Disable all background task functionality with `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`
- **Pre-launch permissions**: Background agents prompt for tool permissions before launching, reducing mid-execution permission failures
- **MCP tools not available**: Background subagents cannot use MCP tools

**Expected behavior**:
- Start an agent task that runs in background
- Continue typing/working on other tasks
- Agent can send messages to notify main agent when done
- Results become available when background work completes

**Use cases**:
- Long-running analysis tasks
- Test suites running while implementing next feature
- Documentation generation in background
- Complex search/exploration while coding

---

## Named Sessions

**What it is**: Ability to name conversation sessions for easier resumption and organization

**Documentation**: https://code.claude.com/docs/en/common-workflows

**Key concepts**:
- Use `/rename` to name current session
- Use `/resume <name>` in REPL to resume named session
- Use `claude --resume <name>` from terminal to resume
- Use `claude --from-pr <number>` to resume sessions linked to a specific PR
- Makes session management more intuitive than using session IDs
- `/rename` now auto-generates session name from conversation context

**Workflow examples**:
```bash
# In Claude Code session:
/rename feature-auth-refactor

# Later, resume from terminal:
claude --resume feature-auth-refactor

# Or resume from within Claude Code:
/resume feature-auth-refactor

# Resume session linked to a PR:
claude --from-pr 123
```

**Benefits**:
- Human-readable session identifiers
- Easy switching between work contexts
- Better organization of related work
- No need to remember cryptic session IDs

---

## /stats Command

**What it is**: Visualize daily usage, session history, streaks, and model preferences

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- `/stats` command provides detailed usage statistics
- Shows personal usage patterns and metrics
- Press 'r' to cycle through date ranges (Last 7 days, Last 30 days, All time)
- Includes visual graphs and tracking features

**Expected metrics**:
- Favorite/most-used model
- Usage over time (graph)
- Usage streak (consecutive days)
- Session history
- Possibly token counts, session counts, etc.

**Usage**:
```
> /stats
# View statistics, press 'r' to cycle date ranges
```

---

## /config Command with Search

**What it is**: Settings interface with search functionality for finding specific settings

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- `/config` opens Settings interface (Config tab)
- Type to search and filter settings
- Makes finding specific settings easier
- Keyword-based filtering of config options

**Usage**:
```
> /config
# Type to search for settings by name or description
```

**Expected behavior**:
- Type search terms to filter settings
- Filter visible config options dynamically
- Quick navigation to specific settings

---

## /plan Command

**What it is**: Direct entry into plan mode from the prompt

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- Use `/plan` to enter plan mode directly
- Alternative to typing "let's plan" or similar prompts
- Triggers plan mode with all its features (research, questions, structured planning)
- Shortcut for common workflow transition

**Usage**:
```
> /plan
# Claude enters plan mode and begins gathering requirements
```

---

## Remote Session Management

**What it is**: Commands to manage remote sessions from claude.ai

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- `/teleport` - Resume a remote session by ID or open picker (claude.ai subscribers)
- `/remote-env` - Configure remote session environment (claude.ai subscribers)
- Enables seamless transition between web and CLI workflows
- Sessions sync between platforms

**Workflow**:
1. Start work on claude.ai web interface
2. Use `/teleport` in CLI to resume that session
3. Continue work with full CLI capabilities
4. Changes sync back to web session

**Benefits**:
- Work continuity across platforms
- Use web for planning, CLI for execution
- Access sessions from anywhere

---

## /debug Command

**What it is**: Command for Claude to help troubleshoot the current session

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- Available in interactive mode for session troubleshooting
- Helps Claude analyze current session state and debug issues
- Useful for understanding complex issues or session state problems
- Can include optional description of the issue: `/debug [description]`

**Expected workflow**:
1. Encounter issue or unusual behavior in session
2. Run `/debug` with optional description
3. Claude reads session debug log and analyzes it
4. Claude suggests fixes or explains the behavior

---

## Summarize from Here Feature

**What it is**: Message selector option to create summaries from selected conversation points

**Documentation**: https://code.claude.com/docs/en/checkpointing

**Key concepts**:
- Available in interactive mode message selector
- Allows creating summaries from specific conversation points
- Useful for extracting relevant context from long conversations
- Can focus on particular message ranges rather than full history
- Compress conversation from selected point forward into summary
- Messages before selected point stay intact; selected message and subsequent messages replaced with compact AI-generated summary

---

## --add-dir CLI Flag

**What it is**: Add additional working directories for Claude to access with enabled plugins and known marketplaces support

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- Add additional working directories for Claude to access (validates each path exists as a directory)
- Enables reading enabledPlugins and extraKnownMarketplaces from additional directories
- Useful for monorepo setups where multiple projects need separate plugin configurations
- Each directory path is validated to ensure it exists

**Usage**:
```bash
claude --add-dir /path/to/directory
```

---

## @-mention File Suggestions Performance Improvements

**What it is**: Enhanced @-mention file suggestions with session caching for faster performance

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- File path mention - Trigger file path autocomplete
- Session caching for faster suggestion loading
- Improved performance when suggesting files for @-mentions
- Cached suggestions persist across the session
- Reduces response time when working with many files

---

## --worktree Flag for Isolated Git Worktree Sessions

**What it is**: Added --worktree (-w) flag for isolated git worktree sessions

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- Start Claude in an isolated git worktree at `<repo>/.claude/worktrees/<name>`
- If no name is given, one is auto-generated
- Provides isolated working directory for experiments without affecting main branch
- Useful for parallel feature development or testing

**Usage**:
```bash
claude --worktree
claude --worktree my-feature
claude -w experiment-1
```

---

## claude agents CLI Command

**What it is**: Added claude agents CLI command to list configured agents

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- List all configured subagents, grouped by source
- Shows available agents in current environment
- Displays agent names, descriptions, and source locations
- Useful for discovering available agents and understanding agent configuration

**Usage**:
```bash
claude agents
```

---

## Copy OAuth URL Keyboard Shortcut

**What it is**: Keyboard shortcut to copy OAuth login URL to clipboard when browser doesn't open automatically

**Documentation**: https://code.claude.com/docs/en/authentication

**Key concepts**:
- Press 'c' during login to copy OAuth URL to clipboard
- Useful when browser auto-open fails in restricted environments
- Allows manual pasting of login URL into browser
- Improves login experience for headless systems

**Expected workflow**:
1. Start login process with `claude auth login`
2. If browser doesn't open automatically
3. Press 'c' to copy URL to clipboard
4. Paste URL manually in your browser to complete login

---

## Claude Auth CLI Subcommands

**What it is**: CLI subcommands for authentication management: login, status, and logout

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- **claude auth login** - Authenticate with Claude Code
- **claude auth status** - Check current authentication status as JSON
- **claude auth logout** - Sign out from current session
- Allows direct authentication management from terminal
- Status command returns JSON format for scripting

**Usage**:
```bash
claude auth login        # Start authentication flow
claude auth status       # Check if authenticated (returns JSON)
claude auth logout       # Sign out
```

---

## /context Command

**What it is**: Visualize current context usage as a colored grid with optimization suggestions

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- Display current context usage visually
- Shows optimization suggestions for context-heavy tools
- Identifies memory bloat and capacity warnings
- Helps understand what's consuming your context

---

## /copy Command with Write Mode

**What it is**: Interactive picker to copy code blocks with optional write mode using 'w' key

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- `/copy` copies the latest response to clipboard
- `/copy N` copies the Nth-latest response
- Press 'w' key to write selections directly to files
- Bypasses clipboard for large code blocks
- Interactive selection interface for choosing which blocks to copy/write

---

## /effort Slash Command

**What it is**: Command to set model effort level (low, medium, high, max)

**Documentation**: https://code.claude.com/docs/en/model-config

**Key concepts**:
- **low** - Fast, basic responses (Sonnet default)
- **medium** - Balanced approach (Opus default)
- **high** - Deep reasoning (requires Opus 4.6)
- **max** - Maximum reasoning (Opus 4.6 only, session-only)
- **auto** - Reset to model default
- Low/medium/high persist across sessions
- Max applies to current session only

**Usage**:
```bash
/effort low        # Fast mode
/effort medium     # Balanced
/effort high       # Deep reasoning
/effort max        # Maximum (Opus 4.6)
/effort auto       # Reset to default
```

---

## /color Command

**What it is**: Command for all users to set prompt bar color

**Documentation**: https://code.claude.com/docs/en/commands

**Key concepts**:
- Set the prompt bar color for the current session
- Available colors: red, blue, green, yellow, purple, orange, pink, cyan
- Use `default` to reset to default color
- Color preference persists during session

**Usage**:
```bash
/color blue        # Set prompt bar to blue
/color red         # Set to red
/color default     # Reset to default
```

---

## Session Name Display on Prompt Bar

**What it is**: Session name displays on prompt bar when using /rename command

**Documentation**: https://code.claude.com/docs/en/commands

**Key concepts**:
- `/rename` to set a custom session name
- Name displays prominently on the prompt bar
- Without a name, auto-generates one from conversation history
- Makes current session context immediately visible
- Helpful when managing multiple parallel sessions

**Usage**:
```bash
/rename my-feature    # Set session name
/rename              # Auto-generate from conversation
```

---

## -n / --name CLI Flag

**What it is**: Flag to set display name for session at startup

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- Set session display name when starting Claude Code
- Name shown in `/resume` and terminal title
- Alternative to renaming within session
- Useful for scripts and automation

**Usage**:
```bash
claude -n my-project
claude --name feature-review
```

---

## --channels Research Preview Flag

**What it is**: Research preview flag enabling MCP servers to push messages into sessions

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- (Research preview) MCP servers whose channel notifications Claude should listen for
- Specify servers to receive async messages from during session
- Enables proactive MCP tool notifications
- Advanced feature for MCP server integration

---

## --console Flag for Anthropic Console Authentication

**What it is**: Flag for claude auth login targeting Anthropic Console API billing authentication

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- `--console` flag for Anthropic Console authentication
- Sign in with Anthropic Console for API billing access
- `--email` to pre-fill email address
- `--sso` to force SSO authentication
- Separate from web claude.ai authentication

**Usage**:
```bash
claude auth login --console              # Sign in to Anthropic Console
claude auth login --console --email user@example.com
claude auth login --sso                  # Force SSO
```

---

## /extra-usage Command for VS Code

**What it is**: Command to configure extra usage in VS Code extension

**Documentation**: https://code.claude.com/docs/en/commands

**Key concepts**:
- Configure extra usage to keep working when rate limits are hit
- Available in VS Code extension
- Helps manage usage quota and continuity
- Provides context-aware usage configuration

---

## /reload-plugins Command

**What it is**: Command to reload all active plugins without restarting

**Documentation**: https://code.claude.com/docs/en/commands

**Key concepts**:
- Reload all active plugins to apply pending changes
- No restart required
- Reports counts for each reloaded component
- Flags any load errors
- Useful after plugin installation or updates

**Usage**:
```bash
/reload-plugins    # Reloads agents, skills, hooks, etc.
```

---

## Remote Control CLI Subcommand

**What it is**: Start a Remote Control server to control Claude Code from Claude.ai or the Claude app

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- Starts server mode (no local interactive session)
- Allows remote control from Claude.ai web interface
- Use optional name argument to set server name
- Enables headless Claude Code control
- Supports server mode flags for configuration

**Usage**:
```bash
claude remote-control              # Start server
claude remote-control my-server    # Named server
/remote-control my-session         # In-session command
/remote-control                    # Unnamed session
```

---

## Optional Name Argument to /remote-control

**What it is**: /remote-control command now accepts optional name for the session

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- Pass name argument to /remote-control
- Sets session name shown in Claude.ai
- Optional - unnamed sessions supported
- Name appears in session management UI
- Consistent with other session naming features
