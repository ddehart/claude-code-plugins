#!/usr/bin/env python3
"""
Tests for export-session.py credential redaction.

Run from this directory:
    python3 -m unittest test_export_session.py
"""

import importlib.util
import json
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPT = Path(__file__).with_name('export-session.py')
spec = importlib.util.spec_from_file_location('export_session', SCRIPT)
export_session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_session)
redact = export_session.redact

# Fake credentials, assembled at runtime so no literal credential-shaped string
# is committed (secret scanners would flag it).
ALNUM = 'AbCdEfGhIjKlMnOpQrStUvWxYz0123456789'
PREFIX = 'sk-' + 'ant-'
FAKE_OAT = PREFIX + 'oat01-' + ALNUM + '_-'
FAKE_API = PREFIX + 'api03-' + ALNUM[::-1]
FAKE_OPENAI = 'sk-' + 'proj-' + ALNUM
FAKE_GHP = 'gh' + 'p_' + ALNUM
FAKE_REFRESH = '1/' + '/0g' + ALNUM
FAKE_TELEGRAM = '1234567890' + ':' + ('AAH' + ALNUM)[:35]

BARE_TOKENS = {
    'anthropic api key': FAKE_API,
    'anthropic oauth token': FAKE_OAT,
    'openai': FAKE_OPENAI,
    'github': FAKE_GHP,
    'github fine-grained pat': 'github' + '_pat_' + ALNUM,
    'slack': 'xo' + 'xb-' + '1234567890-' + ALNUM,
    'google access token': 'ya' + '29.' + ALNUM,
    'google refresh token': FAKE_REFRESH,
    'google api key': 'AI' + 'za' + ALNUM[:35],
    'aws access key id': 'AK' + 'IA' + 'ABCDEFGHIJ234567',
    'telegram bot token': FAKE_TELEGRAM,
}

