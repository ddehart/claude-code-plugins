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
# Unmatched parenthesis: every grep rejects it. (GNU grep accepts an unterminated
# interval.)
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
for fixture in bare-assign.txt bare-auth.txt; do
  PATH="$SHIM:$PATH" "$SCAN" "$TMP/$fixture" >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 2 ] && pass "grep failing on the per-line pass exits 2 ($fixture)" \
    || fail "grep failing on the per-line pass must exit 2, got $rc ($fixture)"
done

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
# loops (prefix patterns, value-checked scans) and the inner per-match loop are broken
# separately, so each guard is reached on its own.
for target in 'outer:"$out":bare-secret.txt:2' 'outer:"$out":bare-assign.txt:2' 'outer:"$out":bare-auth.txt:2' \
              'inner:"$matches":bare-assign.txt:1' 'inner:"$matches":bare-auth.txt:1'; do
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

# --- 5. Values the scan used to look straight past --------------------------------
#
# Every case here that expects 1 exited 0 before it was fixed, apart from the first,
# which pins that FAKE is reported when it stands alone — so a 0 below is the shape
# around it defeating the scan, not the value being unremarkable.
FAKE='Zq7NotARealSecret4Kd9Lm2Xp'

printf '\nJSON inside JSON — quotes escaped with backslashes\n'

expect_exit "the fake value on its own"            1 "PROD_PASSWORD=$FAKE"
expect_exit "escaped key and value"                1 "{\\\"API_KEY\\\": \\\"$FAKE\\\"}"
expect_exit "escaped Authorization header"         1 "\\\"Authorization\\\": \\\"Bearer $FAKE\\\""
expect_exit "escaped twice"                        1 "\\\\\\\"API_KEY\\\\\\\": \\\\\\\"$FAKE\\\\\\\""
expect_exit "escaped placeholder stays clean"      0 '{\"API_KEY\": \"<your-key-here>\"}'
expect_exit "escaped bearer placeholder stays clean" 0 '\"Authorization\": \"Bearer <your-token-here>\"'

# An earlier value on the line that takes the real assignment with it.
printf '\na real assignment inside an earlier value\n'

expect_exit "quoted note opening with <…>"         1 "NOTE_KEY='<see below> and then PROD_PASSWORD=$FAKE isn't shown"
expect_exit "quoted note opening with \${…}"       1 "{\"note_key\": \"\${X} PROD_PASSWORD=$FAKE\"}"
expect_exit "no separator between assignments"     1 "DEBUG_SECRET=<x>PROD_PASSWORD=$FAKE"
expect_exit "key inside a JSON object"             1 "{\"credentials\": {\"password\": \"$FAKE\"}}"
expect_exit "key inside an escaped JSON object"    1 "{\\\"credentials\\\": {\\\"password\\\": \\\"$FAKE\\\"}}"
expect_exit "JSON object of placeholders is clean" 0 '{"credentials": {"password": "<redacted>"}}'

# A value that only STARTS like a placeholder.
printf '\nreal values that merely begin like a placeholder\n'

expect_exit "begins <"                             1 "PROD_PASSWORD=<$FAKE"
expect_exit "begins \$"                            1 "PROD_PASSWORD=\$$FAKE"
expect_exit "begins {"                             1 "PROD_PASSWORD={$FAKE"
expect_exit "begins xxx"                           1 "PROD_PASSWORD=xxx$FAKE"
expect_exit "begins ***"                           1 "PROD_PASSWORD=***$FAKE"
expect_exit "begins ..."                           1 "PROD_PASSWORD=...$FAKE"
expect_exit "leading space inside quotes"          1 "PROD_PASSWORD=\" $FAKE\""
expect_exit "leading vertical tab inside quotes"   1 "PROD_PASSWORD=\"$(printf '\v')$FAKE\""
expect_exit "dummy word, dash, real value"         1 "PROD_PASSWORD=example-$FAKE"
expect_exit "dummy word, colon, real value"        1 "PROD_PASSWORD=none:$FAKE"
expect_exit "dummy word, dollar, real value"       1 "PROD_PASSWORD=my\$$FAKE"
expect_exit "bearer value beginning \$"            1 "Authorization: Bearer \$$FAKE"
expect_exit "bearer dummy word, dot, real value"   1 "Authorization: Bearer example.$FAKE"
expect_exit "a default inside \${…:-…}"            1 "PROD_PASSWORD=\"\${DB_PASSWORD:-$FAKE}\""
expect_exit "a real value after <…>"               1 "PROD_PASSWORD=\"<prod> $FAKE\""

