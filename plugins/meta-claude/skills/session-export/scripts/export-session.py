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

# Credential patterns scrubbed from everything the exporter writes. Exports are
# meant to be committed, and a session that inspects its environment (env,
# /proc/<pid>/environ, cat .secrets, curl -v) prints live credentials into the
# JSONL. Keyed secrets keep their name and quotes so the transcript still reads
# sensibly; only the value becomes [REDACTED].
REDACTED = '[REDACTED]'

# A key that names a secret: anything ending in api_key / access_key /
# secret_key / private_key / token / secret / password / credentials
# (case-insensitive, `_` or `-` separators), or an upper-case env var ending
# in _KEY (OPENAI_KEY). `max_tokens` and `input_tokens` don't match: the name
# has to end at the separator.
_SECRET_NAME = (
    r'(?:(?i:[\w-]*?(?:(?:api|access|secret|private)[_-]?key'
    r'|token|secret|password|passwd|credentials?))'
    r'|[A-Z][A-Z0-9_]*_KEY)'
)
# A quoted value (spaces allowed, JSON-escaped quotes allowed), or a bare run
# that stops at whitespace, quotes, backticks, and the punctuation that
# usually closes the surrounding structure.
_QUOTED_VALUE = r'\\?"[^"\n]*?\\?"|\\?\'[^\'\n]*?\\?\''
_BARE_VALUE = r'[^\s"\'`,;)}\]&]+'
# An auth scheme before the value is kept, so `token: Bearer eyJ...` redacts
# the credential rather than the word "Bearer".
_AUTH_SCHEME = r'(?i:(?:bearer|basic)[ \t]+)?'
_SECRET_VALUE = rf'{_AUTH_SCHEME}(?P<value>{_QUOTED_VALUE}|{_BARE_VALUE})'
_COLON = r'[ \t]*:[ \t]*'
# An unquoted value that reads as a credential rather than code: 16+ chars of
# token alphabet, at least one digit, then the end of the value: whitespace,
# `,`, `;`, a closing quote, backtick, or paren, or the end of the text.
# `token = get_token()` and `password = self.config.password` don't qualify.
_OPAQUE_TOKEN = r'[A-Za-z0-9+/_.~-]'  # base64, base64url, JWT
_CREDENTIAL_LIKE = rf'(?={_OPAQUE_TOKEN}*\d){_OPAQUE_TOKEN}{{16,}}=*(?:[\s,;"\'`)]|$)'
_VALUE_QUOTES = re.compile(r'((?:\\?["\'])?)(.*?)((?:\\?["\'])?)')
# References and placeholders, not secrets: $VAR, ${VAR}, $(cmd), %s, {name}
# (f-strings and templates), <name>, and elisions.
_PLACEHOLDER = re.compile(r'\$(?:\{?\w+\}?|\(.*)|%s|\{\w*\}?|<[\w -]*>|\.\.\.|…')

_KEYED_PATTERNS = [
    # NAME=value; NAME = "value"; and NAME = value (INI, WireGuard's
    # `PrivateKey = ...`) when the value looks like a credential.
    # (?<![\w-]) rather than \b: one match attempt per word run, not one per
    # hyphen in it, which made long kebab-case or base64url runs quadratic.
    rf'(?<![\w-])(?P<name>{_SECRET_NAME})'
    rf'(?:[ \t]*=[ \t]*(?=\\?["\']|{_CREDENTIAL_LIKE})|=){_SECRET_VALUE}',
    # "name": value (JSON, Python dicts)
    rf'(?P<q>\\?["\'])(?P<name>{_SECRET_NAME})(?P=q){_COLON}{_SECRET_VALUE}',
    # name: value at line start (YAML, curl -v request and response headers);
    # not mid-sentence, where "token: " is usually prose
    rf'(?m)^[ \t<>*-]*(?P<name>{_SECRET_NAME}){_COLON}{_SECRET_VALUE}',
    # name: value just inside a quote (-H "x-api-key: ..."). Bare values only,
    # so a label like print('nextPageToken:', body) isn't read as a header.
    rf'(?<=["\'])(?P<name>{_SECRET_NAME}){_COLON}{_AUTH_SCHEME}(?P<value>{_BARE_VALUE})',
]

