---
name: session-export
description: Export Claude Code session transcripts from JSONL logs to readable text format. Use when the user asks to export a session, save a transcript, create session archives, or convert session logs to readable format. Triggers on phrases like "export session", "save transcript", "session to text".
allowed-tools: ["Read", "Write", "Bash", "Glob"]
---

# Session Export Skill

Export Claude Code session JSONL logs to readable, UI-style text format matching the native `/export` command output.

## Capabilities

- Export session transcripts from `~/.claude/projects/<project>/<session-id>.jsonl`
- Generate formatted output matching Claude Code's native export style
- Support browsing recent sessions or exporting specific session IDs
- Create timestamped exports with flexible output location

## Workflow

### 1. Identify the Session

When the user asks to export a session, determine which session to export:

**If user provides a session ID:**
- Look for the JSONL file at `~/.claude/projects/<project-path>/<session-id>.jsonl`

**If user wants to browse recent sessions:**
- List recent sessions from `~/.claude/projects/` for the current project
- Show session timestamps and let user choose

**To find sessions for the current project:**
```bash
ls -lt ~/.claude/projects/$(pwd | sed 's|/|%|g')/*.jsonl | head -10
```

### 2. Determine Output Location

**Check project context first:**
- Look for existing session/transcript directories (e.g., `sessions/`, `transcripts/`, `chronicles/`, `docs/sessions/`)
- Check CLAUDE.md or project documentation for session export conventions
- If a pattern exists, follow it

**If no project convention exists, ask the user:**
- Suggest a sensible default like `./sessions/YYYY-MM-DDThhmm-<description>.txt`
- Let user specify their preferred location
- Remember their preference for future exports in this session

**Output filename format:** `YYYY-MM-DDThhmm-<description>.txt`
- Date/time from the session or current timestamp
- Description from session summary or user-provided label

### 3. Run the Export Script

The export script is located at:
`<plugin-dir>/skills/session-export/scripts/export-session.py`

```bash
python3 <plugin-dir>/skills/session-export/scripts/export-session.py <session-file.jsonl> <output-path.txt>
```

### 4. Report Results

After export, report:
- Output file path and size
- Session summary if available
- Number of messages/turns exported

## Export Format

The export produces UI-style readable text with:
- Claude ASCII art header with version and project path
- User messages prefixed with `>`
- Assistant messages with `⏺` bullets
- Tool uses formatted with `⎿` markers
- Concise output (truncates long file contents)
- Filtered meta messages and command tags

## Examples

**Export current/recent session:**
> "Export this session"
> "Save the transcript"

**Export specific session:**
> "Export session abc123"
> "Export the session from yesterday"

**Browse and choose:**
> "Show me recent sessions to export"
> "List sessions from this project"

## Error Handling

- If session file not found, list available sessions
- If output directory doesn't exist, create it
- If Python script fails, show error and suggest manual export
