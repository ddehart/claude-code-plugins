#!/usr/bin/env bash
#
# scan-secrets.sh — the deterministic floor of the preserve stage's redaction gate.
#
# Scans rendered raw material for credential shapes before it is archived into a
# destination that is public or shared. It is deliberately dumb: fixed patterns, no
# judgment, testable against a planted secret. The agent read-through that runs
# alongside it covers what patterns cannot catch (names, personal details, unreleased
# plans); neither half is adequate alone.
#
# Usage:
#   scan-secrets.sh <file> [<file>...]
#
# Exit codes:
#   0  clean — no credential shapes found
#   1  hits  — at least one finding, listed on stdout
#   2  the scan could not run (bad usage, unreadable file,
#      missing grep, bad pattern, a grep that failed, or matches that could not be
#      read back)
#
# Exit 1 and exit 2 mean the same thing to the caller: do not archive. The preserve
# stage fails closed on any non-zero exit. A scan that cannot run is not a pass, and
# that has to hold for a failure discovered *during* scanning, not only for one caught
# before it starts — see "Failing closed" below.

set -uo pipefail
shopt -s nocasematch

# C locale: every byte is a character. In UTF-8 an invalid byte matches no bracket
# expression and ends a value early. Patterns are ASCII.
export LC_ALL=C

readonly EXIT_CLEAN=0
readonly EXIT_HITS=1
readonly EXIT_ERROR=2

die() {
  printf 'scan-secrets: %s\n' "$1" >&2
  exit "$EXIT_ERROR"
}

# --- preflight -------------------------------------------------------------------

for tool in grep tr wc; do
  command -v "$tool" >/dev/null 2>&1 || die "$tool not found on PATH; cannot scan"
done

if [ "$#" -eq 0 ]; then
  printf 'usage: scan-secrets.sh <file> [<file>...]\n' >&2
  exit "$EXIT_ERROR"
fi

for f in "$@"; do
  [ -e "$f" ] || die "no such file: $f"
  [ -f "$f" ] || die "not a regular file: $f"
  [ -r "$f" ] || die "cannot read: $f"
done

# --- what counts as a placeholder ------------------------------------------------
#
# A bracketed value (<your-key-here>), a shell or template reference ($VAR, ${VAR},
# {{var}}), a masked value (xxxx, ****), or a well-known dummy word is not a
# credential, and a gate that stops on those trains its reader to click through.
#
# Quote characters are deliberately NOT a placeholder marker. They were, and it
# inverted the gate: the value extracted from KEY="realsecret" begins with a quote,
# matched the placeholder test, and was dropped — so quoting a credential made it
# invisible, which is how most secrets are actually written. Quotes are stripped from
# the value before this test instead. Both halves are load-bearing; keep both.
#
# A value is a placeholder only if BOTH of these hold.
#
#   1. It starts like one: a structural marker (PLACEHOLDER_LEAD) or a dictionary word
#      (PLACEHOLDER_WORD) that is the whole value or is followed by a non-alphanumeric
#      character. This was once the entire test, and it is a hole on its own: anything
#      could follow the marker. PASSWORD=$Zq7…, PASSWORD=<Zq7…, PASSWORD=xxxZq7…,
#      PASSWORD=example-Zq7… and a quoted note that merely opened with <see below>
#      before a real assignment all read as clean.
#
#   2. Nothing credential-like is left once the placeholder structure is taken out.
#      Remove every PLACEHOLDER_UNIT (a closed <…> or {{…}}, a $NAME / ${NAME} / {name}
#      reference whose name is one case throughout, a run of x, * or dots). What
#      remains must have fewer than 8 letters and digits (the same floor a bare value
#      gets), or be WORDLIKE: no digits, and every run of letters is a plain word —
#      lower, UPPER, Capitalized or camelCase — as in your-api-key-here,
#      $HOME/.ssh/id_rsa or ${process.env.accessToken}. A random key has digits or
#      changes case mid-run, so it fails this and is reported.
#
# Rule 2 only ever narrows rule 1, so nothing that was reported before goes quiet.
# What it costs is at the edge: a placeholder with a digit in its tail
# (your-key-123, ${HOME}/app2/key) is now a finding to accept by hand.