# Credentials recognizable by shape alone, wherever they appear. The
# knowledge-commons plugin's scripts/scan-secrets.sh detects (rather than
# rewrites) an overlapping set; keep the two in mind together.
_BARE_TOKEN_PATTERNS = [
    r'sk-ant-[A-Za-z0-9_-]+',                       # Anthropic API keys and OAuth tokens
    r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}',  # OpenAI
    r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}',  # GitHub tokens
    r'\bgithub_pat_[A-Za-z0-9_]{20,}',              # GitHub fine-grained PATs
    r'\bxox[abposr]-[A-Za-z0-9-]{10,}',             # Slack
    r'\bya29\.[A-Za-z0-9._-]{20,}',                 # Google OAuth access tokens
    r'\b1//0[A-Za-z0-9_-]{20,}',                    # Google OAuth refresh tokens
    r'\bAIza[0-9A-Za-z_-]{35}',                     # Google API keys
    r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',               # AWS access key IDs
    r'(?:(?<=bot)|\b)\d{8,10}:[A-Za-z0-9_-]{35}\b',  # Telegram bot tokens, incl. /bot<token>/ URLs
]


def _redact_value(match):
    """Replace a secret value, keeping its name, separator, and quotes."""
    opening, inner, closing = _VALUE_QUOTES.fullmatch(match.group('value')).groups()
    # Skip references and placeholders, values an earlier pass already redacted
    # (a bare value stops at `]`, so it reads `[REDACTED`), and the lone
    # `-----BEGIN` word the key-block pass leaves in `KEY=-----BEGIN ...`
    # (_redact_pem keeps that line, so the coupling is to its output shape).
    if (not inner or '[REDACTED' in inner or inner == '-----BEGIN'
            or _PLACEHOLDER.fullmatch(inner)):
        return match.group(0)
    return match.string[match.start():match.start('value')] + opening + REDACTED + closing


# A private key block (PEM, OpenSSH, PGP): the BEGIN line, then body lines of
# base64 or armor headers (Proc-Type:, Version:), with a blank line allowed
# only where more base64 follows. Lines break on real newlines (plus the
# exporter's indent), on JSON-escaped `\n`, or on a single space when the key
# was flattened onto one line (env displays) and key data follows. The END
# line is optional: the exporter cuts long tool results off after a few lines.
_PEM_NEWLINE = r'(?:(?:\\n|\r?\n)[ \t]*|[ ](?=[A-Za-z0-9+/=]{16}|-----END))'
_PEM_LABEL = r'[A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----'
# A base64 line has to run to the end of the line, or `Version: ...` would
# match as the base64 line `Version` and end the block early. The end can
# also be the exporter's truncation mark (`...`) or a closing JSON quote.
_PEM_LINE = (
    rf'(?:[A-Za-z0-9+/=]+(?=\\|\r?\n|$|\.\.\.|…|"| )'
    rf'|[A-Z][\w-]*: [^\n\\]*|(?={_PEM_NEWLINE}[A-Za-z0-9+/=]))'
)
_PEM_BLOCK = re.compile(
    rf'(?P<begin>-----BEGIN {_PEM_LABEL})'
    rf'(?:(?P<sep>{_PEM_NEWLINE}){_PEM_LINE})*'
    rf'(?:{_PEM_NEWLINE}(?P<end>-----END {_PEM_LABEL}))?'
)


def _redact_pem(match):
    """Keep a key block's BEGIN and END lines; replace the body.

    _redact_value skips the `-----BEGIN` this leaves behind; keep the two in step.
    """
    if match.group('sep') is None:  # just the armor line, e.g. a grep pattern
        return match.group(0)
    sep = match.group('sep')
    sep = '\\n' if sep.startswith('\\') else ' ' if sep == ' ' else '\n'
    end = sep + match.group('end') if match.group('end') else ''
    return match.group('begin') + sep + REDACTED + end


