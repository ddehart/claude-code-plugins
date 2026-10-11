#!/usr/bin/env python3
"""
Tests for export-session.py credential redaction.

Run from this directory:
    python3 -m unittest test_export_session.py
"""

import importlib.util
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPT = Path(__file__).with_name('export-session.py')
spec = importlib.util.spec_from_file_location('export_session', SCRIPT)
export_session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_session)

# Fake tokens, assembled at runtime so no literal credential-shaped string is
# committed (secret scanners would flag it).
PREFIX = 'sk-' + 'ant-'
FAKE_OAT = PREFIX + 'oat01-' + 'AbCdEfGhIjKlMnOpQrStUvWxYz0123456789_-'
FAKE_API = PREFIX + 'api03-' + 'ZyXwVuTsRqPoNmLkJiHgFeDcBa9876543210'

# Fixture: a tool_use / tool_result pair shaped like a session that inspected
# /proc/<pid>/environ and printed truncated CLAUDE_CODE_OAUTH_TOKEN values.
FIXTURE_LINES = [
    {
        'type': 'assistant',
        'message': {'content': [{
            'type': 'tool_use', 'id': 'toolu_1', 'name': 'Bash',
            'input': {'command': "tr '\\0' '\\n' < /proc/4242/environ | grep -E 'TOKEN|KEY'"},
        }]},
    },
    {
        'type': 'user',
        'message': {'content': [{
            'type': 'tool_result', 'tool_use_id': 'toolu_1',
            'content': (
                f'CLAUDE_CODE_OAUTH_TOKEN={FAKE_OAT[:45]}\n'
                f'GITHUB_TOKEN=ghp_notarealtoken123\n'
                f'AGENTMAIL_API_KEY=am_notarealkey456'
            ),
        }]},
    },
    {
        'type': 'assistant',
        'message': {'content': [{
            'type': 'text',
            'text': f'The worker had {FAKE_OAT[:40]} while the shell had {FAKE_API}.',
        }]},
    },
]


class RedactTest(unittest.TestCase):
    def test_anthropic_token_anywhere(self):
        self.assertEqual(export_session.redact(f'key is {FAKE_API} ok'), 'key is [REDACTED] ok')

    def test_oauth_token_assignment_keeps_name(self):
        self.assertEqual(
            export_session.redact(f'CLAUDE_CODE_OAUTH_TOKEN={FAKE_OAT}'),
            'CLAUDE_CODE_OAUTH_TOKEN=[REDACTED]',
        )

    def test_generic_assignments_case_insensitive(self):
        cases = {
            'api_key=abc123': 'api_key=[REDACTED]',
            'API-KEY=abc123': 'API-KEY=[REDACTED]',
            'apikey=abc123': 'apikey=[REDACTED]',
            'Token=abc123': 'Token=[REDACTED]',
            'CLIENT_SECRET=abc123': 'CLIENT_SECRET=[REDACTED]',
            'export TG_BOT_TOKEN=123:abc rest': 'export TG_BOT_TOKEN=[REDACTED] rest',
        }
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(export_session.redact(raw), want)

    def test_leaves_ordinary_text_alone(self):
        for text in ['max_tokens=4096', 'token budget is fine', 'secret sauce', 'sk-learn']:
            with self.subTest(text=text):
                self.assertEqual(export_session.redact(text), text)


class ExportRedactionTest(unittest.TestCase):
    def test_export_writes_no_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'session.jsonl'
            out = Path(tmp) / 'out.txt'
            src.write_text('\n'.join(json.dumps(line) for line in FIXTURE_LINES) + '\n')

            with redirect_stdout(StringIO()):
                export_session.export_session(str(src), str(out))
            text = out.read_text()

        self.assertNotIn(PREFIX, text)
        self.assertNotIn('ghp_notarealtoken123', text)
        self.assertNotIn('am_notarealkey456', text)
        self.assertIn('CLAUDE_CODE_OAUTH_TOKEN=[REDACTED]', text)
        self.assertIn('GITHUB_TOKEN=[REDACTED]', text)
        self.assertIn('AGENTMAIL_API_KEY=[REDACTED]', text)
        # The command itself survives; only values are scrubbed.
        self.assertIn('/proc/4242/environ', text)


if __name__ == '__main__':
    unittest.main()