readonly PLACEHOLDER_LEAD='[<{$]|x{3,}|X{3,}|\*{3,}|\.\.\.'
readonly PLACEHOLDER_WORD='your|my|some|insert|placeholder|example|changeme|change|redacted|dummy|fake|sample|todo|fixme|none|null|nil|true|false'
readonly PLACEHOLDER_UNIT='<[^<>]*>|\{\{[^{}]*\}\}|(\$\{?|\{)([A-Z_][A-Z0-9_]*|[a-z_][a-z0-9_]*)\}?|\$[0-9@*#?!]|x{3,}|X{3,}|\*{3,}|\.{3,}'
readonly WORDLIKE_SEG='([A-Z]+|[A-Z]?[a-z]+([A-Z][a-z]+)*)'
readonly WORDLIKE_RE="^[^A-Za-z0-9]*(${WORDLIKE_SEG}[^A-Za-z0-9]+)*${WORDLIKE_SEG}?\$"

# --- patterns --------------------------------------------------------------------
#
# Parallel arrays rather than a delimited string: every regex here contains "|" as
# alternation, so any single-character field delimiter collides with the data.
#
# Ordered most-specific first, which is the order labels appear in a finding when one
# line carries more than one shape (see report()).

LABELS=()
REGEXES=()

# Fixed-format patterns only; all are case-sensitive by construction (a token prefix
# has a fixed case). The two value-checked patterns below need -i and are scanned
# separately, so there is no per-pattern flag here to get out of step with reality.
add_pattern() { LABELS+=("$1"); REGEXES+=("$2"); }

add_pattern "private key block" '-----BEGIN( [A-Z0-9]+)* PRIVATE KEY-----'
add_pattern "Anthropic API key (sk-ant-)" 'sk-ant-[A-Za-z0-9_-]{16,}'
add_pattern "GitHub token (ghp_/gho_/ghs_/ghu_)" 'gh[pousr]_[A-Za-z0-9]{20,}'
add_pattern "GitHub fine-grained PAT" 'github_pat_[A-Za-z0-9_]{20,}'
add_pattern "Slack token (xox*)" 'xox[baprs]-[A-Za-z0-9-]{10,}'
add_pattern "AWS access key id (AKIA)" 'AKIA[0-9A-Z]{16}'
add_pattern "Google API key (AIza)" 'AIza[A-Za-z0-9_-]{35}'
add_pattern "Stripe key (sk_live/rk_live)" '[sr]k_(live|test)_[A-Za-z0-9]{16,}'
# Hyphens allowed after sk-: current OpenAI keys are sk-proj-… and sk-svcacct-….
add_pattern "OpenAI-style API key (sk-)" '(^|[^A-Za-z0-9_-])sk-[A-Za-z0-9_-]{20,}'
add_pattern "JWT" 'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'
add_pattern "connection string carrying a password" '[a-zA-Z][a-zA-Z0-9+.-]*://[^[:space:]/:@"]+:[^[:space:]/:@"]+@[^[:space:]/"]+'

# These two carry a value that has to be checked against the placeholder rules, so
# they are scanned separately below rather than from the arrays above.
#
# Both are case-insensitive, and both tolerate a quote between the name and the
# separator, and any number of backslashes before each quote, because the material
# being scanned is rendered from JSON that itself contains JSON: a credential appears
# as "API_KEY": "…" or {\"API_KEY\": \"…\"} far more often than as API_KEY=….
#
# An unquoted value may not open with a brace followed by a quote, a backslash or
# nothing. That is a JSON object, and matching it as a value consumed the next key:
# in "credentials": {"password": "…"} the match ended at "password": and the real
# value after it was never looked at. With the object refused, the inner key matches
# on its own.
readonly ASSIGN_LABEL="credential assignment with a real value"
readonly ASSIGN_RE='[A-Za-z0-9_.-]*(KEY|TOKEN|SECRET|PASSWORD|PASSWD|PASSPHRASE|CREDENTIAL)[A-Za-z0-9_.-]*\\*["'"'"']?[[:space:]]*[:=][[:space:]]*(\\*"[^"]*"|\\*'"'"'[^'"'"']*'"'"'|([^[:space:],;}{]|\{[^[:space:],;}"'"'"'\\])[^[:space:],;}]*)'
readonly AUTH_LABEL="Authorization header with a bearer value"
readonly AUTH_RE='authorization\\*["'"'"']?[[:space:]]*[:=][[:space:]]*\\*["'"'"']?(bearer|basic|token)[[:space:]]+[^[:space:]"'"'"',;}]{8,}'

