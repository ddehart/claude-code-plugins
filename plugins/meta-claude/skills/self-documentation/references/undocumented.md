# Undocumented Features

Features mentioned in Claude Code release notes but not yet covered in official documentation. Information is based on release note descriptions and behavioral understanding. Details may be incomplete or subject to change.

**Latest Release**: v2.1.7 (as of 2026-01-13)

---

## Ctrl-G External Editor

**What it is**: Keyboard shortcut to edit prompts in system's configured text editor

**Introduced**: v2.0.10 (2024-12)

**What we know**:
- Press Ctrl-G to open current prompt in external editor
- Useful for composing long or complex prompts
- Likely uses $EDITOR or $VISUAL environment variables

**Expected workflow**:
1. Start typing prompt in Claude Code
2. Press Ctrl-G to open in editor
3. Compose/edit in full editor (Vim, VS Code, nano, etc.)
4. Save and close editor
5. Content returns to Claude Code prompt

---

## @-mention to Toggle MCP Servers

**What it is**: Enable or disable MCP servers by @-mentioning their names

**Introduced**: v2.0.10 (2024-12), refined in v2.0.14

**What we know**:
- @-mention an MCP server name to toggle its enabled/disabled state
- Alternative to using `/mcp` menu for quick server management
- Provides visual confirmation of new state

**Practical uses**:
- Quickly disable expensive MCP servers when not needed
- Enable specialized servers only for specific tasks
- Manage token usage by controlling active tools

---

## Real-time Thinking in Transcript Mode

**What it is**: Show thinking blocks in real-time when verbose output is enabled

**Introduced**: v2.1.0 (2026-01)

**What we know**:
- Ctrl+O verbose/transcript mode now shows thinking blocks as they stream
- Previously thinking blocks only appeared after completion
- Enables watching Claude's reasoning process in real-time
- Useful for understanding complex decision-making

---

## Claude in Chrome Improvements

**What it is**: Enhanced Chrome extension capabilities for browser control

**Introduced**: Multiple versions (v2.0.72+, ongoing improvements)

**What we know**:
- Chrome extension at https://claude.ai/chrome
- Enables browser automation: navigate, read content, interact with elements, take screenshots
- More powerful than WebFetch - active browser control vs. passive fetching
- Continuous improvements to capabilities and reliability

**Use cases**:
- Web application testing
- Form automation
- Content extraction
- UI verification

---

## VSCode Extension Updates

**What it is**: Ongoing improvements to the VS Code extension

**Introduced**: Various versions (v2.0.74+, ongoing)

**What we know**:
- Regular feature parity improvements with CLI
- Performance enhancements
- UI/UX refinements
- Bug fixes and stability improvements

**Recent improvements** (general pattern):
- Better integration with VS Code features
- Improved session management
- Enhanced diff viewing
- More responsive UI updates

---

## showTurnDuration Setting

**What it is**: Configuration option to hide turn duration messages

**Introduced**: v2.1.7 (2026-01)

**What we know**:
- Setting to control display of turn duration messages
- Likely configured in settings.json
- Helps reduce visual clutter for users who don't need timing info

**Expected configuration**:
```json
{
  "showTurnDuration": false
}
```

---

## Permission Prompt Feedback

**What it is**: Ability to provide feedback when accepting permission prompts

**Introduced**: v2.1.7 (2026-01)

**What we know**:
- Users can now provide feedback when accepting permission prompts
- Helps improve permission system based on user experience
- Likely integrated into permission dialog UI

**Use cases**:
- Report overly restrictive permissions
- Suggest better permission defaults
- Help Anthropic improve permission UX

---

## /config Search Functionality

**What it is**: Search capability within the /config command interface

**Introduced**: v2.1.6 (2026-01)

**What we know**:
- Added search to `/config` command
- Makes finding specific settings easier
- Likely keyword-based filtering of config options

**Expected behavior**:
- Type to search setting names or descriptions
- Filter visible config options dynamically
- Quick navigation to specific settings

---

## Nested .claude/skills Auto-discovery

**What it is**: Automatic skill discovery from nested subdirectories within .claude/skills

**Introduced**: v2.1.6 (2026-01)

**What we know**:
- Skills can now be organized in nested subdirectories
- Automatic discovery without requiring flat structure
- Enables better organization for projects with many skills

**Expected structure**:
```
.claude/
  skills/
    frontend/
      skill-a/
        SKILL.md
    backend/
      skill-b/
        SKILL.md
    testing/
      skill-c/
        SKILL.md
```

---

## Date Range Filtering in /stats

**What it is**: Ability to filter statistics by date range

**Introduced**: v2.1.6 (2026-01)

**What we know**:
- `/stats` command now supports date range filtering
- View usage statistics for specific time periods
- Helps track usage patterns over time

**Expected usage**:
```
/stats --from 2026-01-01 --to 2026-01-31
```
