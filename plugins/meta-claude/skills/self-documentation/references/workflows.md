# Workflows

Productivity features, keyboard shortcuts, and workflow automation in Claude Code.

**Last updated**: 2026-02-01

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

---

## Customizable Keyboard Shortcuts

**What it is**: Configure keybindings per context, create chord sequences, and personalize Claude Code workflow

**Documentation**: https://code.claude.com/docs/en/keybindings

**Key concepts**:
- **Configuration**: Run `/keybindings` to create or open `~/.claude/keybindings.json`; changes auto-detected without restart
- **Contexts**: Bindings apply to specific contexts (Global, Chat, Autocomplete, Confirmation, Transcript, HistorySearch, Task, etc.)
- **Actions**: Follow `namespace:action` format (e.g., `chat:submit`, `app:toggleTodos`)
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
- **Chat**: chat:submit, chat:cancel, chat:cycleMode, chat:modelPicker, chat:thinkingToggle, chat:externalEditor, chat:stash, chat:imagePaste
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

**Documentation**: https://code.claude.com/docs/en/interactive-mode

**Key concepts**:
- Available in interactive mode message selector
- Allows creating summaries from specific conversation points
- Useful for extracting relevant context from long conversations
- Can focus on particular message ranges rather than full history