# --- scan ------------------------------------------------------------------------

# Findings accumulate as three parallel arrays keyed on "<file>:<lineno>" — bash 3.2
# (the macOS system shell) has no associative arrays.
#
# One finding per LINE, carrying EVERY shape found on it. Reporting one line once keeps
# the report resolvable under D7, since a reader redacts or withholds a line as a unit.
# Carrying every label is the other half, and it is not cosmetic: a line holding a
# GitHub token and a Slack token reported under one label, with a context window that
# may not even show the labelled one, cannot be resolved correctly from the report —
# you redact what you can see and leave the reported secret in place.
F_KEYS=()
F_LABELS=()
F_TEXTS=()

# Index of an already-recorded line, printed on stdout; non-zero if absent.
find_finding() {
  local key="$1" i=0
  while [ "$i" -lt "${#F_KEYS[@]}" ]; do
    if [ "${F_KEYS[$i]}" = "$key" ]; then printf '%s' "$i"; return 0; fi
    i=$((i + 1))
  done
  return 1
}

report() {
  local label="$1" file="$2" lineno="$3" text="$4" key idx
  key="${file}:${lineno}"
  if idx="$(find_finding "$key")"; then
    case "; ${F_LABELS[$idx]}; " in
      *"; $label; "*) ;;                                    # already noted on this line
      *) F_LABELS[$idx]="${F_LABELS[$idx]}; $label" ;;
    esac
  else
    F_KEYS+=("$key")
    F_LABELS+=("$label")
    F_TEXTS+=("$text")
  fi
}

# Strip the assignment's name and separator, then the surrounding quotes, leaving the
# value. A QUOTED value is captured whole by ASSIGN_RE, delimiters and spaces included:
# truncating at the first comma or space and then applying the 8-character floor below
# discarded real credentials — PASSPHRASE="correct horse battery staple" measured as
# "correct" and was dropped, while the keyword list advertises a shape that by
# definition contains spaces.
# Sets EXTRACTED rather than printing, and uses parameter expansion rather than sed.
# Both are for speed, and the speed is not cosmetic: this runs once per match, and a
# rendered transcript is one enormous JSON line after another. The printf|sed form cost
# three subshells per match and took nine minutes on a 4.5 MB transcript — long enough
# that a preserve stage would start looking hung.
#
# Both value_of_* functions set EXTRACTED; "" means "not a credential".
EXTRACTED=""
value_of_assignment() {
  local v="$1"
  v="${v#*[:=]}"
  while [ "$v" != "${v#[[:space:]]}" ]; do v="${v#[[:space:]]}"; done
  # The opening quote with any backslashes escaping it, then the closing one likewise.
  local q="$v"
  while [ "$q" != "${q#\\}" ]; do q="${q#\\}"; done
  [ "$q" != "${q#[\"\']}" ] && v="${q#[\"\']}"
  if [ "$v" != "${v%[\"\']}" ]; then
    v="${v%[\"\']}"
    while [ "$v" != "${v%\\}" ]; do v="${v%\\}"; done
  fi
  # Whitespace inside the quotes is not part of the value, and is not a placeholder:
  # KEY=" realsecret" used to be dropped for its leading space.
  while [ "$v" != "${v#[[:space:]]}" ]; do v="${v#[[:space:]]}"; done
  while [ "$v" != "${v%[[:space:]]}" ]; do v="${v%[[:space:]]}"; done
  # A value shorter than 8 characters is not a credential worth stopping a run over.
  [ "${#v}" -lt 8 ] && v=""
  EXTRACTED="$v"
}

