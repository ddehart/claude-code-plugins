# Workflows

Productivity features, keyboard shortcuts, and workflow automation in Claude Code.

**Last updated**: 2025-01-09

---

## Interactive Mode & Keyboard Shortcuts

**What it is**: Terminal interface controls for navigation, editing, and workflow management with extensive keyboard shortcuts

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/interactive-mode

**Key concepts**:
- **General controls**: Ctrl+C (interrupt), Ctrl+D (exit), Ctrl+L (clear screen), Ctrl+O (toggle verbose/transcript), Ctrl+R (history search), Ctrl+V/Alt+V (paste images), Tab (thinking toggle), Shift+Tab/Alt+M (permission modes)
- **Multiline entry**: `\` + Enter, Option+Enter (macOS), Shift+Enter (after /terminal-setup)
- **Quick commands**: `#` (add to memory), `/` (slash commands), `!` (direct bash), `@` (file autocomplete)
- **Vim mode**: Standard navigation (h/j/k/l, w, b) and editing (dd, cc, x) with Esc mode switching
- **Command history**: Per-directory storage with Ctrl+R interactive search and highlighting
- **Background tasks**: Ctrl+B to run long processes asynchronously with output buffering via BashOutput tool
- **Bash mode**: `!` prefix bypasses Claude's interpretation while maintaining conversation context
- **Kill ring** (v2.0.49+): Ctrl-Y yanks most recent deletion, Alt-Y cycles through older deletions
- **Model switching** (v2.0.65+): Alt+P (Linux/Windows) or Option+P (macOS) to switch models mid-prompt

---

## Checkpointing & Rewind

**What it is**: Automatic file state tracking with ability to rewind conversation and/or code changes to previous points

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/checkpointing

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

**Safety protocols**:
- Never update git config
- Never force push to main/master (warn if requested)
- Never skip hooks (--no-verify) unless explicitly requested
- Only amend commits if: (1) user explicitly requested OR (2) adding pre-commit edits
- Always check authorship before amending: `git log -1 --format='%an %ae'`
- Never commit unless explicitly asked

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

**Introduced**: v2.0.60 (2025-12)

**What we know**:
- Agents can now run in background while user continues working
- Agents and bash commands can run asynchronously and send messages to wake up the main agent
- Enables true parallel workflows with human and agent working simultaneously

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

**Introduced**: v2.0.64 (2025-12)

**What we know**:
- Use `/rename` to name current session
- Use `/resume <name>` in REPL to resume named session
- Use `claude --resume <name>` from terminal to resume
- Makes session management more intuitive than using session IDs

**Workflow examples**:
```bash
# In Claude Code session:
/rename feature-auth-refactor

# Later, resume from terminal:
claude --resume feature-auth-refactor

# Or resume from within Claude Code:
/resume feature-auth-refactor
```

**Benefits**:
- Human-readable session identifiers
- Easy switching between work contexts
- Better organization of related work
- No need to remember cryptic session IDs

---

## /stats Command

**What it is**: Command to view interesting Claude Code usage statistics including graphs and streaks

**Introduced**: v2.0.64 (2025-12)

**What we know**:
- New `/stats` command provides usage statistics
- Shows personal usage patterns and metrics
- May include visual graphs and streak tracking

**Expected metrics**:
- Favorite/most-used model
- Usage over time (graph)
- Usage streak (consecutive days)
- Possibly token counts, session counts, etc.
