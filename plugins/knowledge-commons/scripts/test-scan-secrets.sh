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
# ---------------------------------------------------------------------------------
# Why this file is shaped the way it is
#
# Its first version had nine assertions and all nine stayed green while the scanner
# was badly broken. Three defects survived it, each found by a review that executed
# the scanner instead of reading it:
#
#   1. Quoting a credential made it invisible. KEY="realsecret" passed clean, because
#      the extracted value began with a quote and the placeholder test treated a
#      leading quote as a placeholder marker. Most secrets are written quoted.
#   2. A pattern that failed to compile produced "clean" and exit 0. The failure
#      handler ran inside a command substitution, so its exit killed only the subshell.
#   3. Deleting the entire credential-assignment scan — one of the advertised shapes —
#      left every assertion green.
#
# (3) is the one that permitted the other two, and it had a specific cause: all three
# planted secrets in the positive fixture were ALSO caught by prefix patterns, so
# "exactly 3 findings" held with the assignment path gone entirely. The suite proved
# three regexes existed. It did not test the gate.
#
# Two rules follow, and they are why the cases below look the way they do:
#
#   - Every distinct code path needs a plant that ONLY that path can catch. A case
#     that a second pattern also catches cannot fail when its path breaks.
#   - Assert per-shape, never on the finding count alone. A count is satisfied by any
#     three findings, including three from one pattern and none from the others.
# ---------------------------------------------------------------------------------

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAN="$SCRIPT_DIR/scan-secrets.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

failures=0
passes=0
skips=0

pass() { printf '  ok    — %s\n' "$1"; passes=$((passes + 1)); }
# A case that could not be exercised on this machine. Counted and printed in the
# closing line, so a run with skipped cases cannot be read as full coverage.
skip() { printf '  skip  — %s\n' "$1"; skips=$((skips + 1)); }
fail() { printf '  FAIL  — %s\n' "$1"; failures=$((failures + 1)); }

[ -x "$SCAN" ] || { printf 'scan-secrets.sh is not executable at %s\n' "$SCAN" >&2; exit 1; }

# Assert that scanning a one-line file exits with the expected code.
# $1 = description, $2 = expected exit code, $3 = file content
expect_exit() {
  local desc="$1" want="$2" content="$3" out rc
  printf '%s\n' "$content" > "$TMP/case.txt"
  out="$("$SCAN" "$TMP/case.txt" 2>&1)"; rc=$?
  if [ "$rc" -eq "$want" ]; then
    pass "$desc"
  else
    fail "$desc (wanted exit $want, got $rc)"
  fi
}

# ---------------------------------------------------------------------------------
# On the odd-looking "xox""b-…" splits below
#
# Fixture tokens are written as two adjacent quoted strings, which bash joins into one
# word at runtime. The value the scanner sees is a complete, realistic token; the value
# sitting in this file is not.
#
# This is not cosmetic. The first version used whole literals, and GitHub's push
# protection rejected the branch — it read the fixtures as a live Slack token and a live
# Stripe key. It was right to: they are exactly the shapes it exists to catch, which is
# also why they make good fixtures. Do not "tidy" these back into single literals, and do
# not resolve a future block by allowlisting the secret; split the literal instead.
# ---------------------------------------------------------------------------------

# --- 1. Each shape, planted so ONLY its own path can catch it ---------------------

printf 'each advertised shape, planted in isolation (spec §7.1)\n'

