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
#   2  the scan could not run (bad usage, unreadable file, grep, tr or wc missing,
#      bad pattern, a command that failed, or matches that could not be read back)
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
#      could follow the marker. PASSWORD=$Zq7…, PASSWORD=<Zq7…>, PASSWORD=xxxZq7…,
#      PASSWORD=example-Zq7… and a quoted note that merely opened with <see below>
#      before a real assignment all read as clean.
#
#   2. Nothing in it looks like a credential. It must have fewer than 8 letters and
#      digits — not counting x's when it holds a run of three or more, so that
#      xxxxxxxx1234 is still a mask — or
#      be WORDLIKE: every run of letters and digits is a plain word — lower, UPPER,
#      Capitalized or camelCase, with at most three digits after it — or a number of
#      at most four digits. your-api-key-here, <YOUR_API_KEY_2>, $HOME/.ssh/id_rsa and
#      ${process.env.accessToken} are; a random key changes case mid-run or mixes
#      digits through its letters, so it is not, wherever it sits: after the marker,
#      inside <…> or {{…}}, or as the default in ${VAR:-…}.
#
# Rule 2 is only applied to a value rule 1 accepted, so on its own it only turns
# placeholders into findings. Known limits, all of which rule 1 had too: a secret of
# plain words behind a placeholder opening (none:correcthorsebattery), and one under
# 8 letters and digits (<x>hunter2).

readonly PLACEHOLDER_LEAD='[<{$]|x{3,}|X{3,}|\*{3,}|\.\.\.'
readonly PLACEHOLDER_WORD='your|my|some|insert|placeholder|example|changeme|change|redacted|dummy|fake|sample|todo|fixme|none|null|nil|true|false'
readonly MASK_RUN='x{3,}|X{3,}'
# Eight letters and digits anywhere in the value; and the same not counting x.
readonly EIGHT_ALNUM='([A-Za-z0-9][^A-Za-z0-9]*){8}'
readonly EIGHT_ALNUM_NOT_X='([A-WYZa-wyz0-9]([^A-Za-z0-9]|[xX])*){8}'
readonly WORDLIKE_SEG='(([A-Z]+|[A-Z]?[a-z]+([A-Z][a-z]+)*)[0-9]{0,3}|[0-9]{1,4})'
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
# CRED_WORD is the part of a name that makes it a credential's. It is also how
# judge() below tells that a value has another assignment inside it.
readonly CRED_WORD='(KEY|TOKEN|SECRET|PASSWORD|PASSWD|PASSPHRASE|CREDENTIAL)'
readonly ASSIGN_LABEL="credential assignment with a real value"
readonly ASSIGN_RE='[A-Za-z0-9_.-]*'"$CRED_WORD"'[A-Za-z0-9_.-]*\\*["'"'"']?[[:space:]]*[:=][[:space:]]*(\\*"[^"]*"|\\*'"'"'[^'"'"']*'"'"'|[^[:space:],;}]+)'
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
# Anchored regexes for the trims in value_of_assignment. Each takes a whole run in
# one match: one character per pass, and ${v##*[! ]}, are both quadratic, and a value
# padded with 200 KB of spaces took minutes.
readonly RE_LEAD_WS='^[[:space:]]+'
readonly RE_LEAD_BS='^\\+'
readonly RE_BODY_WS='^(.*[^[:space:]])?[[:space:]]*$'
readonly RE_BODY_BS='^(.*[^\\])?\\*$'

