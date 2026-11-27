#!/usr/bin/env python3
"""Compare two versions of scan-secrets.sh on generated lines. FAKE values only.

A maintenance tool for changes to scan-secrets.sh, not part of the gate. The fixture
tests in test-scan-secrets.sh pin known shapes; this looks for what they do not pin, by
running an old and a new copy of the scanner over the same generated file and comparing
which lines each reports.

Usage:
    fuzz-scan-secrets.py <old-script> <new-script> [seed] [lines]

To compare a working copy against the last commit:

    git show HEAD:plugins/knowledge-commons/scripts/scan-secrets.sh > /tmp/scan-old.sh
    chmod +x /tmp/scan-old.sh
    ./fuzz-scan-secrets.py /tmp/scan-old.sh ./scan-secrets.sh 31

Every generated line is well-formed and is one of two kinds: it carries exactly one
random-looking fake secret under a credential-named key, or it holds only placeholders.
The shapes are the ones rendered transcripts contain: JSON, JSON escaped once and
twice, env lists joined by spaces or by a literal backslash-n, env and compose files
quoted inside a JSON string, and YAML flow mappings, with nested objects and JSON held
in strings.

What to read in the output:
  - "secrets new misses" must be 0. So must "secrets old reports, new misses": that is
    a credential the gate used to catch and no longer does.
  - "placeholder lines flagged" is the false-positive count. It should not rise. Each
    one stops an archive until someone accepts it by hand.

Exit status: 0 if the new script reports every fake secret, 1 if it misses any, 2 on
bad usage. A rise in false positives does not change the exit status; read the counts.

Try several seeds. Add a shape to the generator whenever a review finds one by hand:
the escaped-newline env list and the shell default (${VAR:-default}) are here because
each hid a false positive that three rounds of fixture tests had not caught.
"""
import collections
import json
import os
import random
import re
import subprocess
import sys
import tempfile

if len(sys.argv) < 3:
    sys.stderr.write("usage: fuzz-scan-secrets.py <old-script> <new-script> [seed] [lines]\n")
    sys.exit(2)

OLD, NEW = sys.argv[1], sys.argv[2]
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 31
COUNT = int(sys.argv[4]) if len(sys.argv) > 4 else 1500
for script in (OLD, NEW):
    if not os.access(script, os.X_OK):
        sys.stderr.write(f"not an executable file: {script}\n")
        sys.exit(2)
random.seed(SEED)

# Obviously fake. Never put a real credential in this file.
STRONG = [
    "Zq7xR2mK9pLw4TnB8vYc", "Ab3dEf6hIj9kLmN2pQrS", "Tr0ub4dor3xyzQ", "S3cr3tV4lu3Here99", "p9X2kLm4Qw7ZtB1nVc6R",
]
PLACEHOLDERS = [
    "<your-api-key>", "${API_KEY}", "$GITHUB_TOKEN", "changeme", "example", "xxxxxxxxxxxx", "********",
    "your-password-here", "<token>", "none", "{{secret}}", "my-secret-value", "${DB_PASSWORD:-changeme}",
    "${SECRET_KEY:?must be set}", "$(cat /run/secrets/db_password)", "<REDACTED>", "null", "todo",
    "${{ secrets.API_TOKEN }}", "process.env.API_KEY", "os.environ['API_KEY']", "YOUR_API_KEY_HERE",
]
CRED_NAMES = ["API_KEY", "password", "DB_PASSWORD", "secret_token", "client_secret", "auth_token", "PASSPHRASE", "credentials_key"]
PLAIN_NAMES = ["note", "config", "user", "comment", "description", "image", "port"]


def json_object(depth, with_secret):
    o = {}
    for _ in range(random.randint(1, 3)):
        o[random.choice(PLAIN_NAMES)] = random.choice(["hello world", random.choice(PLACEHOLDERS), 42])
    for _ in range(random.randint(0, 2)):
        o[random.choice(CRED_NAMES)] = random.choice(PLACEHOLDERS)
    if with_secret:
        if depth and random.random() < 0.5:
            inner = json_object(depth - 1, True)
            key = random.choice(CRED_NAMES + PLAIN_NAMES + ["credentials"])
            # A nested object, or JSON held in a string.
            o[key] = inner if random.random() < 0.5 else json.dumps(inner)
        else:
            o[random.choice(CRED_NAMES)] = random.choice(STRONG)
    items = list(o.items())
    random.shuffle(items)
    return dict(items)


