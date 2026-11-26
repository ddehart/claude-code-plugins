#!/usr/bin/env bash
#
# check-wikilinks.sh — fails when a [[wikilink]] is split across a line break.
# Hard-wrapped prose does that to long note titles, silently: the result is not a link.
#
# Usage:  check-wikilinks.sh <graph-root>
#
# Read-only: it never writes inside the graph. Each finding is one line on stdout,
#   <file>:<line>: [[link text]]        (text shown rejoined; line = where it opens)
#
# Exit codes: 0 clean; 1 findings, listed; 2 the check could not run (bad usage,
# missing root, no markdown files, an unreadable config, awk failure). 2 is not a pass.
#
# What is read: every *.md under the root, raw text, YAML frontmatter included; a
# link's target is never resolved. What is not:
#   - .git directories, and each raw archive the nearest .commons.yml at or above the
#     root names under a source tier's archive: key. Archives are verbatim raw material
#     (transcripts), not notes. Each skipped directory is named on stdout.
#   - Code: fenced blocks (``` or ~~~) and inline code spans, including a span that
#     wraps. Indented (four-space) code is NOT recognized; list continuations look the
#     same and are far more common.
# A link ends at a blank line, and a [[ not closed within 1000 bytes is not a link.
# A code fence that never closes is a finding of its own: the rest of that file is
# code to a renderer and was not checked.
#
# Rationale for each of these: docs/specs/knowledge-commons-wikilink-check.md in the
# plugin's source repository.

set -uo pipefail

readonly EXIT_CLEAN=0
readonly EXIT_FINDINGS=1
readonly EXIT_ERROR=2

die() {
  printf 'check-wikilinks: %s\n' "$1" >&2
  exit "$EXIT_ERROR"
}

usage() {
  printf 'usage: check-wikilinks.sh <graph-root>\n' >&2
  exit "$EXIT_ERROR"
}

# --- arguments and preflight ------------------------------------------------------

[ "$#" -eq 1 ] || usage
case "$1" in -*) printf 'check-wikilinks: unknown option: %s\n' "$1" >&2; usage ;; esac
ROOT="$1"

command -v awk  >/dev/null 2>&1 || die "awk not found on PATH; cannot check"
command -v find >/dev/null 2>&1 || die "find not found on PATH; cannot check"

[ -e "$ROOT" ] || die "no such directory: $ROOT"
[ -d "$ROOT" ] || die "not a directory: $ROOT (give the graph root, not a note)"
ROOT="${ROOT%/}"
[ -n "$ROOT" ] || ROOT="/"
ROOT_PHYS="$(cd "$ROOT" 2>/dev/null && pwd -P)" || die "cannot enter $ROOT"

WORK="$(mktemp -d)" || die "mktemp failed"
trap 'rm -rf "$WORK"' EXIT

# --- raw archives: what is not read -----------------------------------------------
#
# archive: is read by pattern from the nearest .commons.yml, in block form and flow
# form ({ ..., archive: x, ... }). It is a project-relative directory by convention,
# so it is resolved against the config's own directory.

EXCLUDES=()     # prefixes in the form find prints them: "$ROOT/sub/dir"

CONFIG=""
d="$ROOT_PHYS"
while :; do
  if [ -f "$d/.commons.yml" ]; then CONFIG="$d/.commons.yml"; break; fi
  [ "$d" = "/" ] && break
  d="$(dirname "$d")"
done