# Bash's own =~ rather than sed's s///I. The I flag is a GNU extension; it happens to
# work on the macOS sed this was written against, but the failure it would cause
# elsewhere is the shape this file exists to avoid — sed errors, the command
# substitution yields nothing, and the empty-value guard drops a real finding with no
# error and no non-zero exit. nocasematch is already set.
value_of_authorization() {
  EXTRACTED=""
  [[ "$1" =~ (bearer|basic|token)[[:space:]]+(.*) ]] && EXTRACTED="${BASH_REMATCH[2]}"
  EXTRACTED="${EXTRACTED#[\"\']}"
  # The backslash of an escaped closing quote: Bearer <your-token>\" in nested JSON.
  while [ "$EXTRACTED" != "${EXTRACTED%\\}" ]; do EXTRACTED="${EXTRACTED%\\}"; done
}

# Bash's own =~ instead of a grep subshell, for the same reason as value_of_assignment.
# nocasematch is set once at the top; the case statements elsewhere compare fixed
# label and path strings, which case-insensitivity does not affect. The rules
# themselves are stated above PLACEHOLDER_LEAD.
is_placeholder() {
  local v="$1" m alnum
  # Rule 1: starts like a placeholder. Case-insensitive, for the dictionary words.
  [[ "$v" =~ ^($PLACEHOLDER_LEAD) ]] || [[ "$v" =~ ^($PLACEHOLDER_WORD)([^A-Za-z0-9]|$) ]] || return 1
  # Rule 2: nothing credential-like left over. Case matters here — one-case names and
  # plain words are the whole distinction — so nocasematch is off until every return.
  shopt -u nocasematch
  while [[ "$v" =~ $PLACEHOLDER_UNIT ]]; do
    m="${BASH_REMATCH[0]}"
    v="${v%%"$m"*} ${v#*"$m"}"
  done
  alnum="${v//[^A-Za-z0-9]/}"
  if [ "${#alnum}" -lt 8 ] || [[ "$v" =~ $WORDLIKE_RE ]]; then
    shopt -s nocasematch
    return 0
  fi
  shopt -s nocasematch
  return 1
}

# --- Failing closed --------------------------------------------------------------
#
# grep exits 0 on a match, 1 on no match, and >1 on its own failure — a malformed
# regex, an unreadable file, a pattern eaten as an option.
#
# That third case MUST stop the scan, and making it do so is subtler than it looks.
# The obvious factoring — a grep_lines() helper called as out="$(grep_lines …)" — is
# broken: the helper runs inside a command substitution, so its `exit 2` terminates
# only that subshell. The caller keeps going with an empty result, reads it as "no
# match", and a pattern that never ran degrades to a clean pass with the secret still
# in the file. That is the precise failure this gate exists to prevent, so the grep
# and its status check are inlined in the main shell below, where die() can actually
# stop the process. Do not refactor them into a function invoked via $( ).
#
# Three rules for any loop over grep output:
#   - Check every grep's status, including the per-line -o pass. If -o finds nothing
#     on a line the first pass matched, report the line.
#   - Feed the loop with `done < <(printf ...)`. A here-document can need a temp file,
#     and `printf ... | while` puts die() in a subshell.
#   - Set a flag inside the loop and call must_have_read after it.

must_have_read() {
  [ "$1" -eq 1 ] || die "matches were found in $2 but could not be read back while scanning for: $3"
}