def env_list(with_secret, joiner, most):
    parts = []
    for _ in range(random.randint(0, most)):
        name = random.choice(CRED_NAMES + PLAIN_NAMES).upper()
        quote = random.choice(["", "", '"', "'"])
        prefix = random.choice(["", "", "export "])
        parts.append(f"{prefix}{name}={quote}{random.choice(PLACEHOLDERS)}{quote}")
    if with_secret:
        quote = random.choice(["", '"', "'"])
        secret = f"{random.choice(CRED_NAMES).upper()}={quote}{random.choice(STRONG)}{quote}"
        parts.insert(random.randint(0, len(parts)), secret)
    return joiner.join(parts) or "nothing here"


def one_line(with_secret, kind):
    if kind in ("json", "escaped", "escaped2"):
        s = json.dumps(json_object(2, with_secret))
        if kind == "escaped":
            s = "tool output: " + json.dumps(s)
        if kind == "escaped2":
            s = "tool output: " + json.dumps(json.dumps(s))
        return s
    if kind == "env":
        return env_list(with_secret, random.choice([" ", "; "]), 4)
    if kind == "env-n":
        return env_list(with_secret, "\\n", 30)  # a literal backslash-n, as inside a JSON string
    if kind == "env-n-json":
        return json.dumps({"path": ".env.example", "content": env_list(with_secret, "\n", 20)})
    if kind == "compose":
        entries = [
            f"      - {random.choice(CRED_NAMES + PLAIN_NAMES).upper()}={random.choice(PLACEHOLDERS)}"
            for _ in range(random.randint(1, 8))
        ]
        if with_secret:
            entries.insert(
                random.randint(0, len(entries)),
                f"      - {random.choice(CRED_NAMES).upper()}={random.choice(STRONG)}",
            )
        return json.dumps({"content": "services:\n  db:\n    environment:\n" + "\n".join(entries)})
    parts = [f"{random.choice(CRED_NAMES)}: {random.choice(PLACEHOLDERS)}" for _ in range(random.randint(0, 3))]
    if with_secret:
        parts.insert(random.randint(0, len(parts)), f"{random.choice(CRED_NAMES)}: {random.choice(STRONG)}")
    return "{" + ", ".join(parts) + "}"


KINDS = ["json", "escaped", "escaped2", "env", "env-n", "env-n-json", "yaml", "compose"]
lines, meta = [], []
for _ in range(COUNT):
    with_secret = random.random() < 0.55
    kind = random.choice(KINDS)
    lines.append(one_line(with_secret, kind))
    meta.append((with_secret, kind))

work = tempfile.mkdtemp()
path = os.path.join(work, "f.txt")
with open(path, "w") as fh:
    fh.write("\n".join(lines) + "\n")


def reported(script):
    """Line numbers the script reports. Its exit status must be 0 (clean) or 1 (findings)."""
    run = subprocess.run([script, path], capture_output=True, text=True, errors="replace")
    if run.returncode not in (0, 1):
        sys.stderr.write(f"{script} exited {run.returncode}; it could not scan the generated file:\n{run.stderr}")
        sys.exit(2)
    return {int(m.group(1)) for m in re.finditer(r"f\.txt:(\d+)$", run.stdout, re.M)}


try:
    old, new = reported(OLD), reported(NEW)
finally:
    os.remove(path)
    os.rmdir(work)

secret_lines = {i + 1 for i, (s, _) in enumerate(meta) if s}
clean_lines = {i + 1 for i, (s, _) in enumerate(meta) if not s}
missed = sorted(secret_lines - new)
regressed = sorted((old - new) & secret_lines)


def by_kind(numbers):
    return dict(collections.Counter(meta[n - 1][1] for n in numbers))


print(f"seed {SEED}: {COUNT} lines, {len(secret_lines)} with a fake secret, {len(clean_lines)} placeholders only")
print(f"  secrets reported:           old {len(old & secret_lines)}/{len(secret_lines)}   new {len(new & secret_lines)}/{len(secret_lines)}")
print(f"  secrets old reports, new misses: {len(regressed)}   secrets new misses: {len(missed)}")
print(f"  placeholder lines flagged:  old {len(old & clean_lines)}/{len(clean_lines)}   new {len(new & clean_lines)}/{len(clean_lines)}")
print("  new-script false positives by kind:", by_kind(sorted(new & clean_lines)))
print("  old-script false positives by kind:", by_kind(sorted(old & clean_lines)))
for n in missed[:8]:
    print("  MISS:", meta[n - 1][1], repr(lines[n - 1][:230]))
for n in sorted((new - old) & clean_lines)[:10]:
    print("  FALSE POSITIVE, new only:", meta[n - 1][1], repr(lines[n - 1][:230]))

sys.exit(1 if missed else 0)