# The other side of the same rule: every one of these is a placeholder and must stay
# one. A gate that stops on them trains its reader to click through.
printf '\nplaceholders that must still read as placeholders\n'

expect_exit "<your-key-here>"                      0 'API_KEY=<your-key-here>'
expect_exit "<YOUR_API_KEY>"                       0 'API_KEY=<YOUR_API_KEY>'
expect_exit "quoted <…> with spaces"               0 'API_KEY="<your key goes here>"'
expect_exit "unquoted <…> cut at a space"          0 'API_KEY=<your-long-key goes here>'
expect_exit "<…> in backticks with a comma"        0 'set `API_KEY=<your-key-here>`, then run it'
expect_exit "\${VAR}"                              0 'API_TOKEN=${GITHUB_TOKEN}'
expect_exit "\$VAR"                                0 'API_TOKEN=$GITHUB_TOKEN'
expect_exit "\$VAR with a digit"                   0 'API_TOKEN=$OAUTH2_CLIENT_TOKEN'
expect_exit "\${VAR:-} with an empty default"      0 'API_TOKEN="${GITHUB_TOKEN:-}"'
expect_exit "\$(command)"                          0 'API_TOKEN="$(gh auth token --hostname example)"'
expect_exit "a path under \$HOME"                  0 'SSH_KEY_FILE="$HOME/.ssh/id_rsa"'
expect_exit "{{ template }}"                       0 'api_password: "{{ vault_database_password }}"'
expect_exit "\${{ secrets.X }}"                    0 'GH_TOKEN: "${{ secrets.GITHUB_TOKEN }}"'
expect_exit "{name} in a format string"            0 'url = f"https://host/?api_token={api_token_value}"'
expect_exit "xxxxxxxx"                             0 'API_KEY=xxxxxxxx'
expect_exit "XXXXXXXXXXXX"                         0 'API_KEY=XXXXXXXXXXXX'
expect_exit "********"                             0 'PASSWORD=********'
expect_exit "a row of dots"                        0 'PASSWORD=........'
expect_exit "masked with the last four shown"      0 'API_KEY=************a1b2'
expect_exit "xxxx-xxxx-xxxx groups"                0 'LICENSE_KEY=xxxx-xxxx-xxxx-xxxx'
expect_exit "x mask with the last four shown"      0 'CARD_TOKEN=xxxxxxxxxxxx1234'
expect_exit "your-api-key-here"                    0 'API_KEY=your-api-key-here'
expect_exit "YOUR_API_KEY_HERE"                    0 'API_KEY=YOUR_API_KEY_HERE'
expect_exit "bearer \${accessToken}"               0 'Authorization: Bearer ${accessToken}'
expect_exit "bearer \$TOKEN"                       0 'Authorization: Bearer $GITHUB_TOKEN'
expect_exit "bearer YOUR_TOKEN_HERE"               0 'Authorization: Bearer YOUR_TOKEN_HERE'
expect_exit "bearer xxxxxxxxxxxx"                  0 'Authorization: Bearer xxxxxxxxxxxx'

# Each dictionary word, as the whole value and leading a phrase of plain words.
for word in your my some insert placeholder example changeme change redacted dummy fake sample todo fixme none null nil true false; do
  expect_exit "dummy word alone: $word"            0 "API_SECRET=$word"
  expect_exit "dummy word leading a phrase: $word" 0 "API_SECRET=$word-value-goes-here"
done

# --- 6. Text with NUL bytes in it -------------------------------------------------
#
# UTF-16 puts a NUL after (or before) every ASCII character, so no pattern matched and
# a token in plain sight read as clean. The same happens to a UTF-16 fragment pasted
# into a UTF-8 transcript. Files with NULs are scanned from a copy without them.
printf '\ntext with NUL bytes\n'

