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
#   2  the scan could not run (bad usage, unreadable file, missing grep)
#
# Exit 1 and exit 2 mean the same thing to the caller: do not archive. The preserve
# stage fails closed on any non-zero exit. A scan that cannot run is not a pass.

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

# --- patterns --------------------------------------------------------------------
#
# Each entry is "<label>|<ERE>". The label names the credential shape so a reader can
# judge the finding without reverse-engineering the regex.
#
# Placeholder rejection lives inside the assignment and Authorization patterns rather
# than in a second pass: a value that is bracketed (<your-key-here>), a shell or
# template reference ($VAR, ${VAR}, {{var}}), or one of the well-known dummy words is
# not a credential, and a gate that stops on those trains its reader to click through.

readonly PLACEHOLDER='([<{$"'"'"'[:space:]]|x{3,}|X{3,}|\*{3,}|\.\.\.|your[-_]|my[-_]|some[-_]|placeholder|example|changeme|change[-_]me|redacted|dummy|fake|sample|insert[-_]|todo|fixme|none|null|nil|true|false)'

PATTERNS=(
  "private key block|-----BEGIN( [A-Z0-9]+)* PRIVATE KEY-----"
  "Anthropic API key (sk-ant-)|sk-ant-[A-Za-z0-9_-]{16,}"
  "OpenAI-style API key (sk-)|(^|[^A-Za-z0-9_-])sk-[A-Za-z0-9]{20,}"
  "GitHub personal access token (ghp_)|ghp_[A-Za-z0-9]{20,}"
  "GitHub OAuth token (gho_)|gho_[A-Za-z0-9]{20,}"
  "GitHub fine-grained PAT (github_pat_)|github_pat_[A-Za-z0-9_]{20,}"
  "Slack token (xox*)|xox[baprs]-[A-Za-z0-9-]{10,}"
  "AWS access key id (AKIA)|AKIA[0-9A-Z]{16}"
  "connection string carrying a password|[a-zA-Z][a-zA-Z0-9+.-]*://[^[:space:]/:@]+:[^[:space:]/:@]+@[^[:space:]/]+"
  "Authorization header with a bearer value|[Aa]uthorization[[:space:]]*:[[:space:]]*(Bearer|Basic|Token|token)[[:space:]]+[^[:space:]\"']{8,}"
)

# Credential assignments are scanned separately from the table above, because "not a
# placeholder" cannot be expressed in a POSIX ERE: the match is made here and the
# captured value is then rejected against PLACEHOLDER.
readonly ASSIGN_LABEL="credential assignment with a real value"
readonly ASSIGN_RE='[A-Za-z_]*(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)[A-Za-z_]*[[:space:]]*[:=][[:space:]]*[^[:space:]]+'

# --- scan ------------------------------------------------------------------------

findings=0
# Lines already reported, as "|<file>:<lineno>|" segments. Bash 3.2 (the macOS system
# shell) has no associative arrays, so membership is a substring test on one string.
reported_lines="|"

# Run one pattern over one file. grep exits 0 on a match, 1 on no match, and >1 on its
# own failure — a bad regex, an unreadable file, a pattern eaten as an option. That
# third case must stop the scan: a grep error that is discarded reads exactly like a
# clean file, which is the failure this gate exists to prevent. (Found by the planted
# secret in the §7.1 test: a pattern beginning with "-" was parsed as options, grep
# exited 2, stderr was discarded, and a planted private key silently did not appear.)
grep_lines() {
  local re="$1" file="$2" out rc
  out="$(grep -a -n -E -e "$re" -- "$file")"
  rc=$?
  if [ "$rc" -gt 1 ]; then
    die "grep failed (exit $rc) while scanning $file for: $re"
  fi
  printf '%s' "$out"
}

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
  findings=$((findings + 1))
  reported_lines="${reported_lines}${file}:${lineno}|"
  printf '\n[%d] %s\n' "$findings" "$label"
  printf '    %s:%s\n' "$file" "$lineno"
  printf '    > %.200s\n' "$text"
}

scan_file() {
  local file="$1" entry label re out line lineno text value

  for entry in "${PATTERNS[@]}"; do
    label="${entry%%|*}"
    re="${entry#*|}"

    out="$(grep_lines "$re" "$file")"
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

  # Credential assignments, with placeholder values rejected. This pattern is the
  # catch-all, so a line one of the specific patterns above already flagged is skipped
  # rather than reported twice — a duplicate inflates the finding count and gives a
  # reader two things to resolve where there is one secret. Two *specific* shapes on one
  # line still earn two findings; only the generic pattern defers.
  out="$(grep_lines "$ASSIGN_RE" "$file")"
  [ -z "$out" ] && return 0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    lineno="${line%%:*}"
    text="${line#*:}"
    already_reported "$file" "$lineno" && continue
    # Value = everything after the first : or = in the matched assignment.
    value="$(printf '%s' "$text" | grep -a -o -E -e "$ASSIGN_RE" | head -1 | sed -E 's/^[^:=]*[:=][[:space:]]*//')"
    [ -z "$value" ] && continue
    if printf '%s' "$value" | grep -q -a -i -E -e "^$PLACEHOLDER"; then
      continue
    fi
    # A value shorter than 8 characters is not a credential worth stopping a run over.
    [ "${#value}" -lt 8 ] && continue
    report "$ASSIGN_LABEL" "$file" "$lineno" "$text"
  done <<EOF
$out
EOF
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