if [ -n "$CONFIG" ]; then
  [ -r "$CONFIG" ] || die "cannot read $CONFIG, so this graph's raw archives are unknown"
  ARCHIVE_RE='(^|[[:space:],{])archive:[[:space:]]*("[^"]*"|'"'"'[^'"'"']*'"'"'|[^[:space:],}]+)'
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"
    [[ "$line" =~ $ARCHIVE_RE ]] || continue
    v="${BASH_REMATCH[2]}"
    v="${v#[\"\']}"; v="${v%[\"\']}"
    [ -n "$v" ] || continue
    phys="$(cd "$(dirname "$CONFIG")/$v" 2>/dev/null && pwd -P)" || continue
    # An archive that covers the root would skip every note: a broken config, not a
    # clean graph.
    case "$ROOT_PHYS/" in
      "$phys"/*) die "archive: $v in $CONFIG covers the whole graph root; refusing to report a graph clean without reading it" ;;
    esac
    case "$phys" in
      "$ROOT_PHYS"/*) EXCLUDES+=("$ROOT/${phys#"$ROOT_PHYS"/}") ;;
    esac
  done < "$CONFIG"
fi

is_excluded() {
  local f="$1" x
  [ "${#EXCLUDES[@]}" -gt 0 ] || return 1
  for x in "${EXCLUDES[@]}"; do
    case "$f" in "$x"/*) return 0 ;; esac
  done
  return 1
}

# --- the scanner ------------------------------------------------------------------
#
# POSIX awk only (no gensub, no match() arrays, no regex intervals). One pass, linear
# in the size of the file: nothing is re-copied per link or per code span, so a
# paragraph of any size costs what its bytes cost. (An earlier version built each
# paragraph into one string and took 35 s on 200 KB of "[[".)
#
# A paragraph is a run of non-blank lines outside a fence. It is the unit because an
# inline code span may wrap within one, and because a blank line is what stops a stray
# [[ from pairing with an unrelated ]] far below it. Within a paragraph:
#
#   pass 1  list every backtick run and, for each, the next run of the same length.
#           A run opens a code span only if such a closer exists; otherwise it is a
#           literal character.
#   pass 2  walk the lines again, feeding the text outside code spans to prose(),
#           which tracks at most one open link: its text so far, the line it opened
#           on, and how many line breaks it has crossed.

read -r -d '' AWK_PROG <<'AWK' || true
# Something that is not link text (a line break, a code span) sits inside the open
# link. Past MAXLINK bytes it is not a link, which also bounds the cost of a stray [[.
function gap() {
  if (!pend) return
  ptext = ptext " "
  if (length(ptext) > MAXLINK) pend = 0
}

function report(line, text) {
  gsub(/[ \t\r]+/, " ", text)
  printf "%s:%d: [[%s]]\n", cur, line, text
}

# Text outside code, in order. A link can only become a finding by staying open across
# a line break, so a link that opens and closes inside one piece is never looked at.
function prose(t, ln,    p, n, i, c) {
  if (t == "") return
  if (index(t, "[[") == 0) {
    if (!pend) return
    c = index(t, "]]")
    if (c == 0) { ptext = ptext t; if (length(ptext) > MAXLINK) pend = 0; return }
    if (pnl > 0) report(pline, ptext substr(t, 1, c - 1))
    pend = 0
    return
  }
  n = split(t, p, /\[\[/)
  if (pend) {
    c = index(p[1], "]]")
    if (c > 0 && pnl > 0) report(pline, ptext substr(p[1], 1, c - 1))
    pend = 0          # closed, or abandoned because another [[ opened first
  }
  # Only the last opener in the piece can still be open at its end.
  if (index(p[n], "]]") == 0) { pend = 1; ptext = p[n]; pline = ln; pnl = 0 }
}

function check_block(s, e,    i, j, m, r, k, nr, L, closer) {
  if (s == 0) return
  pend = 0

  nr = 0
  for (i = s; i <= e; i++) {
    if (index(lines[i], "`") == 0) continue
    m = split(lines[i], seg, "`")
    r = 0
    for (j = 2; j <= m; j++) {
      r++
      if (seg[j] == "" && j < m) continue
      run[++nr] = r; r = 0
    }
  }
  for (k = nr; k >= 1; k--) {
    L = run[k]
    nxt[k] = (L in last) ? last[L] : 0
    last[L] = k
  }
  for (L in last) delete last[L]

  k = 0; closer = 0
  for (i = s; i <= e; i++) {
    if (i > s && pend) { pnl++; gap() }
    if (index(lines[i], "`") == 0) {
      if (closer == 0) prose(lines[i], i)
      continue
    }
    m = split(lines[i], seg, "`")
    if (closer == 0) prose(seg[1], i)
    r = 0
    for (j = 2; j <= m; j++) {
      r++
      if (seg[j] == "" && j < m) continue
      k++; r = 0
      if (closer == 0) closer = nxt[k]
      else if (k == closer) closer = 0
      gap()
      if (closer == 0) prose(seg[j], i)
    }
  }
  pend = 0
}

function end_file(    i, S, T, infence, fch, flen, fline, bs) {
  infence = 0; bs = 0
  for (i = 1; i <= n; i++) {
    S = lines[i]
    sub(/\r$/, "", S)
    sub(/^[ \t>]+/, "", S)

    if (infence) {
      T = S
      sub(/[ \t]+$/, "", T)
      if (length(T) >= flen && ((fch == "`" && T ~ /^`+$/) || (fch == "~" && T ~ /^~+$/))) infence = 0
      continue
    }

    fch = ""
    if (match(S, /^```+/)) {
      # An info string cannot contain a backtick; if it does, this line is prose that
      # happens to start with an inline code span.
      if (index(substr(S, RLENGTH + 1), "`") == 0) fch = "`"
    } else if (match(S, /^~~~+/)) {
      fch = "~"
    }
    if (fch != "") {
      check_block(bs, i - 1); bs = 0
      infence = 1; flen = RLENGTH; fline = i
      continue
    }

    if (S == "") { check_block(bs, i - 1); bs = 0; continue }
    if (bs == 0) bs = i
  }
  check_block(bs, n)

  if (infence)
    printf "%s:%d: unclosed code fence; the rest of this file was not checked\n", cur, fline
  n = 0
}

BEGIN { MAXLINK = 1000; n = 0 }
# cur, not FILENAME: by the time a file is finished, FILENAME already names the next.
FNR == 1 { if (NR > 1) end_file(); cur = FILENAME }
{ lines[++n] = $0 }
END { if (NR > 0) end_file() }
AWK

[ -n "$AWK_PROG" ] || die "internal error: scanner program is empty"

# --- collect the files ------------------------------------------------------------

LIST="$WORK/files"
find "$ROOT" -name .git -prune -o -type f -name '*.md' -print0 > "$LIST" 2>"$WORK/find.err"
rc=$?
[ "$rc" -eq 0 ] || die "find failed (exit $rc) under $ROOT: $(head -n 1 "$WORK/find.err")"

NL='
'
FILES=()
SKIPPED=0
while IFS= read -r -d '' f; do
  # A finding is one line that starts with a path. A path holding a newline could
  # forge one, so it is refused rather than reported around.
  case "$f" in
    *"$NL"*) die "a file or directory name under $(dirname "${f%%"$NL"*}") contains a newline; rename it, nothing was checked" ;;
  esac
  if is_excluded "$f"; then SKIPPED=$((SKIPPED + 1)); continue; fi
  FILES+=("$f")
done < "$LIST"

# Zero files is a wrong root far more often than an empty graph.
[ "${#FILES[@]}" -gt 0 ] || die "no markdown files to check under $ROOT (${SKIPPED} skipped as archived); nothing was checked"

# --- check ------------------------------------------------------------------------
#
# awk runs in the main shell, in batches, with its status checked each time: a scanner
# that died halfway must stop the run, not shorten the list of findings. LC_ALL=C
# because the program only ever looks for ASCII ([[ ]] ` and whitespace), and in a
# UTF-8 locale awk re-walks multibyte text on every index() and substr(): 2.2 s against
# 0.1 s on a 970-note graph, for identical output.

FINDINGS="$WORK/findings"
: > "$FINDINGS" || die "cannot write to $FINDINGS"
i=0
while [ "$i" -lt "${#FILES[@]}" ]; do
  LC_ALL=C awk "$AWK_PROG" "${FILES[@]:$i:200}" >> "$FINDINGS"
  rc=$?
  [ "$rc" -eq 0 ] || die "awk failed (exit $rc) while checking files under $ROOT"
  i=$((i + 200))
done

cat "$FINDINGS"

if [ "${#EXCLUDES[@]}" -gt 0 ]; then
  for x in "${EXCLUDES[@]}"; do
    printf 'check-wikilinks: not read (raw archive, named by archive: in %s): %s\n' "$CONFIG" "$x"
  done
  printf 'check-wikilinks: %d archived file(s) skipped; archives are verbatim raw material, not notes.\n' "$SKIPPED"
fi

count="$(grep -c '' "$FINDINGS")"
if [ "$count" -eq 0 ]; then
  printf 'check-wikilinks: clean — %d file(s) under %s, no wikilink split across a line break.\n' \
    "${#FILES[@]}" "$ROOT"
  exit "$EXIT_CLEAN"
fi

printf 'check-wikilinks: %d finding(s) under %s. A wikilink stays on one line: rejoin each one (the line break and the indentation after it become one space).\n' \
  "$count" "$ROOT"
exit "$EXIT_FINDINGS"