# The password in scheme://user:password@host (postgres://, https://, and
# redis://:password@host, where the user is often empty). The password runs to
# the last `@` before the host, so raw `/` and `@` inside it (generated
# passwords, which clients like libpq accept) are covered.
# host:8080/path@x is a port and a path, not a password. scp-style
# git@host:path has no `://`, so it never matches.
# Two guards keep this linear: the scheme anchors on (?<![A-Za-z0-9+.-])
# rather than \b (one attempt per dotted or hyphenated run), and the password
# is capped at 1,024 characters, so a long run of `x://` starts can't each scan
# to the end of the run. A longer password goes unredacted (see SKILL.md).
_URL_CREDENTIAL = re.compile(
    r'(?<![A-Za-z0-9+.-])[A-Za-z][A-Za-z0-9+.-]*://[^\s/:@"\']*:'
    r'(?P<value>(?!\d{1,5}/)[^\s"\'`]{1,1024})(?=@[^\s@/?#"\'`]+(?:[/?#\s"\'`]|$))'
)


# Access tokens in URL query strings: capability links (a calendar export
# whose URL alone grants access), pre-signed S3 and GCS links, OAuth codes.
# A parameter starts after `?`, `&`, `;` (so `&amp;` in HTML/XML counts), or
# JSON's `&`. Its value runs to the first character outside the rule's
# alphabet, so a token followed by `,`, `|`, `]`, or an escaped `\n` is still
# caught. Every rule needs a digit in the value.
def _query_token(names, chars, min_len, guard=''):
    return re.compile(
        rf'(?:(?<=[?&;])|(?<=\\u0026)){names}='
        rf'(?P<value>{guard}(?={chars}*\d){chars}{{{min_len},}})(?!{chars})'
    )


_QUERY_TOKEN_PATTERNS = [
    # Signature-style names: 16+ characters of base64, raw (`+`, `/`) or
    # %-encoded.
    _query_token(r'(?i:sig|signature|code|key|x-amz-signature|x-amz-security-token|x-goog-signature)',
                 r'[A-Za-z0-9_.~%/=+-]', 16),
    # `s` is a signature on some links and a search box on others, so no `+`:
    # `?s=how+to+configure+nginx` isn't read as a token.
    _query_token(r'(?i:s)', r'[A-Za-z0-9_.~%/=-]', 16),
    # Any name, when the value is long and random-looking: 32+ token characters
    # with a letter. No `%` or `/`, so encoded URLs, searches, and paths stay
    # readable. UUIDs and 40-hex git SHAs (`?ref=<sha>`) are left alone; other
    # long hashes, like a `?v=<hash>` cache-buster, are redacted too (SKILL.md).
    _query_token(r'[\w.-]+', r'[A-Za-z0-9_.~=-]', 32, guard=(
        r'(?![0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}(?![\w.~=-]))'
        r'(?![0-9a-f]{40}(?![\w.~=-]))(?=[A-Za-z0-9_.~=-]*[A-Za-z])'
    )),
]


# Order matters, in three tiers. Structural passes (key blocks, URL passwords,
# URL query tokens) run first, so a keyed pattern can't redact `-----BEGIN` out
# from under a key body. Keyed patterns run next, so `GITHUB_TOKEN=ghp_...`
# keeps its name. Shape-only patterns run last. A later pass leaves alone what
# an earlier one already redacted (see _redact_value).
REDACTION_PATTERNS = (
    [(_PEM_BLOCK, _redact_pem), (_URL_CREDENTIAL, _redact_value)]
    + [(p, _redact_value) for p in _QUERY_TOKEN_PATTERNS]
    + [(re.compile(p), _redact_value) for p in _KEYED_PATTERNS]
    + [(re.compile(rf'(?i)\b((?:bearer|basic)[ \t]+){_OPAQUE_TOKEN}{{16,}}=*'), r'\1' + REDACTED)]
    + [(re.compile(p), REDACTED) for p in _BARE_TOKEN_PATTERNS]
)


def redact(text):
    """Replace credential-shaped substrings with [REDACTED]."""
    for pattern, replacement in REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


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
            f.write(redact('\n'.join(output_lines)))
    except PermissionError:
        print(f"✗ Error: Permission denied writing to: {output_path}")
        sys.exit(1)
    except OSError as e:
        print(f"✗ Error: Failed to write file: {e}")
        sys.exit(1)

    print(f"✓ Exported session to: {output_path}")
    if info['summary']:
        print(f"  Summary: {redact(info['summary'])}")
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