# The two value-checked scans: find the shape, then reject placeholder values. $4 names
# the function that pulls the value out of one match. Call this as a plain command,
# never through $( ) or a pipe — it must be able to die().
scan_valued() {
  local file="$1" label="$2" re="$3" value_fn="$4" out rc line lineno text matches m read_any read_inner

  if [ "$HAS_NUL" -eq 1 ]; then
    out="$(printf '%s\n' "$STRIPPED" | grep -a -n -i -E -e "$re")"
  else
    out="$(grep -a -n -i -E -e "$re" -- "$file")"
  fi
  rc=$?
  [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file for: $label"
  [ -z "$out" ] && return 0

  read_any=0
  while IFS= read -r line; do
    read_any=1
    [ -z "$line" ] && continue
    lineno="${line%%:*}"
    text="${line#*:}"
    # EVERY match on the line, not just the first. Checking only the first and skipping
    # the line on its verdict is fail-open: `DEBUG_SECRET=todo
    # PROD_PASSWORD=Tr0ub4dor3xyz` discarded the whole line because the leading match
    # was a placeholder, and reported clean with a real credential still in it.
    matches="$(printf '%s' "$text" | grep -a -o -i -E -e "$re")"
    rc=$?
    [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file line $lineno for: $label"
    if [ -z "$matches" ]; then
      report "$label" "$file" "$lineno" "$text"
      continue
    fi
    read_inner=0
    while IFS= read -r m; do
      read_inner=1
      [ -z "$m" ] && continue
      "$value_fn" "$m"
      [ -z "$EXTRACTED" ] && continue
      is_placeholder "$EXTRACTED" && continue
      report "$label" "$file" "$lineno" "$text"
      break
    done < <(printf '%s\n' "$matches")
    must_have_read "$read_inner" "$file" "$label"
  done < <(printf '%s\n' "$out")
  must_have_read "$read_any" "$file" "$label"
}

# NUL bytes. grep -a treats NUL as one more character, so text with NULs through it
# matches nothing: a whole UTF-16 file, or a UTF-16 fragment pasted into a UTF-8
# transcript (both occur), read as clean with a token in plain sight. A file that has
# any is therefore scanned from a copy with the NULs taken out, held in a variable —
# no temp file — and fed to grep on stdin. Line numbers are unchanged. The copy is
# made by a plain assignment so that a tr that fails is seen and stops the scan.
HAS_NUL=0
STRIPPED=""

scan_file() {
  local file="$1" i label re out rc line lineno text read_any bytes kept

  HAS_NUL=0
  STRIPPED=""
  bytes="$(wc -c < "$file")" && kept="$(tr -d '\000' < "$file" | wc -c)" && [ "$bytes" -ge "$kept" ] 2>/dev/null \
    || die "could not count the bytes in $file"
  if [ "$bytes" -ne "$kept" ]; then
    STRIPPED="$(tr -d '\000' < "$file")" || die "could not read $file past its NUL bytes"
    HAS_NUL=1
  fi

  i=0
  while [ "$i" -lt "${#REGEXES[@]}" ]; do
    label="${LABELS[$i]}"
    re="${REGEXES[$i]}"
    i=$((i + 1))

    if [ "$HAS_NUL" -eq 1 ]; then
      out="$(printf '%s\n' "$STRIPPED" | grep -a -n -E -e "$re")"
    else
      out="$(grep -a -n -E -e "$re" -- "$file")"
    fi
    rc=$?
    [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file for: $label"

    [ -z "$out" ] && continue
    read_any=0
    while IFS= read -r line; do
      read_any=1
      [ -z "$line" ] && continue
      lineno="${line%%:*}"
      text="${line#*:}"
      report "$label" "$file" "$lineno" "$text"
    done < <(printf '%s\n' "$out")
    must_have_read "$read_any" "$file" "$label"
  done

  scan_valued "$file" "$ASSIGN_LABEL" "$ASSIGN_RE" value_of_assignment
  scan_valued "$file" "$AUTH_LABEL" "$AUTH_RE" value_of_authorization

  return 0
}

printf 'scan-secrets: scanning %d file(s)\n' "$#"

for f in "$@"; do
  scan_file "$f"
done

if [ "${#F_KEYS[@]}" -eq 0 ]; then
  printf '\nscan-secrets: clean — no credential shapes found.\n'
  exit "$EXIT_CLEAN"
fi

i=0
while [ "$i" -lt "${#F_KEYS[@]}" ]; do
  printf '\n[%d] %s\n' "$((i + 1))" "${F_LABELS[$i]}"
  printf '    %s\n' "${F_KEYS[$i]}"
  # Truncated so one long transcript line does not flood the report; the file:line
  # reference is what a reader follows to see the rest.
  printf '    > %.200s\n' "${F_TEXTS[$i]}"
  i=$((i + 1))
done

printf '\nscan-secrets: %d finding(s). Resolve each one individually — redact, withhold, or accept as a false positive — before anything is archived.\n' "${#F_KEYS[@]}"
exit "$EXIT_HITS"
