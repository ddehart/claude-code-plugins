# Undocumented Features

Features mentioned in Claude Code release notes but not yet covered in official documentation. Information is based on release note descriptions and observed behavior. Details may be incomplete or subject to change.

**Latest Release**: v2.1.20

---

## Real-time Thinking in Transcript Mode

**What it is**: Show thinking blocks in real-time when verbose output is enabled

**Introduced**: v2.1.0

**What we know**:
- Ctrl+O verbose/transcript mode now shows thinking blocks as they stream
- Previously thinking blocks only appeared after completion
- Enables watching Claude's reasoning process in real-time
- Useful for understanding complex decision-making

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

## Copy OAuth URL Keyboard Shortcut

**What it is**: Keyboard shortcut 'c' to copy OAuth URL when browser doesn't open during login

**Introduced**: v2.1.10

**What we know**:
- Press 'c' to copy OAuth URL to clipboard during login
- Useful when browser auto-open fails
- Improves login experience in restricted environments

**Expected workflow**:
1. Start login process
2. Browser fails to open automatically
3. Press 'c' to copy URL to clipboard
4. Paste URL manually in browser

---

## Install Count Display in VSCode Plugin Listings

**What it is**: Display of installation counts for plugins in VS Code extension

**Introduced**: v2.1.10

**What we know**:
- Plugin listings in VSCode extension now show install counts
- Helps users assess plugin popularity and community adoption
- Provides social proof for plugin discovery

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

## Plugin Pinning to Git Commit SHAs

**What it is**: Support for pinning plugins to specific git commit SHAs for exact version control

**Introduced**: v2.1.14

**What we know**:
- Marketplace entries can specify exact commit SHAs
- Enables reproducible builds and dependency locking
- Useful for enterprise environments requiring audit trails
- Allows teams to control exact plugin versions across installs

**Expected configuration**:
- Marketplace entry includes commit SHA in source specification
- Plugin installation uses exact commit rather than branch head
- Updates require explicit SHA changes in marketplace definition

---

## PR Review Status Indicator

**What it is**: Display of pull request review status in the prompt footer showing branch PR state

**Introduced**: v2.1.20

**What we know**:
- Prompt footer now shows PR review status indicator
- Shows the state of any PR associated with current branch
- Provides quick visibility into review progress without leaving CLI

**Expected behavior**:
- Footer displays when working on a branch with an open PR
- Shows review state (pending, approved, changes requested, etc.)
- Updates as PR status changes

---

## Agents Process User Messages While Working

**What it is**: Background agents can now receive and process user messages while actively working

**Introduced**: v2.1.20

**What we know**:
- Agents can now process user messages while actively working on tasks
- Enables more interactive workflows with background agents
- Users can provide additional context or corrections mid-task

**Use cases**:
- Provide clarifications without waiting for agent to finish
- Redirect agent's approach during execution
- Add additional requirements discovered during processing

---

## Background Agent Pre-launch Permission Prompts

**What it is**: Background agents now prompt for tool permissions before launching

**Introduced**: v2.1.20

**What we know**:
- Background agents prompt for tool permissions before launching rather than during execution
- Improves UX by handling permissions upfront
- Reduces mid-execution permission failures

**Benefits**:
- Fewer interrupted background tasks
- Better visibility into what tools background agent will use
- More predictable background agent behavior

---

## Wildcard Permission Rule Simplification

**What it is**: Permission rules like `Bash(*)` are now treated equivalently to `Bash`

**Introduced**: v2.1.20

**What we know**:
- Permission rules with `(*)` wildcard are simplified
- `Bash(*)` is treated the same as just `Bash`
- Reduces confusion around wildcard patterns

---

## Config Backup Rotation

**What it is**: Configuration backups are now timestamped and rotated, keeping the 5 most recent

**Introduced**: v2.1.20

**What we know**:
- Config changes now create timestamped backup files
- Only the 5 most recent backups are retained
- Automatic rotation prevents backup file accumulation

**Benefits**:
- Recovery from recent config mistakes
- No manual cleanup required
- Predictable disk usage for config backups

