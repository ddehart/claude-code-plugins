#!/usr/bin/env python3
"""
Export Claude Code session JSONL to UI-style readable text format.
Mimics the output of the /export command.

Requires Python 3.6+ (for f-strings and pathlib).
"""

import json
import os
import re
import sys
from pathlib import Path

# Get home directory dynamically
HOME_DIR = os.path.expanduser("~")


def generate_edit_diff(old_string, new_string, max_lines=15):
    """Generate a simple diff showing added/removed lines.

    Args:
        old_string: The original text being replaced
        new_string: The new text replacing it
        max_lines: Maximum lines to show in diff (truncate if larger, minimum 2)

    Returns:
        Tuple of (diff_lines, added_count, removed_count)
    """
    # Ensure max_lines is at least 2 to prevent division issues
    max_lines = max(max_lines, 2)

    old_lines = old_string.split('\n') if old_string else []
    new_lines = new_string.split('\n') if new_string else []

    added = len(new_lines)
    removed = len(old_lines)

    diff_lines = []

    # Show removed lines (limited)
    for line in old_lines[:max_lines // 2]:
        diff_lines.append(f"-{line}")

    if len(old_lines) > max_lines // 2:
        diff_lines.append(f"  ... ({len(old_lines) - max_lines // 2} more removed)")

    # Show added lines (limited)
    for line in new_lines[:max_lines // 2]:
        diff_lines.append(f"+{line}")

    if len(new_lines) > max_lines // 2:
        diff_lines.append(f"  ... ({len(new_lines) - max_lines // 2} more added)")

    return diff_lines, added, removed


def format_tool_params(params, tool_name=''):
    """Format tool parameters for display - match native format."""
    if not params:
        return ""

    # For Read operations - just show filename
    if tool_name == 'Read' and 'file_path' in params:
        file_path = params['file_path']
        # Extract just the filename for display (cross-platform)
        return Path(file_path).name

    # For simple single params, show just the value (no key)
    if len(params) == 1 and isinstance(list(params.values())[0], str):
        key, val = list(params.items())[0]
        if len(val) < 50:
            # For description params, show the value directly
            if key in ['description', 'file_path', 'pattern']:
                return val
            return f"{key}: {val}"

    # For complex params, format nicely
    formatted = []
    for key, val in params.items():
        if isinstance(val, str) and '\n' in val:
            formatted.append(f"{key}: |\n  " + val.replace('\n', '\n  '))
        elif isinstance(val, (dict, list)):
            formatted.append(f"{key}: {json.dumps(val, indent=2)}")
        else:
            formatted.append(f"{key}: {val}")
    return '\n      '.join(formatted)


def format_tool_result(content):
    """Format tool result content - keep it concise, match native format."""
    if isinstance(content, str):
        # Very long file contents - just show summary (no extra indent)
        if len(content) > 2000:
            lines = content.split('\n')
            # Count numbered lines (file content)
            numbered_lines = [l for l in lines if l.strip() and '→' in l[:10]]
            if numbered_lines:
                return f"  Read {len(numbered_lines)} lines"
            return f"  ({len(lines)} lines)"

        # Medium-length results - truncate
        if len(content) > 500:
            lines = content.split('\n')
            if len(lines) > 10:
                # Show first few lines with indent
                formatted_lines = ['  ' + line for line in lines[:5]]
                formatted_lines.append(f"    ... ({len(lines) - 5} more lines)")
                return '\n'.join(formatted_lines)
            return '  ' + content[:500] + "..."

        # Short results - indent them
        if '\n' in content:
            return '\n'.join('  ' + line for line in content.split('\n'))
        return '  ' + content
    elif isinstance(content, list):
        return '\n'.join(format_tool_result(c) for c in content)
    return str(content)


def extract_session_info(entries):
    """Extract session metadata from entries."""
    info = {
        'version': 'unknown',
        'model': None,
        'cwd': '~',
        'summary': None
    }

    # Count model occurrences to find the most common one
    model_counts = {}

    for entry in entries:
        if entry.get('type') == 'summary' and 'summary' in entry:
            info['summary'] = entry['summary']
        if 'version' in entry:
            info['version'] = entry['version']
        if 'cwd' in entry:
            # Show relative to home directory, matching native format
            cwd = entry['cwd']
            if cwd.startswith(HOME_DIR):
                info['cwd'] = '~' + cwd[len(HOME_DIR):]
            else:
                info['cwd'] = cwd
        if 'message' in entry and 'model' in entry['message']:
            model = entry['message']['model']
            # Only count actual Claude models, not internal references
            if model and model.startswith('claude-') and 'code' not in model:
                model_counts[model] = model_counts.get(model, 0) + 1

    # Pick the most common model
    if model_counts:
        info['model'] = max(model_counts, key=model_counts.get)

    return info


def parse_model_display_name(model_id):
    """Parse model ID to friendly display name.

    Examples:
        claude-opus-4-5-20251101 -> Opus 4.5
        claude-sonnet-4-5-20250929 -> Sonnet 4.5
        claude-3-5-sonnet-20241022 -> Sonnet 3.5
    """
    if not model_id:
        return "Claude"

    model_id = model_id.lower()

    # Extract model family and version
    if 'opus' in model_id:
        family = 'Opus'
    elif 'sonnet' in model_id:
        family = 'Sonnet'
    elif 'haiku' in model_id:
        family = 'Haiku'
    else:
        return "Claude"

    # Extract version number (e.g., "4-5" -> "4.5", "3-5" -> "3.5")
    version_match = re.search(r'(\d+)-(\d+)', model_id)
    if version_match:
        version = f"{version_match.group(1)}.{version_match.group(2)}"
        return f"{family} {version}"

    return family


def format_header(info):
    """Format session header - match native format exactly."""
    model_display = parse_model_display_name(info.get('model', ''))

    lines = []
    lines.append("")  # Leading blank line
    lines.append(" * ▐▛███▜▌ *   Claude Code v" + info['version'])  # Leading space
    lines.append(f"* ▝▜█████▛▘ *  {model_display} · Claude API")
    lines.append(" *  ▘▘ ▝▝  *   " + info['cwd'])
    lines.append("")
    return '\n'.join(lines)


def format_user_message(entry):
    """Format a user message."""
    msg = entry.get('message', {})
    content = msg.get('content', '')

    # Skip meta messages (like context dumps, command outputs)
    if entry.get('isMeta'):
        return None

    # Skip command tags whether meta or not
    if isinstance(content, str):
        if any(tag in content for tag in ['<command-name>', '<local-command-stdout>', '<command-args>', '<command-message>']):
            return None

    # Skip tool results - they're handled separately
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'tool_result':
                return None

    # Skip content that's just raw tool result JSON
    if isinstance(content, str) and content.startswith("[{'tool_use_id'"):
        return None

    # Format regular user message (no ⎿ marker per native format)
    return f"> {content}"


def format_assistant_message(entry):
    """Format an assistant message with tool uses."""
    msg = entry.get('message', {})
    content = msg.get('content', [])

    if isinstance(content, str):
        content = [{'type': 'text', 'text': content}]

    lines = []

    for block in content:
        if not isinstance(block, dict):
            continue

        block_type = block.get('type', '')

        if block_type == 'text':
            text = block.get('text', '').strip()
            if text:
                lines.append(f"⏺ {text}")
                lines.append("")

        elif block_type == 'thinking':
            # Skip thinking blocks in the UI-style output
            continue

        elif block_type == 'tool_use':
            tool_name = block.get('name', 'Unknown')
            tool_input = block.get('input', {})

            # Format tool name (capitalize, handle special cases)
            display_name = tool_name.replace('_', ' ').title()
            if tool_name == 'Read':
                display_name = 'Read'
            elif tool_name == 'Write':
                display_name = 'Write'
            elif tool_name == 'Edit':
                display_name = 'Edit'
            elif tool_name == 'Bash':
                display_name = 'Bash'
            elif tool_name == 'Task':
                display_name = block.get('input', {}).get('description', 'Task')

            # Format parameters - keep concise for verbose tools
            if tool_name == 'Edit':
                # For edits, show file and diff summary
                file_path = tool_input.get('file_path', '')
                filename = Path(file_path).name if file_path else 'file'
                old_string = tool_input.get('old_string', '')
                new_string = tool_input.get('new_string', '')

                diff_lines, added, removed = generate_edit_diff(old_string, new_string)

                lines.append(f"⏺ Update({filename})")
                lines.append(f"  ⎿  Added {added} lines, removed {removed} lines")

                # Show diff preview (indented)
                for diff_line in diff_lines[:10]:  # Limit to 10 lines
                    lines.append(f"     {diff_line}")
                if len(diff_lines) > 10:
                    lines.append(f"     ... ({len(diff_lines) - 10} more diff lines)")
            elif tool_name == 'Write':
                # For writes, just show the file
                file_path = tool_input.get('file_path', '')
                content_lines = tool_input.get('content', '').count('\n') + 1
                filename = Path(file_path).name if file_path else 'file'
                lines.append(f"⏺ Write({filename} - {content_lines} lines)")
                lines.append("  ⎿  ")
            elif tool_name == 'Bash':
                # For Bash, show raw command (no description label)
                command = tool_input.get('command', '')
                if command:
                    # Show command directly without labels
                    lines.append(f"⏺ Bash({command})")
                else:
                    lines.append(f"⏺ Bash")
                lines.append("  ⎿  ")
            else:
                # For other tools, format normally
                params = format_tool_params(tool_input, tool_name)
                if params and '\n' in params:
                    lines.append(f"⏺ {display_name}({params})")
                elif params:
                    lines.append(f"⏺ {display_name}({params})")
                else:
                    lines.append(f"⏺ {display_name}")
                lines.append("  ⎿  ")

    return '\n'.join(lines) if lines else None


def format_tool_result_entry(entry):
    """Format tool result from a user entry - match native format (no blank line after ⎿)."""
    msg = entry.get('message', {})
    content = msg.get('content', [])

    if isinstance(content, str):
        # Try to parse if it looks like a list
        if content.startswith("[{"):
            return None
        content = [{'type': 'text', 'text': content}]

    lines = []

    for block in content:
        if not isinstance(block, dict):
            continue

        if block.get('type') == 'tool_result':
            # Skip interrupted requests (noise in export)
            if block.get('is_error'):
                content_str = str(block.get('content', ''))
                if 'Request interrupted' in content_str:
                    continue

            result_content = block.get('content', '')

            # Handle agent results specially
            if isinstance(result_content, list):
                for item in result_content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text = item.get('text', '')
                        if text and not text.startswith('agentId:'):
                            # Clean formatting for agent results
                            for line in text.split('\n'):
                                if line.strip():
                                    lines.append(line)
            # Handle string results
            elif isinstance(result_content, str):
                formatted = format_tool_result(result_content)
                if formatted:
                    # Add result lines directly (no extra indent per native format)
                    lines.append(formatted)

    return '\n'.join(lines) if lines else None


def export_session(jsonl_path, output_path):
    """Export JSONL session to UI-style readable text format."""

    # Read and parse JSONL file with error handling
    try:
        with open(jsonl_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"✗ Error: Session file not found: {jsonl_path}")
        sys.exit(1)
    except PermissionError:
        print(f"✗ Error: Permission denied reading: {jsonl_path}")
        sys.exit(1)

    # Parse JSON lines with error handling
    entries = []
    for i, line in enumerate(lines):
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON on line {i + 1}: {e}")
            sys.exit(1)

    # Extract session info
    info = extract_session_info(entries)

    # Start output with header
    output_lines = []
    output_lines.append(format_header(info))

    # Process entries in order
    for i, entry in enumerate(entries):
        entry_type = entry.get('type', '')

        # Handle compaction boundary - add visual separator
        if entry_type == 'system' and entry.get('subtype') == 'compact_boundary':
            output_lines.append("═" * 80)
            output_lines.append(" Conversation compacted · ctrl+o for history ")
            output_lines.append("═" * 80)
            output_lines.append("")
            continue

        if entry_type == 'user':
            formatted = format_user_message(entry)
            if formatted:
                output_lines.append(formatted)
                # Add blank line after user message (matches native format)
                output_lines.append("")

        elif entry_type == 'assistant':
            formatted = format_assistant_message(entry)
            if formatted:
                output_lines.append(formatted)

        # Check next entry for tool results
        if i + 1 < len(entries) and entries[i + 1].get('type') == 'user':
            next_msg = entries[i + 1].get('message', {})
            if isinstance(next_msg.get('content'), list):
                for block in next_msg['content']:
                    if isinstance(block, dict) and block.get('type') == 'tool_result':
                        formatted = format_tool_result_entry(entries[i + 1])
                        if formatted:
                            output_lines.append(formatted)
                            # Add blank line after tool result block (matches native format)
                            output_lines.append("")
                        break

    # Write to file with error handling
    output_path = Path(output_path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write('\n'.join(output_lines))
    except PermissionError:
        print(f"✗ Error: Permission denied writing to: {output_path}")
        sys.exit(1)
    except OSError as e:
        print(f"✗ Error: Failed to write file: {e}")
        sys.exit(1)

    print(f"✓ Exported session to: {output_path}")
    if info['summary']:
        print(f"  Summary: {info['summary']}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python export-session.py <session-file.jsonl> [output.txt]")
        print("\nExample:")
        print("  python export-session.py ~/.claude/projects/.../session-id.jsonl output.txt")
        sys.exit(1)

    jsonl_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'session-transcript.txt'

    export_session(jsonl_path, output_path)