# Fixture: one entry per export path that can carry a credential — the
# summary, a user message, an Edit diff, a Bash command, a short tool result
# (written verbatim), a medium one (cut at 500 characters), and assistant text.
# The Bash pair is shaped like the incident: a session that read
# /proc/<pid>/environ and printed truncated CLAUDE_CODE_OAUTH_TOKEN values.
FIXTURE_LINES = [
    {'type': 'summary', 'summary': f'Debugging auth with {FAKE_OAT}'},
    {
        'type': 'user',
        'message': {'content': f'Here is the key to test with: {FAKE_API}'},
    },
    {
        'type': 'assistant',
        'message': {'content': [{
            'type': 'tool_use', 'id': 'toolu_0', 'name': 'Edit',
            'input': {
                'file_path': '/home/u/.env',
                'old_string': 'OPENAI_KEY=old',
                'new_string': f'OPENAI_KEY={FAKE_OPENAI}',
            },
        }]},
    },
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
                f'GITHUB_TOKEN={FAKE_GHP}\n'
                f'AGENTMAIL_API_KEY=am_notarealkey456'
            ),
        }]},
    },
    {
        'type': 'assistant',
        'message': {'content': [{
            'type': 'tool_use', 'id': 'toolu_2', 'name': 'Bash',
            'input': {'command': 'cat ~/.config/gws/credentials.json'},
        }]},
    },
    {
        'type': 'user',
        'message': {'content': [{
            'type': 'tool_result', 'tool_use_id': 'toolu_2',
            'content': json.dumps({
                'refresh_token': FAKE_REFRESH,
                'client_secret': 'GOCSPX-notarealsecret',
                'padding': 'x' * 600,
            }),
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

SECRET_VALUES = [
    FAKE_OAT[:40], FAKE_API, FAKE_OPENAI, FAKE_GHP, FAKE_REFRESH,
    'am_notarealkey456', 'GOCSPX-notarealsecret',
]


class RedactAssertions(unittest.TestCase):
    def assertRedacts(self, cases):
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(redact(raw), want)

    def assertUnchanged(self, texts):
        self.assertRedacts({text: text for text in texts})


class BareTokenTest(RedactAssertions):
    def test_each_format_redacted_in_prose(self):
        self.assertRedacts({f'got {token} back': 'got [REDACTED] back' for token in BARE_TOKENS.values()})

    def test_telegram_token_in_bot_url(self):
        self.assertEqual(
            redact(f'curl https://api.telegram.org/bot{FAKE_TELEGRAM}/getMe'),
            'curl https://api.telegram.org/bot[REDACTED]/getMe',
        )

    def test_bearer_header(self):
        self.assertRedacts({
            '-H "Authorization: Bearer abcdef0123456789abcdef"': '-H "Authorization: Bearer [REDACTED]"',
            # A keyed value that carries an auth scheme: the credential goes, not the word Bearer
            'access_token: Bearer eyJhbGciOi.eyJzdWIiOi.c2lnbmF0dXJl': 'access_token: Bearer [REDACTED]',
            '-H "x-api-key: Bearer abc123def456"': '-H "x-api-key: Bearer [REDACTED]"',
        })


class KeyedSecretTest(RedactAssertions):
    def test_assignments_keep_name(self):
        cases = {
            f'CLAUDE_CODE_OAUTH_TOKEN={FAKE_OAT}': 'CLAUDE_CODE_OAUTH_TOKEN=[REDACTED]',
            'api_key=abc123': 'api_key=[REDACTED]',
            'API-KEY=abc123': 'API-KEY=[REDACTED]',
            'apikey=abc123': 'apikey=[REDACTED]',
            'Token=abc123': 'Token=[REDACTED]',
            'CLIENT_SECRET=abc123': 'CLIENT_SECRET=[REDACTED]',
            '--api-key=abc123': '--api-key=[REDACTED]',
            'export TG_BOT_TOKEN=123:abc rest': 'export TG_BOT_TOKEN=[REDACTED] rest',
        }
        self.assertRedacts(cases)

    def test_secret_names_beyond_token_and_api_key(self):
        self.assertRedacts({
            f'{name}=s3cr3tvalue': f'{name}=[REDACTED]'
            for name in ['AWS_SECRET_ACCESS_KEY', 'STRIPE_SECRET_KEY', 'PRIVATE_KEY',
                         'OPENAI_KEY', 'DB_PASSWORD', 'GOOGLE_APPLICATION_CREDENTIALS',
                         'client-secret']
        })

    def test_quoted_values_with_spaces(self):
        cases = {
            "export CLIENT_SECRET='abc def ghi'": "export CLIENT_SECRET='[REDACTED]'",
            'DB_PASSWORD="correct horse battery"': 'DB_PASSWORD="[REDACTED]"',
            'token = "abc def"': 'token = "[REDACTED]"',
        }
        self.assertRedacts(cases)

    def test_json_keys(self):
        self.assertRedacts({
            '{"refresh_token": "1abc", "client_secret": "x y", "expiry": 3600}':
                '{"refresh_token": "[REDACTED]", "client_secret": "[REDACTED]", "expiry": 3600}',
            # JSON nested inside a JSON string
            '"{\\"access_token\\": \\"abc123\\"}"': '"{\\"access_token\\": \\"[REDACTED]\\"}"',
        })

    def test_yaml_and_header_lines(self):
        cases = {
            'token: abc123': 'token: [REDACTED]',
            '  - api_key: abc123': '  - api_key: [REDACTED]',
            '> x-api-key: am_abc123': '> x-api-key: [REDACTED]',
            '< x-auth-token: abc123secret': '< x-auth-token: [REDACTED]',
            'curl -H "x-api-key: am_abc123" https://x': 'curl -H "x-api-key: [REDACTED]" https://x',
        }
        self.assertRedacts(cases)


class StructurePreservedTest(RedactAssertions):
    def test_surrounding_punctuation_survives(self):
        cases = {
            '⏺ Bash(env TOKEN=abc123)': '⏺ Bash(env TOKEN=[REDACTED])',
            'GET /cb?access_token=abc123&page=2': 'GET /cb?access_token=[REDACTED]&page=2',
            'use `CLAUDE_CODE_OAUTH_TOKEN=\\S+`, then': 'use `CLAUDE_CODE_OAUTH_TOKEN=[REDACTED]`, then',
        }
        self.assertRedacts(cases)

    def test_shell_references_are_not_secrets(self):
        self.assertUnchanged(['TODOIST_API_TOKEN="$TODOIST_API_TOKEN" ./run',
                     'token=${TOKEN}', 'TOKEN=$TOKEN', 'API_KEY="$(pass show x)"',
                     'TOKEN=""', 'Authorization: Bearer $KEY',
                     """printf 'header = "x-api-key: %s"\\n' "$KEY\"""",
                     'f.write(f"export TYPESAFE_API_KEY={key}\\n")',
                     '"x-api-key": "<redacted>"', 'API_KEY=...'])

    def test_leaves_ordinary_text_alone(self):
        self.assertUnchanged(['max_tokens=4096', '"input_tokens": 1234', 'token budget is fine',
                     'secret sauce', 'sk-learn', 'we lost the token: it expired',
                     'send a Bearer token header', 'SSH_AUTH_SOCK=/tmp/agent',
                     "print('nextPageToken:', body.get('nextPageToken'))"])

    def test_idempotent(self):
        text = f'GITHUB_TOKEN={FAKE_GHP} "token": "a b" Bearer abcdef0123456789abcdef {FAKE_API}'
        once = redact(text)
        self.assertEqual(redact(once), once)
        self.assertNotIn('[REDACTED]]', once)

    def test_long_word_runs_stay_linear(self):
        # Long kebab-case and base64url runs once backtracked quadratically
        # (16 KB of a-a-a... took ~8 s). Generous bound; healthy is ~1 ms.
        for text in ['a-' * 8192, ('Ab0_-' * 4000) + '=']:
            with self.subTest(length=len(text)):
                start = time.monotonic()
                redact(text)
                self.assertLess(time.monotonic() - start, 0.5)


class ExportRedactionTest(unittest.TestCase):
    def test_export_writes_no_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'session.jsonl'
            out = Path(tmp) / 'out.txt'
            src.write_text('\n'.join(json.dumps(line) for line in FIXTURE_LINES) + '\n')

            stdout = StringIO()
            with redirect_stdout(stdout):
                export_session.export_session(str(src), str(out))
            text = out.read_text()

        for written in (text, stdout.getvalue()):
            self.assertNotIn(PREFIX, written)
            for secret in SECRET_VALUES:
                self.assertNotIn(secret, written)
        self.assertIn('Summary: Debugging auth with [REDACTED]', stdout.getvalue())
        self.assertIn('Here is the key to test with: [REDACTED]', text)
        self.assertIn('+OPENAI_KEY=[REDACTED]', text)
        self.assertIn('CLAUDE_CODE_OAUTH_TOKEN=[REDACTED]', text)
        self.assertIn('GITHUB_TOKEN=[REDACTED]', text)
        self.assertIn('AGENTMAIL_API_KEY=[REDACTED]', text)
        self.assertIn('"refresh_token": "[REDACTED]"', text)
        # The commands themselves survive; only values are scrubbed.
        self.assertIn('/proc/4242/environ', text)
        self.assertIn('cat ~/.config/gws/credentials.json', text)


if __name__ == '__main__':
    unittest.main()