expect_exit "private key block"                1 '-----BEGIN OPENSSH PRIVATE KEY-----'
expect_exit "Anthropic key in prose"           1 "pasted sk-""ant-api03-Zx9QmTb7Lk2Wv4Rn8Ha1Cd6Ye0Uf3"
expect_exit "GitHub token in prose"            1 "token gh""p_aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789"
expect_exit "AWS access key id in prose"       1 'id AKIAIOSFODNN7EXAMPLE'
expect_exit "Slack token in prose"             1 "xox""b-123456789012-abcdefghijklmno"
expect_exit "Stripe key in prose"              1 "pasted sk""_live_abcdefghijklmnopqrstuvwxyz012345"
expect_exit "OpenAI sk-proj- key in prose"     1 "pasted sk-""proj-abcdefghijklmnopqrstuvwxyz012345"
expect_exit "JWT in prose"                     1 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dBjftJeZ4CVPmB92K27uhbUJU1p1r'
expect_exit "connection string with password"  1 'DATABASE_URL=postgres://appuser:hunter2correct@db.example.com:5432/app'

# The credential-assignment path. Each of these has NO recognized prefix, so nothing
# else in the scanner can catch them — delete that path and these go red, which is
# exactly what the first version of this suite failed to do.
printf '\ncredential assignment — the path with no prefix to fall back on\n'

expect_exit "bare assignment"                  1 'DB_PASSWORD=Tr0ub4dor3notaplaceholder'
expect_exit "double-quoted value"              1 'DB_PASSWORD="Tr0ub4dor3notaplaceholder"'
expect_exit "single-quoted value"              1 "DB_PASSWORD='Tr0ub4dor3notaplaceholder'"
expect_exit "shell export, quoted"             1 'export API_SECRET="Tr0ub4dor3notaplaceholder"'
expect_exit "JSON key/value"                   1 '  "SERVICE_PASSWORD": "abcdefghijklmnopqrstuvwxyz"'
expect_exit "YAML, lowercase key"              1 'password: hunter2correcthorsebattery'
expect_exit "lowercase with spaces"            1 "db_password = 'sup3rs3cr3tvaluehere'"

printf '\nAuthorization header\n'

expect_exit "bearer with a real value"         1 'Authorization: Bearer abcdefghijklmnopqrstuvwxyz'
expect_exit "JSON-shaped authorization"        1 '{"authorization":"Bearer abcdefghijklmnopqrstuvwx"}'
expect_exit "bearer with a placeholder"        0 'Authorization: Bearer <your-token-here>'

# A quoted value is captured whole, delimiters and spaces included. Truncating it at the
# first comma or space and then applying the 8-character floor discarded real credentials.
printf '\nquoted values spanning delimiters\n'

expect_exit "passphrase with spaces"            1 'PASSPHRASE="correct horse battery staple"'
expect_exit "comma inside the first 8 chars"    1 'PASSWORD="abcdefg,hijklmnop"'
expect_exit "semicolon inside a JSON value"     1 '{"db_password":"a;bcdefghijklmnop"}'

# One line, several shapes: one finding carrying every label. Reporting only the first
# leaves a reader redacting what the context window happens to show while the labelled
# secret stays in the file.
printf '\nseveral shapes on one line\n'

multi="curl -H \"Authorization: Bearer gh""p_AAAABBBBCCCCDDDDEEEEFFFFGGGG\" -d \"slack=xox""b-1234567890-abcdefghijklmno\""
printf '%s\n' "$multi" > "$TMP/multi.txt"
out="$("$SCAN" "$TMP/multi.txt" 2>&1)"
n="$(printf '%s' "$out" | grep -c '^\[')"
[ "$n" -eq 1 ] && pass "one line yields one finding" || fail "expected 1 finding for one line, got $n"
if printf '%s' "$out" | grep -q 'GitHub token' && printf '%s' "$out" | grep -q 'Slack token'; then
  pass "that finding names every shape on the line"
else
  fail "a shape on the line went unlabelled: $(printf '%s' "$out" | grep '^\[')"
fi

# Two assignment-shaped values on one line, the first a placeholder. Checking only the
# first match and skipping the line on its verdict is fail-open — the existing
# multi-shape case above uses two DIFFERENT patterns, so it could not catch this.
printf '\nseveral assignments on one line\n'