# $1 = le|be, $2 = text. Writes the text as UTF-16 without a byte-order mark.
utf16() {
  local order="$1" s="$2" i=0 c
  while [ "$i" -lt "${#s}" ]; do
    c="${s:$i:1}"
    if [ "$order" = le ]; then printf '%s\0' "$c"; else printf '\0%s' "$c"; fi
    i=$((i + 1))
  done
  if [ "$order" = le ]; then printf '\n\0'; else printf '\0\n'; fi
}
utf16_token="token gh""p_aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789"

utf16 le "$utf16_token" > "$TMP/utf16.txt"
"$SCAN" "$TMP/utf16.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 1 ] && pass "a token in a UTF-16LE file is found" || fail "a token in a UTF-16LE file must exit 1, got $rc"

{ printf '\376\377'; utf16 be "$utf16_token"; } > "$TMP/utf16.txt"
"$SCAN" "$TMP/utf16.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 1 ] && pass "a token in a UTF-16BE file with a byte-order mark is found" || fail "a token in a UTF-16BE file must exit 1, got $rc"

{ printf 'an ordinary UTF-8 line\n'; utf16 le "$utf16_token"; printf 'and another\n'; } > "$TMP/utf16.txt"
out="$("$SCAN" "$TMP/utf16.txt" 2>&1)"; rc=$?
[ "$rc" -eq 1 ] && pass "a UTF-16 fragment inside a UTF-8 file is found" || fail "a UTF-16 fragment in a UTF-8 file must exit 1, got $rc"
printf '%s' "$out" | grep -q "utf16.txt:2\$" && pass "and it is reported on its own line number" \
  || fail "a finding in a file with NUL bytes must keep its line number"

printf 'PROD_PASSWORD=x\0x\0x\0%s\n' "$FAKE" > "$TMP/nul.txt"
"$SCAN" "$TMP/nul.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 1 ] && pass "NUL bytes cannot assemble a placeholder prefix" || fail "a value behind NUL-separated x's must exit 1, got $rc"

printf 'an ordinary line with a stray \0 byte\nand nothing else\n' > "$TMP/nul.txt"
"$SCAN" "$TMP/nul.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 0 ] && pass "a stray NUL in clean text is still clean" || fail "a stray NUL in clean text must exit 0, got $rc"

# --- 7. What a review of sections 5 and 6 found ------------------------------------
#
# The first version of those fixes was attacked by reviewers who had not seen the
# reasoning behind it. Each case below is something they broke, or a test they showed
# could not fail.

# grep -o returns matches that do not overlap, so a name inside another match's value
# is never matched itself. When the outer value is a placeholder the inner one was
# never judged. The line is now judged again from the start of an unreported value.
printf '\na credential whose name sits inside another match\n'

PLAIN='correcthorsebatterystaple'
expect_exit "words-only secret in a quoted note"          1 "A_KEY=\"my B_PASSWORD=$PLAIN\""
expect_exit "the same, quotes escaped"                    1 "A_KEY=\\\"my B_PASSWORD=$PLAIN\\\""
expect_exit "the same, in escaped JSON"                   1 "{\\\"api_key\\\": \\\"your password=$PLAIN\\\"}"
expect_exit "hint string inside a JSON object"            1 "\"credentials\": {\"password_hint\": \"example PASSWORD=$PLAIN\"}"
expect_exit "JSON held in a JSON string"                  1 "\"credentials\": \"{\\\"password\\\": \\\"$FAKE\\\"}\""
expect_exit "JSON held in a JSON string, a level down"    1 "\\\"credentials\\\": \\\"{\\\\\\\"password\\\\\\\": \\\\\\\"$FAKE\\\\\\\"}\\\""
expect_exit "a second key after the swallowed one"        1 "\"SecretString\": \"{\\\"password\\\": \\\"$FAKE\\\", \\\"username\\\": \\\"admin\\\"}\""
expect_exit "escaped outer key, bare inner key"           1 "{\\\"credentials\\\": {password: \\\"$FAKE\\\"}}"
expect_exit "YAML flow mapping"                           1 "credentials: {password: $FAKE}"
expect_exit "object literal"                              1 "const credentials = {password: \"$FAKE\"}"
expect_exit "three names deep"                            1 "{\"secrets\": {\"credentials\": {\"password\": \"$FAKE\"}}}"
# Every level here is a placeholder holding the next, so nothing but the depth limit
# reports the deep one. The shallow one shows the same shape is clean when followed.
chain=""; i=0; while [ "$i" -lt 30 ]; do chain="${chain}A_KEY=<"; i=$((i + 1)); done
expect_exit "a chain too deep to follow is reported"      1 "${chain}changeme"
expect_exit "a short chain of placeholders is clean"      0 "A_KEY=<A_KEY=<A_KEY=<changeme"

