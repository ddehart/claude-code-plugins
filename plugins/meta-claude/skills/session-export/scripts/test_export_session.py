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


def armor(edge, kind='', suffix=''):
    """A private-key armor line, split so the file holds no literal key header."""
    return f'-----{edge} {kind}PRIV' + f'ATE KEY{suffix}-----'


KEY_LINES = [ALNUM + ALNUM[:28], ALNUM[::-1] + 'abcdefghijklmnopqrstuvwxyz01', 'ZmFrZWtleWJvZHk=']
BODY = '\n'.join(KEY_LINES)
SSH_BEGIN, SSH_END = armor('BEGIN', 'OPENSSH '), armor('END', 'OPENSSH ')
# A key JSON-escaped onto one line (a service-account file), and its redaction
ESCAPED_KEY = '\\n'.join([armor('BEGIN'), *KEY_LINES, armor('END')]) + '\\n'
ESCAPED_KEY_REDACTED = armor('BEGIN') + '\\n[REDACTED]\\n' + armor('END') + '\\n'

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
            'type': 'tool_use', 'id': 'toolu_3', 'name': 'Bash',
            'input': {'command': 'cat ~/.ssh/id_ed25519; psql postgres://app:hunter2db@db/app -c "select 1"'},
        }]},
    },
    {
        'type': 'user',
        'message': {'content': [{
            'type': 'tool_result', 'tool_use_id': 'toolu_3',
            'content': '\n'.join([SSH_BEGIN, *KEY_LINES, SSH_END]),
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
    'am_notarealkey456', 'GOCSPX-notarealsecret', 'hunter2db', *KEY_LINES,
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

    def test_unquoted_spaced_assignment_when_credential_like(self):
        self.assertRedacts({
            'PrivateKey = yAnz5TF+lXXJte14tji3zlMNq+hd2rYUIgJBgB3fBmk=': 'PrivateKey = [REDACTED]',
            'password = hunter2hunter2hunter2': 'password = [REDACTED]',
        })
        # Code, not credentials: calls, attribute chains, short values
        self.assertUnchanged([
            'token = get_token()', 'password = self.config.password',
            'api_key = os.environ["API_KEY"]', 'secret = 42',
        ])

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


class PrivateKeyTest(RedactAssertions):
    def test_block_body_replaced_armor_kept(self):
        self.assertRedacts({
            f'before\n{SSH_BEGIN}\n{BODY}\n{SSH_END}\nafter':
                f'before\n{SSH_BEGIN}\n[REDACTED]\n{SSH_END}\nafter',
            # Indented the way the exporter indents tool results
            '\n'.join('  ' + line for line in [SSH_BEGIN, *KEY_LINES, SSH_END]):
                f'  {SSH_BEGIN}\n[REDACTED]\n{SSH_END}',
            # JSON-escaped on one line (a service-account file, a dumped config)
            f'"{ESCAPED_KEY}"': f'"{ESCAPED_KEY_REDACTED}"',
        })

    def test_cut_off_block_without_end_line(self):
        self.assertRedacts({
            f'{SSH_BEGIN}\n  {KEY_LINES[0]}\n  {KEY_LINES[1]}\n    ... (12 more lines)\n\n⏺ Next':
                f'{SSH_BEGIN}\n[REDACTED]\n    ... (12 more lines)\n\n⏺ Next',
            f'{SSH_BEGIN}\n  {KEY_LINES[0]}\n\n⏺ Next': f'{SSH_BEGIN}\n[REDACTED]\n\n⏺ Next',
        })

    def test_encrypted_and_pgp_blocks(self):
        encrypted = [armor('BEGIN', 'RSA '), 'Proc-Type: 4,ENCRYPTED', 'DEK-Info: AES-128-CBC,0A1B2C3D',
                     '', *KEY_LINES, armor('END', 'RSA ')]
        pgp = [armor('BEGIN', 'PGP ', ' BLOCK'), 'Version: GnuPG v2', '', *KEY_LINES,
               armor('END', 'PGP ', ' BLOCK')]
        self.assertRedacts({
            '\n'.join(encrypted): f'{encrypted[0]}\n[REDACTED]\n{encrypted[-1]}',
            '\n'.join(pgp): f'{pgp[0]}\n[REDACTED]\n{pgp[-1]}',
        })

    def test_key_assigned_to_a_secret_named_variable(self):
        # The keyed pass used to redact the BEGIN line itself, leaving the body
        # for nothing to find. These are the env-dump and config shapes.
        self.assertRedacts({
            f'HOME=/home/u\nSSH_PRIVATE_KEY={SSH_BEGIN}\n{BODY}\n{SSH_END}\nPATH=/bin':
                f'HOME=/home/u\nSSH_PRIVATE_KEY={SSH_BEGIN}\n[REDACTED]\n{SSH_END}\nPATH=/bin',
            f'private_key: {SSH_BEGIN}\n  {BODY}\n  {SSH_END}':
                f'private_key: {SSH_BEGIN}\n[REDACTED]\n{SSH_END}',
            f'{{"private_key": "{ESCAPED_KEY}"}}': f'{{"private_key": "{ESCAPED_KEY_REDACTED}"}}',
        })

    def test_flattened_onto_one_line(self):
        # Some env and secret displays join a key's lines with spaces
        flat = ' '.join([SSH_BEGIN, *KEY_LINES, SSH_END])
        self.assertRedacts({
            f'"private_key": "{flat}"': f'"private_key": "{SSH_BEGIN} [REDACTED] {SSH_END}"',
            f'SSH_PRIVATE_KEY={flat} PATH=/bin': f'SSH_PRIVATE_KEY={SSH_BEGIN} [REDACTED] {SSH_END} PATH=/bin',
        })

    def test_line_cut_by_truncation(self):
        # A one-line JSON dump cut at 500 characters ends mid-body with `...`
        cut = '{"private_key": "' + armor('BEGIN') + '\\n' + KEY_LINES[0][:40] + '...'
        self.assertRedacts({cut: '{"private_key": "' + armor('BEGIN') + '\\n[REDACTED]...'})

    def test_armor_line_alone_untouched(self):
        self.assertUnchanged([
            f"grep -l -- '{SSH_BEGIN}' ~/.ssh/*",
            f'Look for a line reading {SSH_BEGIN} at the top.',
        ])

    def test_public_material_untouched(self):
        self.assertUnchanged([
            f'ssh-ed25519 {KEY_LINES[0]} derek@devbox',
            f'-----BEGIN PUBLIC KEY-----\n{KEY_LINES[0]}\n-----END PUBLIC KEY-----',
            f'-----BEGIN CERTIFICATE-----\n{KEY_LINES[0]}\n-----END CERTIFICATE-----',
        ])


class UrlCredentialTest(RedactAssertions):
    def test_password_redacted_user_and_host_kept(self):
        self.assertRedacts({
            'postgres://app:hunter2@db.internal:5432/app': 'postgres://app:[REDACTED]@db.internal:5432/app',
            'git remote set-url origin https://x-access-token:abc123def@github.com/o/r.git':
                'git remote set-url origin https://x-access-token:[REDACTED]@github.com/o/r.git',
            'redis://:s3cret@localhost:6379/0': 'redis://:[REDACTED]@localhost:6379/0',
            'amqp://u:pa:ss@mq': 'amqp://u:[REDACTED]@mq',
            # Raw `/` and `@` in generated passwords
            'postgres://app:ab/cd+ef==@db.internal/app': 'postgres://app:[REDACTED]@db.internal/app',
            'postgres://app:p@ss@db.internal/app': 'postgres://app:[REDACTED]@db.internal/app',
            '(see mysql://root:x/y@z@db:3306)': '(see mysql://root:[REDACTED]@db:3306)',
        })

    def test_urls_without_a_password_untouched(self):
        self.assertUnchanged([
            'http://localhost:8080/path', 'https://user@github.com/o/r', 'git@github.com:org/repo.git',
            'postgres://app:$DB_PASSWORD@db/app', 'mailto:someone@example.com',
            'see http://example.com/a:b@c',
            'http://localhost:8080/users/@me',
        ])


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
        # Long kebab-case, dotted, and base64url runs once backtracked
        # quadratically (64 KB of a-a-a... took seconds). Generous bound;
        # healthy is a few ms.
        for text in ['a-' * 32768, 'a.' * 32768, ('Ab0_-' * 13000) + '=',
                     'x://u:' + 'b@' * 32768, 'PrivateKey = ' + 'a1' * 32768,
                     'x://u:' * 11000, 'a://' * 16000, 'http://h:8080/p,' * 4000]:
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
        self.assertIn('postgres://app:[REDACTED]@db/app', text)
        self.assertIn(f'{SSH_BEGIN}\n[REDACTED]\n{SSH_END}', text)


if __name__ == '__main__':
    unittest.main()