expect_exit "placeholder first, real second"   1 'DEBUG_SECRET=todo PROD_PASSWORD=Tr0ub4dor3xyzLONGVALUE'
expect_exit "short first, real second"         1 'KEY=abc API_PASSWORD=R3alSecretValueHere123'
expect_exit "placeholder bearer, real token"   1 'authorization: Bearer <your-token-here> auth_token: R3alBearerValue123456'
expect_exit "both placeholders stays clean"    0 'DEBUG_SECRET=todo OTHER_KEY=<your-key-here>'

printf '\nmultiple files\n'

printf 'nothing here\n' > "$TMP/clean.txt"
printf 'DB_PASSWORD=Tr0ub4dor3notaplaceholder\n' > "$TMP/dirty.txt"
"$SCAN" "$TMP/clean.txt" "$TMP/dirty.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 1 ] && pass "a secret in the second file is found" || fail "multi-file scan must exit 1, got $rc"
"$SCAN" "$TMP/clean.txt" "$TMP/gone.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "one missing file fails the whole scan closed" || fail "missing second file must exit 2, got $rc"

# --- 2. Things that must NOT trip it ---------------------------------------------

printf '\nnegative cases — placeholders and prose are not credentials\n'

expect_exit "bracketed placeholder"            0 'API_KEY=<your-key-here>'
expect_exit "template reference"               0 'TOKEN=${GITHUB_TOKEN}'
expect_exit "dummy word"                       0 'SECRET=changeme'
expect_exit "prose naming key prefixes"        0 'OpenAI keys start with sk- and Anthropic keys with sk-ant-.'
expect_exit "short value"                      0 'KEY=abc'
expect_exit "whole-value dummy word"           0 'SECRET=redacted'
expect_exit "dummy word with separator"        0 'KEY=change-me-please'

# A dictionary word may be a placeholder as the WHOLE value; as a prefix of a longer
# run it is just how the credential happens to start. Matching it as a prefix silently
# suppressed real secrets — "starts with a common English word" is not rare in a key.
printf '\nreal values that merely begin with a placeholder word\n'

expect_exit "value beginning null"             1 'API_KEY=nullXk29LpQr7Wm3Zt8Vc1Bh6Ny4'
expect_exit "value beginning true"             1 'PASSWORD=trueBl00dSecretValue99'
expect_exit "value beginning fake"             1 'API_KEY=fakeR3alSecretValue123456'
expect_exit "value beginning nil"              1 'SECRET=nilsHiddenPassphrase2026'

# --- 3. Fail-closed -------------------------------------------------------------

printf '\nfail-closed — a scan that cannot run is not a scan that passed\n'

"$SCAN" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "no arguments exits 2" || fail "no arguments must exit 2, got $rc"

"$SCAN" "$TMP/nope.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "missing file exits 2" || fail "missing file must exit 2, got $rc"

"$SCAN" "$TMP" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "directory argument exits 2" || fail "directory must exit 2, got $rc"

# The regression test for defect (2) above. A maintainer adding a pattern typos the
# regex; grep exits 2 on it. The scan must stop rather than continue.
#
# The broken pattern is injected AHEAD of the real Stripe pattern, which is what makes
# this assertion sharp: if the fail-closed check regressed, the scan would carry on,
# reach the real pattern, report the secret and exit 1 — so the test wants 2, and 1 is
# a failure rather than an acceptable near-miss. (The file's secret is caught by the
# real pattern too; the ordering, not the secret's uniqueness, is what this pins.)
#
# The pattern is broken by an UNMATCHED PARENTHESIS, which every grep rejects. It used
# to be broken by an unterminated interval ('…{20,'), and that is not an error
# everywhere: BSD grep (macOS, where this was written) refuses it, GNU grep compiles it
# with the brace taken literally and exits 1 for "no match". On Linux the scan then ran
# correctly to the real pattern and exited 1, and this case failed with a message that
# said the gate was reporting clean when the gate was fine and the fixture was not
# broken. So the fixture is now checked before it is used: if this machine's grep
# accepts the pattern, the case says so instead of blaming the scanner.
BROKEN_RE='sk_live_([A-Za-z0-9]{20,}'
printf 'pasted from the dashboard: %s\n' "sk""_live_abcdefghijklmnopqrstuvwxyz012345" > "$TMP/bare-secret.txt"
printf 'DB_PASSWORD=Tr0ub4dor3notaplaceholder\n' > "$TMP/bare-assign.txt"
printf 'Authorization: Bearer abcdefghijklmnopqrstuvwxyz\n' > "$TMP/bare-auth.txt"