# The same re-scan must not turn structure into findings.
expect_exit "nested counters stay clean"                  0 '"token_usage": {"prompt_tokens": 100, "completion_tokens": 20}'
expect_exit "a default in \${VAR:-…} is not an assignment" 0 'DB_PASSWORD="${DB_PASSWORD:-changeme}"'
expect_exit "a placeholder naming another key is clean"   0 'API_KEY="<copy the value of SECRET_KEY: from the console>"'
expect_exit "nested placeholders stay clean"              0 '{"secrets": {"credentials": {"password": "<redacted>"}}}'

# A closed <…> or {{…}}, or a $name, used to be removed whole before the value was
# judged, so whatever sat inside was never looked at.
printf '\na real value inside placeholder punctuation\n'

expect_exit "inside closed <…>"                           1 "PROD_PASSWORD=<$FAKE>"
expect_exit "inside {{…}}"                                1 "PROD_PASSWORD=\"{{$FAKE}}\""
expect_exit "bearer inside closed <…>"                    1 "Authorization: Bearer <$FAKE>"
expect_exit "hex after \$"                                1 'PROD_PASSWORD=$deadbeef0123456789abcdef01234567'
expect_exit "a word and a year after \$"                  1 'PROD_PASSWORD=$ummertime2024'
expect_exit "\$-separated groups"                         1 'PROD_PASSWORD=$a1b2$c3d4$e5f6$a7b8$c9d0'
expect_exit "escaped quotes around closed <…>"            1 "PROD_PASSWORD=\\\"<$FAKE>\\\""
# No digits anywhere: only the case test can catch this one.
expect_exit "mixed case with no digits"                   1 'PROD_PASSWORD=example-ZqNotARealSecretKdLmXp'

expect_exit "your-key-123"                                0 'API_KEY=your-key-123'
expect_exit "example-token-1234"                          0 'API_TOKEN=example-token-1234'
expect_exit "a path with a digit under \$HOME"            0 'KEY_PATH="$HOME/.config/app2/token"'
expect_exit "\${VAR:-default123}"                         0 'API_KEY=${API_KEY:-default123}'
expect_exit "\${camelCase2}"                              0 'PASSWORD=${databasePassword2}'
expect_exit "unclosed <paste-your-32-char-key"            0 'API_KEY=<paste-your-32-char-key'
expect_exit "<your-api-key-v2>"                           0 'API_KEY=<your-api-key-v2>'
expect_exit "escaped quotes around \$VAR"                 0 'DB_PASSWORD=\"$DB_PASSWORD\"'

# The placeholder test switches case-insensitive matching off and must switch it back
# on: the Authorization extractor and the dictionary words depend on it. Every other
# fixture is one line, so none of them could see state carried from one match to the
# next.
printf '\nstate carried from one match to the next\n'

printf 'API_KEY=<your-key-here>\nAuthorization: Bearer %s\n' "$FAKE" > "$TMP/two.txt"
"$SCAN" "$TMP/two.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 1 ] && pass "a bearer value after a placeholder is still found" || fail "a bearer value after a placeholder must exit 1, got $rc"
printf 'API_KEY=<your-key-here>\nAPI_SECRET=CHANGEME-PLEASE-NOW\n' > "$TMP/two.txt"
"$SCAN" "$TMP/two.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 0 ] && pass "an upper-case dummy word after a placeholder is still one" || fail "CHANGEME after a placeholder must exit 0, got $rc"

# Taking NULs out joins their neighbors. A file with NULs is scanned both ways.
printf '\nmore text with NUL bytes\n'

printf 'tool\0--key\0sk-%s\0--host\0x\n' "$FAKE" > "$TMP/nul.txt"
"$SCAN" "$TMP/nul.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 1 ] && pass "a key set off only by NUL bytes is found" || fail "a key between NUL bytes must exit 1, got $rc"

