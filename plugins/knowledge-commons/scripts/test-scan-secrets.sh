#!/usr/bin/env bash
#
# test-scan-secrets.sh — the planted-secret test for the redaction gate's floor.
#
# This is the spec's §7.1 first half, committed so it can be re-run rather than
# performed once at implementation time. Run it after any edit to scan-secrets.sh.
#
#   ./test-scan-secrets.sh
#
# Exits 0 if every case passes, 1 otherwise.
#
# Why this exists as a file rather than a paragraph in a spec: the floor's whole claim
# is that it is dumb, deterministic, and verifiable against a planted secret. On its
# first run the scanner reported three findings and silently missed a planted private
# key — a pattern beginning with "-" was parsed by grep as options, grep exited 2, and
# the error was discarded, so the miss looked exactly like a clean pass. A preflight
# that passes while the thing it guards is broken manufactures confidence.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAN="$SCRIPT_DIR/scan-secrets.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

failures=0

pass() { printf '  ok    — %s\n' "$1"; }
fail() { printf '  FAIL  — %s\n' "$1"; failures=$((failures + 1)); }

[ -x "$SCAN" ] || { printf 'scan-secrets.sh is not executable at %s\n' "$SCAN" >&2; exit 1; }

# --- fixtures ---------------------------------------------------------------------

cat > "$TMP/positive.txt" <<'FIXTURE'
Session notes.

  ANTHROPIC_API_KEY=sk-ant-api03-Zx9QmTb7Lk2Wv4Rn8Ha1Cd6Ye0Uf3Ij5Ko7Pl9Qs2Tw4Xz6Ab8Cd

-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
-----END OPENSSH PRIVATE KEY-----

  DATABASE_URL=postgres://appuser:hunter2correctbattery@db.internal.example.com:5432/app
FIXTURE

cat > "$TMP/negative.txt" <<'FIXTURE'
The docs example uses a placeholder, as they should:
  API_KEY=<your-key-here>

We discussed how OpenAI keys start with the sk- prefix and Anthropic's with sk-ant-.
  TOKEN=${GITHUB_TOKEN}
  SECRET=changeme
FIXTURE

# --- cases ------------------------------------------------------------------------

printf 'planted-secret test (spec §7.1)\n'

out="$("$SCAN" "$TMP/positive.txt" 2>&1)"; rc=$?
[ "$rc" -ne 0 ] && pass "positive fixture exits non-zero (got $rc)" \
                || fail "positive fixture must exit non-zero, got $rc"

# Each planted secret must surface as its own finding. Counting findings alone is not
# enough — three findings can be two secrets and a duplicate, which is what the first
# broken version produced.
for shape in "private key block" "Anthropic API key" "connection string carrying a password"; do
  printf '%s' "$out" | grep -q "$shape" \
    && pass "reports: $shape" \
    || fail "did not report: $shape"
done

count="$(printf '%s' "$out" | grep -c '^\[[0-9]*\]')"
[ "$count" -eq 3 ] \
  && pass "exactly 3 distinct findings, no duplicates" \
  || fail "expected 3 distinct findings, got $count"

out="$("$SCAN" "$TMP/negative.txt" 2>&1)"; rc=$?
[ "$rc" -eq 0 ] \
  && pass "negative fixture exits zero (placeholders and prose are not credentials)" \
  || fail "negative fixture must exit zero, got $rc: $out"

printf '\nfail-closed test\n'

"$SCAN" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "no arguments exits 2" || fail "no arguments must exit 2, got $rc"

"$SCAN" "$TMP/nope.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "missing file exits 2" || fail "missing file must exit 2, got $rc"

"$SCAN" "$TMP" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "directory argument exits 2" || fail "directory must exit 2, got $rc"

# --- result -----------------------------------------------------------------------

printf '\n'
if [ "$failures" -eq 0 ]; then
  printf 'all cases passed.\n'
  exit 0
fi
printf '%d case(s) failed.\n' "$failures"
exit 1