grep -E -e "$BROKEN_RE" -- "$TMP/bare-secret.txt" >/dev/null 2>&1; rc=$?
BROKEN="$TMP/broken-scan.sh"
: > "$BROKEN"; chmod +x "$BROKEN"
if [ "$rc" -gt 1 ]; then
  sed "s|add_pattern \"Google API key (AIza)\".*|add_pattern \"Deliberately broken\" '$BROKEN_RE'|" \
    "$SCAN" > "$BROKEN"
  if grep -q 'Deliberately broken' "$BROKEN"; then
    "$BROKEN" "$TMP/bare-secret.txt" >/dev/null 2>&1; rc=$?
    if [ "$rc" -eq 2 ]; then
      pass "a pattern that fails to compile exits 2, with the secret still unreported"
    else
      fail "a pattern that fails to compile must exit 2, got $rc (0 = reported clean, 1 = scanned on past the failure)"
    fi
  else
    fail "could not inject the broken pattern — the line this test rewrites has moved"
  fi

  # The same failure in the two value-checked scans, which do not go through the
  # pattern arrays and so are not covered by the case above.
  for target in ASSIGN_RE:bare-assign.txt AUTH_RE:bare-auth.txt; do
    var="${target%%:*}"; fixture="${target#*:}"
    sed "s|^readonly $var='|readonly $var='(|" "$SCAN" > "$BROKEN"
    if grep -q "^readonly $var='(" "$BROKEN"; then
      "$BROKEN" "$TMP/$fixture" >/dev/null 2>&1; rc=$?
      [ "$rc" -eq 2 ] && pass "a broken $var exits 2" || fail "a broken $var must exit 2, got $rc"
    else
      fail "could not break $var — the line this test rewrites has moved"
    fi
  done
else
  fail "this machine's grep accepts the deliberately broken pattern (exit $rc) — the fixture, not the scanner, needs a pattern this grep rejects"
fi

# A grep that fails on the SECOND pass. The two value-checked scans run grep twice: once
# over the file, then once per matching line (-o) to pull out each value. The first was
# checked and the second was not, so a failure there left an empty result, the line was
# skipped as "no value", and a credential the first pass had already found was reported
# clean with exit 0. The stand-in grep below is the real one except that it fails
# whenever it is asked for -o.
SHIM="$TMP/shim"
mkdir -p "$SHIM"
REAL_GREP="$(command -v grep)"
printf '#!/usr/bin/env bash\nfor a in "$@"; do [ "$a" = "-o" ] && exit 2; done\nexec "%s" "$@"\n' "$REAL_GREP" > "$SHIM/grep"
chmod +x "$SHIM/grep"
PATH="$SHIM:$PATH" "$SCAN" "$TMP/bare-assign.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "grep failing on the per-line pass exits 2 (assignment)" \
  || fail "grep failing on the per-line pass must exit 2, got $rc (assignment)"
PATH="$SHIM:$PATH" "$SCAN" "$TMP/bare-auth.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "grep failing on the per-line pass exits 2 (authorization)" \
  || fail "grep failing on the per-line pass must exit 2, got $rc (authorization)"

