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
#   2  the scan could not run (bad usage, unreadable file, missing grep, bad pattern,
#      a grep that failed, or matches that could not be read back)
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

command -v grep >/dev/null 2>&1 || die "grep not found on PATH; cannot scan"

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
# {{var}}), or a well-known dummy word is not a credential, and a gate that stops on
# those trains its reader to click through.
#
# Quote characters are deliberately NOT in this list. They were, and it inverted the
# gate: the value extracted from KEY="realsecret" begins with a quote, matched the
# placeholder test, and was dropped — so quoting a credential made it invisible, which
# is how most secrets are actually written in .env, YAML, JSON, and source. Quotes are
# stripped from the value before this test instead.
#
# Both halves are load-bearing on purpose and either one alone prevents the defect, so
# removing the "redundant" one looks safe and passes the suite. Keep both.
#
# TWO GROUPS, matched differently, and the difference is the whole point.
#
#   LEAD  — structural markers. A value that *begins* with one is a placeholder however
#           it continues: <your-key-here>, ${VAR}, xxxx, ***, ….
#   WORD  — dictionary words. These must be the WHOLE value, or be followed by a
#           non-alphanumeric character. Matching them as a prefix is a hole: a real
#           credential that happens to start with one is silently suppressed, and
#           "starts with a common English word" is not rare in a random key.
#           API_KEY=nullXk29LpQr7Wm3Zt8Vc1Bh6Ny4 read as clean under the prefix form,
#           as did values beginning true…, nil…, fake…, none…. Same shape as the two
#           defects already fixed here: a legitimate value defeating the heuristic
#           because the check was looser than the thing it was checking for.

readonly PLACEHOLDER_LEAD='[<{$[:space:]]|x{3,}|X{3,}|\*{3,}|\.\.\.'
readonly PLACEHOLDER_WORD='your|my|some|insert|placeholder|example|changeme|change|redacted|dummy|fake|sample|todo|fixme|none|null|nil|true|false'

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

# These two carry a value that has to be checked against the placeholder groups, so
# they are scanned separately below rather than from the arrays above.
#
# Both are case-insensitive and both tolerate a quote between the name and the
# separator, because the material being scanned is rendered from JSON: a credential
# appears as "ANTHROPIC_API_KEY": "…" far more often than as ANTHROPIC_API_KEY=….
readonly ASSIGN_LABEL="credential assignment with a real value"
readonly ASSIGN_RE='[A-Za-z0-9_.-]*(KEY|TOKEN|SECRET|PASSWORD|PASSWD|PASSPHRASE|CREDENTIAL)[A-Za-z0-9_.-]*["'"'"']?[[:space:]]*[:=][[:space:]]*("[^"]*"|'"'"'[^'"'"']*'"'"'|[^[:space:],;}]+)'
readonly AUTH_LABEL="Authorization header with a bearer value"
readonly AUTH_RE='authorization["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"']?(bearer|basic|token)[[:space:]]+[^[:space:]"'"'"',;}]{8,}'

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
  v="${v#[\"\']}"
  v="${v%[\"\']}"
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
}

# Bash's own =~ instead of a grep subshell, for the same reason as value_of_assignment.
# nocasematch is set once at the top; the case statements elsewhere compare fixed
# label and path strings, which case-insensitivity does not affect.
is_placeholder() {
  [[ "$1" =~ ^($PLACEHOLDER_LEAD) ]] && return 0
  # Whole value, or the word followed by a separator (changeme, change-me, your-key…) —
  # never merely a prefix of a longer alphanumeric run.
  [[ "$1" =~ ^($PLACEHOLDER_WORD)([^A-Za-z0-9]|$) ]] && return 0
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

  out="$(grep -a -n -i -E -e "$re" -- "$file")"
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

scan_file() {
  local file="$1" i label re out rc line lineno text read_any

  i=0
  while [ "$i" -lt "${#REGEXES[@]}" ]; do
    label="${LABELS[$i]}"
    re="${REGEXES[$i]}"
    i=$((i + 1))

    out="$(grep -a -n -E -e "$re" -- "$file")"
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