# The two below go through the value-checked scan; the token cases in section 6 do not.
utf16 le "PROD_PASSWORD=$FAKE" > "$TMP/utf16.txt"
"$SCAN" "$TMP/utf16.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 1 ] && pass "an assignment in a UTF-16 file is found" || fail "an assignment in a UTF-16 file must exit 1, got $rc"
utf16 be "Authorization: Bearer $FAKE" > "$TMP/utf16.txt"
"$SCAN" "$TMP/utf16.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 1 ] && pass "a bearer value in a UTF-16 file is found" || fail "a bearer value in a UTF-16 file must exit 1, got $rc"

# tr and wc are needed now, and each way they can fail must stop the scan.
printf '\ntr and wc\n'

printf 'nothing here\n' > "$TMP/plain.txt"
printf 'a stray \0 byte\n' > "$TMP/nul.txt"
for tool in tr wc; do
  NOTOOL="$TMP/no-$tool"
  mkdir -p "$NOTOOL"
  for keep in grep tr wc; do
    [ "$keep" = "$tool" ] || ln -s "$(command -v "$keep")" "$NOTOOL/$keep"
  done
  PATH="$NOTOOL" "$(command -v bash)" "$SCAN" "$TMP/plain.txt" >/dev/null 2>&1; rc=$?
  [ "$rc" -eq 2 ] && pass "no $tool on PATH exits 2" || fail "no $tool on PATH must exit 2, got $rc"
done

REAL_TR="$(command -v tr)"
printf '#!/usr/bin/env bash\nexit 1\n' > "$SHIM/tr"
chmod +x "$SHIM/tr"
PATH="$SHIM:$PATH" "$SCAN" "$TMP/plain.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "a tr that fails exits 2" || fail "a tr that fails must exit 2, got $rc"
# Works for the byte count, fails when asked for the NUL-free copy.
printf '#!/usr/bin/env bash\nif [ -e "%s/tr-called" ]; then exit 1; fi\n: > "%s/tr-called"\nexec "%s" "$@"\n' "$TMP" "$TMP" "$REAL_TR" > "$SHIM/tr"
PATH="$SHIM:$PATH" "$SCAN" "$TMP/nul.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "a tr that fails on the NUL-free copy exits 2" || fail "a tr failing on its second call must exit 2, got $rc"
rm -f "$SHIM/tr" "$TMP/tr-called"
printf '#!/usr/bin/env bash\nexit 1\n' > "$SHIM/wc"
chmod +x "$SHIM/wc"
PATH="$SHIM:$PATH" "$SCAN" "$TMP/nul.txt" >/dev/null 2>&1; rc=$?
[ "$rc" -eq 2 ] && pass "a wc that fails exits 2" || fail "a wc that fails must exit 2, got $rc"
rm -f "$SHIM/wc"

# Long values. Each of these took from 20 seconds to several minutes, which a caller
# reads as a hung gate. The bound is loose on purpose: they finish in about a second.
printf '\nlong values finish\n'

pad="$(head -c 200000 /dev/zero | tr '\0' ' ')"
masks=""; i=0; while [ "$i" -lt 8000 ]; do masks="${masks}xxx "; i=$((i + 1)); done
for target in "8000 masks in one value:0:NOTE_KEY=\"$masks\"" \
              "200 KB of spaces before the value:1:PROD_PASSWORD=\"$pad$FAKE\"" \
              "200 KB of spaces after the value:1:PROD_PASSWORD=\"$FAKE$pad\""; do
  name="${target%%:*}"; rest="${target#*:}"; want="${rest%%:*}"
  printf '%s\n' "${rest#*:}" > "$TMP/long.txt"
  started=$SECONDS
  "$SCAN" "$TMP/long.txt" >/dev/null 2>&1; rc=$?
  took=$((SECONDS - started))
  if [ "$rc" -eq "$want" ] && [ "$took" -lt 30 ]; then
    pass "$name"
  else
    fail "$name (wanted exit $want in under 30 s, got $rc in $took s)"
  fi
done

# --- result -----------------------------------------------------------------------

printf '\n'
printf '%d passed, %d failed, %d skipped.\n' "$passes" "$failures" "$skips"
[ "$failures" -eq 0 ] && exit 0
exit 1
