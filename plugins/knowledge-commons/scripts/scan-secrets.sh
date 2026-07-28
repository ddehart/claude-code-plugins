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
#   2  the scan could not run (bad usage, unreadable file, missing grep, bad pattern)
#
# Exit 1 and exit 2 mean the same thing to the caller: do not archive. The preserve
# stage fails closed on any non-zero exit. A scan that cannot run is not a pass, and
# that has to hold for a failure discovered *during* scanning, not only for one caught
# before it starts — see "Failing closed" below.

set -uo pipefail

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

readonly PLACEHOLDER='([<{$[:space:]]|x{3,}|X{3,}|\*{3,}|\.\.\.|your[-_]|my[-_]|some[-_]|placeholder|example|changeme|change[-_]me|redacted|dummy|fake|sample|insert[-_]|todo|fixme|none|null|nil|true|false)'

# --- patterns --------------------------------------------------------------------
#
# Three parallel arrays rather than a delimited string: every regex here contains "|"
# as alternation, so any single-character field delimiter collides with the data.
#
# Ordered most-specific first. A line already reported is not reported again by a
# later pattern (see report()), so the label a reader sees is the most informative one.

LABELS=()
FLAGS=()
REGEXES=()

add_pattern() { LABELS+=("$1"); FLAGS+=("$2"); REGEXES+=("$3"); }

add_pattern "private key block"                 ""  '-----BEGIN( [A-Z0-9]+)* PRIVATE KEY-----'
add_pattern "Anthropic API key (sk-ant-)"       ""  'sk-ant-[A-Za-z0-9_-]{16,}'
add_pattern "GitHub token (ghp_/gho_/ghs_/ghu_)" "" 'gh[pousr]_[A-Za-z0-9]{20,}'
add_pattern "GitHub fine-grained PAT"           ""  'github_pat_[A-Za-z0-9_]{20,}'
add_pattern "Slack token (xox*)"                ""  'xox[baprs]-[A-Za-z0-9-]{10,}'
add_pattern "AWS access key id (AKIA)"          ""  'AKIA[0-9A-Z]{16}'
add_pattern "Google API key (AIza)"             ""  'AIza[A-Za-z0-9_-]{35}'
add_pattern "Stripe key (sk_live/rk_live)"      ""  '[sr]k_(live|test)_[A-Za-z0-9]{16,}'
# Hyphens allowed after sk-: current OpenAI keys are sk-proj-… and sk-svcacct-….
add_pattern "OpenAI-style API key (sk-)"        ""  '(^|[^A-Za-z0-9_-])sk-[A-Za-z0-9_-]{20,}'
add_pattern "JWT"                               ""  'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'
add_pattern "connection string carrying a password" "" '[a-zA-Z][a-zA-Z0-9+.-]*://[^[:space:]/:@"]+:[^[:space:]/:@"]+@[^[:space:]/"]+'

# These two carry a value that has to be checked against PLACEHOLDER, so they are
# scanned separately below rather than from the arrays above.
#
# Both are case-insensitive and both tolerate a quote between the name and the
# separator, because the material being scanned is rendered from JSON: a credential
# appears as "ANTHROPIC_API_KEY": "…" far more often than as ANTHROPIC_API_KEY=….
readonly ASSIGN_LABEL="credential assignment with a real value"
readonly ASSIGN_RE='[A-Za-z0-9_.-]*(KEY|TOKEN|SECRET|PASSWORD|PASSWD|PASSPHRASE|CREDENTIAL)[A-Za-z0-9_.-]*["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"']?[^[:space:],;}]+'
readonly AUTH_LABEL="Authorization header with a bearer value"
readonly AUTH_RE='authorization["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"']?(bearer|basic|token)[[:space:]]+[^[:space:]"'"'"',;}]{8,}'

# --- scan ------------------------------------------------------------------------

findings=0
# Lines already reported, as "|<file>:<lineno>|" segments. Bash 3.2 (the macOS system
# shell) has no associative arrays, so membership is a substring test on one string.
reported_lines="|"