# Matches that were found and then never read. The scanner used to feed each grep
# result to a loop through a here-document, and bash backs a large one with a temp
# file. If that file cannot be written (a full or read-only temp directory) the loop is
# skipped with an error on stderr and the script carries on: every match in that result
# was lost, and the run ended "clean" with exit 0. The loops read from a pipe now, so
# with no writable temp file the scan must simply still work and report the secret.
#
# Simulated with a zero file-size limit and SIGXFSZ ignored, so a temp-file write fails
# instead of killing the shell. Each fixture line is far longer than a pipe buffer,
# which is what makes bash reach for a temp file — and is also what a rendered
# transcript looks like. The simulation is checked first, with a here-document of the
# same size in this shell: where it does not bite, the cases are SKIPPED, because a
# pass there would prove nothing.
long_tail="$(head -c 200000 /dev/zero | tr '\0' 'a')"
( trap '' XFSZ; ulimit -f 0; cat >/dev/null <<PROBE
$long_tail
PROBE
) 2>/dev/null; probe_rc=$?
for target in "prefix pattern:bare-secret.txt" "assignment:bare-assign.txt" "authorization:bare-auth.txt"; do
  name="${target%%:*}"; fixture="${target#*:}"
  if [ "$probe_rc" -eq 0 ]; then
    skip "no way to simulate an unwritable temp file here, so this is untested ($name)"
    continue
  fi
  printf '%s %s\n' "$(cat "$TMP/$fixture")" "$long_tail" > "$TMP/long.txt"
  ( trap '' XFSZ; ulimit -f 0; "$SCAN" "$TMP/long.txt" >/dev/null 2>&1 ); rc=$?
  [ "$rc" -eq 1 ] && pass "with no writable temp file the secret is still reported ($name)" \
    || fail "with no writable temp file the scan must still exit 1, got $rc ($name)"
done

# The backstop behind that: a loop that had matches to read and never ran must stop the
# scan. Nothing in normal operation makes a pipe fail on demand, so each loop's input is
# rewritten to a file that does not exist — bash reports the failed redirection, skips
# the loop, and carries on, which is the exact shape the backstop exists for. The outer
# loops (one per scan) and the inner per-match loops are broken separately, so each
# guard is reached on its own.
for target in 'outer:"$out":bare-secret.txt:3' 'outer:"$out":bare-assign.txt:3' 'outer:"$out":bare-auth.txt:3' \
              'inner:"$matches":bare-assign.txt:2' 'inner:"$matches":bare-auth.txt:2'; do
  IFS=: read -r which var fixture want_n <<<"$target"
  sed "s|done < <(printf '%s\\\\n' $var)|done < \"$TMP/no-such-input\"|" "$SCAN" > "$BROKEN"
  n="$(grep -c "done < \"$TMP/no-such-input\"" "$BROKEN")"
  if [ "$n" -ne "$want_n" ]; then
    fail "could not break the $which loops ($n rewritten, wanted $want_n) — the lines this test rewrites have moved"
    continue
  fi
  "$BROKEN" "$TMP/$fixture" >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 2 ] && pass "an $which loop that never ran exits 2 ($fixture)" \
    || fail "an $which loop that never ran must exit 2, got $rc ($fixture)"
done

# --- 4. Bytes that are not text ---------------------------------------------------
#
# In a UTF-8 locale a byte that is not valid UTF-8 matches no bracket expression, not
# even a negated one, so it ended the value: DB_PASSWORD=abcd<FF>efgh… measured as the
# four characters before the stray byte and was dropped as too short. The scanner now
# runs in the C locale, where every byte is a character.
printf '\nbytes that are not valid UTF-8\n'

printf 'DB_PASSWORD=Tr0u\377b4dor3notaplaceholder\n' > "$TMP/badutf.txt"
LC_ALL=en_US.UTF-8 "$SCAN" "$TMP/badutf.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 1 ] && pass "a stray byte inside a value does not hide it" \
  || fail "a value containing an invalid UTF-8 byte must exit 1, got $rc"

# --- result -----------------------------------------------------------------------

printf '\n'
printf '%d passed, %d failed, %d skipped.\n' "$passes" "$failures" "$skips"
[ "$failures" -eq 0 ] && exit 0
exit 1