value_of_assignment() {
  local v="$1" q
  v="${v#*[:=]}"
  [[ "$v" =~ $RE_LEAD_WS ]] && v="${v:${#BASH_REMATCH[0]}}"
  # The opening quote with any backslashes escaping it, then the closing one likewise.
  q="$v"
  [[ "$q" =~ $RE_LEAD_BS ]] && q="${q:${#BASH_REMATCH[0]}}"
  [ "$q" != "${q#[\"\']}" ] && v="${q#[\"\']}"
  if [ "$v" != "${v%[\"\']}" ]; then
    v="${v%[\"\']}"
    [[ "$v" =~ $RE_BODY_BS ]] && v="${BASH_REMATCH[1]-}"
  fi
  # Whitespace inside the quotes is not part of the value, and is not a placeholder:
  # KEY=" realsecret" used to be dropped for its leading space.
  [[ "$v" =~ $RE_LEAD_WS ]] && v="${v:${#BASH_REMATCH[0]}}"
  [[ "$v" =~ $RE_BODY_WS ]] && v="${BASH_REMATCH[1]-}"
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
# label and path strings, which case-insensitivity does not affect. The rules
# themselves are stated above PLACEHOLDER_LEAD.
is_placeholder() {
  local v="$1" enough
  # Rule 1: starts like a placeholder. Case-insensitive, for the dictionary words.
  [[ "$v" =~ ^($PLACEHOLDER_LEAD) ]] || [[ "$v" =~ ^($PLACEHOLDER_WORD)([^A-Za-z0-9]|$) ]] || return 1
  # Rule 2: nothing in it looks like a credential. Case is the whole distinction
  # here, so nocasematch is off until every return — and must come back on: the
  # Authorization extractor and the dictionary test above both depend on it.
  shopt -u nocasematch
  # Regex tests only. Stripping characters with ${v//…/} is quadratic in bash 3.2 —
  # five minutes on a 32 KB value — and a loop that removed masks one at a time was
  # no better.
  enough="$EIGHT_ALNUM"
  [[ "$v" =~ $MASK_RUN ]] && enough="$EIGHT_ALNUM_NOT_X"
  if ! [[ "$v" =~ $enough ]] || [[ "$v" =~ $WORDLIKE_RE ]]; then
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
#   - Check every grep's status, including the per-line -o pass in judge(). If -o
#     finds nothing on a line the first pass matched, report the line.
#   - Feed the loop with `done < <(printf ...)`. A here-document can need a temp file,
#     and `printf ... | while` puts die() in a subshell.
#   - Set a flag inside the loop and call must_have_read after it.

must_have_read() {
  [ "$1" -eq 1 ] || die "matches were found in $2 but could not be read back while scanning for: $3"
}

# $NAME and ${NAME with the name blanked out, into BLANKED. A reference is not an
# assignment: without this, the re-scan in judge() reads "${DB_PASSWORD:-changeme}"
# as DB_PASSWORD, a separator, and a value.
BLANKED=""
blank_references() {
  local rest="$1" kept="" m before
  while [[ "$rest" =~ \$\{?[A-Za-z_][A-Za-z0-9_]* ]]; do
    m="${BASH_REMATCH[0]}"
    before="${rest%%"$m"*}"
    kept="$kept$before "
    rest="${rest:$(( ${#before} + ${#m} ))}"
  done
  BLANKED="$kept$rest"
}

# Does $1 (a line, or what is left of one) carry a real value? Answers in JUDGED:
# 0 yes, 1 no, 2 the -o pass found nothing at all.
#
# EVERY match is judged, not just the first. Checking only the first and skipping the
# line on its verdict is fail-open: `DEBUG_SECRET=todo PROD_PASSWORD=Tr0ub4dor3xyz`
# discarded the whole line because the leading match was a placeholder.
#
# A match that is not reported can still be hiding one. grep -o hands back matches
# that do not overlap, so a name inside another match's value is never matched itself:
#   "credentials": {"password": "…"}      the value is {"password": and stops there
#   NOTE_KEY="example PROD_PASSWORD=…"    the value is the whole quoted note
# In both the outer value is a placeholder and the real one was never looked at. So
# when an unreported value contains a credential word, the line is judged again from
# the start of that value. On that second look only the first match is new — the rest
# are the outer loop's — which keeps this a chain, one step per nested name, and a
# chain deeper than 20 is reported rather than followed.
#
# Called as a plain command, and it calls itself: die() must reach the main shell.
JUDGED=1
judge() {
  local text="$1" file="$2" lineno="$3" label="$4" re="$5" value_fn="$6" depth="$7"
  local matches rc m vp before read_inner verdict=1

  matches="$(printf '%s' "$text" | grep -a -o -i -E -e "$re")"
  rc=$?
  [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file line $lineno for: $label"
  if [ -z "$matches" ]; then
    JUDGED=2
    return 0
  fi
  read_inner=0
  while IFS= read -r m; do
    read_inner=1
    [ -z "$m" ] && continue
    "$value_fn" "$m"
    if [ -n "$EXTRACTED" ] && ! is_placeholder "$EXTRACTED"; then
      verdict=0
      break
    fi
    vp="${m#*[:=]}"
    if [[ "$vp" =~ $CRED_WORD ]]; then
      if [ "$depth" -ge 20 ]; then
        verdict=0
        break
      fi
      blank_references "$vp"
      # What follows this match on the line, by offset: ${text#*"$m"} is slow on a
      # long line, and very slow in bash 3.2.
      before="${text%%"$m"*}"
      judge "$BLANKED${text:$(( ${#before} + ${#m} ))}" "$file" "$lineno" "$label" "$re" "$value_fn" "$((depth + 1))"
      if [ "$JUDGED" -eq 0 ]; then
        verdict=0
        break
      fi
    fi
    [ "$depth" -gt 0 ] && break
  done < <(printf '%s\n' "$matches")
  must_have_read "$read_inner" "$file" "$label"
  JUDGED="$verdict"
}

# The two value-checked scans: find the shape, then reject placeholder values. $4 names
# the function that pulls the value out of one match. Call this as a plain command,
# never through $( ) or a pipe — it must be able to die().
scan_valued() {
  local file="$1" label="$2" re="$3" value_fn="$4" out more rc line lineno text read_any

  out="$(grep -a -n -i -E -e "$re" -- "$file")"
  rc=$?
  [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file for: $label"
  if [ "$HAS_NUL" -eq 1 ]; then
    more="$(printf '%s\n' "$STRIPPED" | grep -a -n -i -E -e "$re")"
    rc=$?
    [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file without its NUL bytes for: $label"
    [ -n "$more" ] && out="${out:+$out$NEWLINE}$more"
  fi
  [ -z "$out" ] && return 0

  read_any=0
  while IFS= read -r line; do
    read_any=1
    [ -z "$line" ] && continue
    lineno="${line%%:*}"
    text="${line#*:}"
    judge "$text" "$file" "$lineno" "$label" "$re" "$value_fn" 0
    # 2: the first pass matched this line and the -o pass found nothing on it. A value
    # that could not be extracted cannot be shown to be a placeholder.
    case "$JUDGED" in
      0|2) report "$label" "$file" "$lineno" "$text" ;;
    esac
  done < <(printf '%s\n' "$out")
  must_have_read "$read_any" "$file" "$label"
}

# NUL bytes. grep -a treats NUL as one more character, so text with NULs through it
# matches nothing: a whole UTF-16 file, or a UTF-16 fragment pasted into a UTF-8
# transcript (both occur), read as clean with a token in plain sight. A file that has
# any is therefore scanned twice: as it is, and from a copy with the NULs taken out,
# held in a variable — no temp file — and fed to grep on stdin. Both, because taking
# a NUL out joins its neighbors, and a NUL can be the only thing separating a token
# from the text before it. Line numbers are the same in both. The copy is made by a
# plain assignment so that a tr that fails is seen and stops the scan.
readonly NEWLINE='
'
HAS_NUL=0
STRIPPED=""

scan_file() {
  local file="$1" i label re out more rc line lineno text read_any bytes kept

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

    out="$(grep -a -n -E -e "$re" -- "$file")"
    rc=$?
    [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file for: $label"
    if [ "$HAS_NUL" -eq 1 ]; then
      more="$(printf '%s\n' "$STRIPPED" | grep -a -n -E -e "$re")"
      rc=$?
      [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file without its NUL bytes for: $label"
      [ -n "$more" ] && out="${out:+$out$NEWLINE}$more"
    fi

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