already_reported() {
  case "$reported_lines" in
    *"|$1:$2|"*) return 0 ;;
    *) return 1 ;;
  esac
}

# Print one finding. Truncates the context line so a long transcript line does not
# flood the report; the file:line reference is what a reader follows to see the rest.
report() {
  local label="$1" file="$2" lineno="$3" text="$4"
  already_reported "$file" "$lineno" && return 0
  findings=$((findings + 1))
  reported_lines="${reported_lines}${file}:${lineno}|"
  printf '\n[%d] %s\n' "$findings" "$label"
  printf '    %s:%s\n' "$file" "$lineno"
  printf '    > %.200s\n' "$text"
}

# Strip the assignment's name and separator, then one leading quote, leaving the value.
extract_value() {
  printf '%s' "$1" | sed -E 's/^[^:=]*[:=][[:space:]]*//; s/^["'"'"']//'
}

is_placeholder() {
  printf '%s' "$1" | grep -q -a -i -E -e "^$PLACEHOLDER"
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

scan_file() {
  local file="$1" i label re flags out rc line lineno text value

  i=0
  while [ "$i" -lt "${#REGEXES[@]}" ]; do
    label="${LABELS[$i]}"
    flags="${FLAGS[$i]}"
    re="${REGEXES[$i]}"
    i=$((i + 1))

    if [ "$flags" = "i" ]; then
      out="$(grep -a -n -i -E -e "$re" -- "$file")"
    else
      out="$(grep -a -n -E -e "$re" -- "$file")"
    fi
    rc=$?
    [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file for: $label"

    [ -z "$out" ] && continue
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      lineno="${line%%:*}"
      text="${line#*:}"
      report "$label" "$file" "$lineno" "$text"
    done <<EOF
$out
EOF
  done

  # Credential assignments, with placeholder values rejected.
  out="$(grep -a -n -i -E -e "$ASSIGN_RE" -- "$file")"
  rc=$?
  [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file for: $ASSIGN_LABEL"
  if [ -n "$out" ]; then
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      lineno="${line%%:*}"
      text="${line#*:}"
      already_reported "$file" "$lineno" && continue
      value="$(printf '%s' "$text" | grep -a -o -i -E -e "$ASSIGN_RE" | head -1)"
      value="$(extract_value "$value")"
      [ -z "$value" ] && continue
      is_placeholder "$value" && continue
      # A value shorter than 8 characters is not a credential worth stopping a run over.
      [ "${#value}" -lt 8 ] && continue
      report "$ASSIGN_LABEL" "$file" "$lineno" "$text"
    done <<EOF
$out
EOF
  fi

  # Authorization headers, same placeholder rejection.
  out="$(grep -a -n -i -E -e "$AUTH_RE" -- "$file")"
  rc=$?
  [ "$rc" -gt 1 ] && die "grep failed (exit $rc) while scanning $file for: $AUTH_LABEL"
  if [ -n "$out" ]; then
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      lineno="${line%%:*}"
      text="${line#*:}"
      already_reported "$file" "$lineno" && continue
      value="$(printf '%s' "$text" | grep -a -o -i -E -e "$AUTH_RE" | head -1 \
               | sed -E 's/.*(bearer|basic|token)[[:space:]]+//I; s/^["'"'"']//')"
      [ -z "$value" ] && continue
      is_placeholder "$value" && continue
      report "$AUTH_LABEL" "$file" "$lineno" "$text"
    done <<EOF
$out
EOF
  fi

  return 0
}

printf 'scan-secrets: scanning %d file(s)\n' "$#"

for f in "$@"; do
  scan_file "$f"
done

if [ "$findings" -eq 0 ]; then
  printf '\nscan-secrets: clean — no credential shapes found.\n'
  exit "$EXIT_CLEAN"
fi

printf '\nscan-secrets: %d finding(s). Resolve each one individually — redact, withhold, or accept as a false positive — before anything is archived.\n' "$findings"
exit "$EXIT_HITS"
