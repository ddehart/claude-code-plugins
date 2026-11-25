#!/usr/bin/env bash
#
# check-wikilinks.sh — fails when a [[wikilink]] is split across a line break.
#
# Graph notes are written as prose hard-wrapped near a fixed column. A long note title
# that straddles the wrap column gets split:
#
#     ... the claim itself, see [[pruning window sets
#     the whole season's timing]] for ...
#
# That is not a link. Obsidian renders it as literal brackets and no resolver follows
# it, and nothing says so: the note reads fine in an editor. The convention (a wikilink
# stays on one line) is a rule a writer has to remember at the one moment its attention
# is on the sentence, so this is a check rather than more guidance.
#
# Usage:
#   check-wikilinks.sh [--exclude <dir>]... <graph-root>
#   check-wikilinks.sh --fix [--exclude <dir>]... <graph-root>
#
# Reads every *.md file under <graph-root>, skipping .git directories and the graph's
# raw archives (see "Raw archives are not notes" below). Each finding is one line on
# stdout:
#
#   <file>:<line>: [[link text]]
#
# with the link text shown rejoined and <line> the line the link opens on.
#
# Exit codes:
#   0  clean — no wikilink is split across a line break
#   1  findings — at least one, listed on stdout
#   2  the check could not run (bad usage, missing root, no markdown files, awk failure)
#
# A check that cannot run is not a pass: exit 2 is as much a "not clean" as exit 1.
#
# What counts, and what deliberately does not:
#
#   - Detection is on the raw text. Whether the target resolves to a note is not
#     consulted; a count taken only among resolvable targets missed a wrapped link in
#     practice, and a wrapped link to a note that does not exist yet is just as broken.
#   - YAML frontmatter is read like the body. supports: and genitor: carry links too.
#   - Code is skipped: fenced blocks (``` or ~~~) and inline code spans, including a
#     span that itself wraps. Notes quote the broken form as an example, and a note
#     documenting this defect must be able to pass. Indented (four-space) code blocks
#     are NOT recognized, because list continuation lines are indented prose and far
#     more common in a graph than indented code.
#   - A link ends at a blank line. A stray [[ in one paragraph and a stray ]] in a
#     later one are not a link, and neither is an unclosed [[ followed by a whole one.
#   - A code fence that never closes is reported as a finding of its own. Everything
#     after it is code as far as a renderer is concerned, so it is not checked, and a
#     check with an unread region does not get to say "clean".
#
# Raw archives are not notes
#
# A source tier whose material is too large to inline keeps it in a committed archive
# directory, named by that tier's archive: key in the project's .commons.yml. Those
# files are verbatim raw material (session transcripts, mostly): full of quoted tool
# output, unbalanced code fences, and shell text, and none of it is a note anyone
# wrote. Checking them reports findings no one may act on, since editing an archive
# falsifies the record it exists to keep. So they are not read, and because --fix only
# ever writes a file the check read, it cannot write to one.
#
# The script finds the nearest .commons.yml at or above <graph-root>, takes every
# archive: value in it (relative to that file's directory), and skips each one that
# lies inside the root. --exclude <dir> skips a further directory, for a graph with no
# config or a verbatim directory the config does not name. Every skipped directory is
# named on stdout, so what was not read is never a guess. An exclusion that would
# cover the whole root is refused (exit 2): that is a broken config, not a clean graph.
#
# --fix rejoins what it safely can: the line break and the indentation after it become
# one space, and nothing else in the file changes. It declines three shapes and leaves
# them reported for a hand decision, because joining them would not be whitespace-only
# or would be a guess:
#
#   - a link whose continuation line starts with a blockquote marker;
#   - a link that crosses more than one line break;
#   - text that does not read as a note title: it contains && || == or !=, or starts
#     with a shell test operator (-f, -d, -z, ...), $, !, ( or a quote. A multi-line
#     shell test quoted outside a code block looks exactly like a wrapped link
#     ("if [[ -f x &&" / "-d y ]]; then"), and rejoining it rewrites quoted code. The
#     check still REPORTS these: the test is deliberately broad, a real title can trip
#     it, and a wrongly declined fix costs one hand edit while a wrongly skipped
#     finding is a broken link nobody hears about. The hand decision is to rejoin it if
#     it is a link, or put it in a code span or fence if it is code.
#
# The exit code after --fix comes from re-running the check on the result, not from
# what the fix believes it did.
#
# --fix replaces a note by writing a temporary file beside it and renaming that over
# the original, so an interruption leaves either the old note or the new one, never a
# truncated one. The file's mode is kept. A hard link to the note is not: the other
# name keeps the old content. Notes in a git working tree have no hard links, and a
# truncated note is the worse failure.

set -uo pipefail

readonly EXIT_CLEAN=0
readonly EXIT_FINDINGS=1
readonly EXIT_ERROR=2

die() {
  printf 'check-wikilinks: %s\n' "$1" >&2
  exit "$EXIT_ERROR"
}

usage() {
  printf 'usage: check-wikilinks.sh [--fix] [--exclude <dir>]... <graph-root>\n' >&2
  exit "$EXIT_ERROR"
}

# --- arguments and preflight ------------------------------------------------------

FIX=0
ROOT=""
USER_EXCLUDES=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --fix)     FIX=1 ;;
    --exclude) [ "$#" -ge 2 ] || usage; USER_EXCLUDES+=("$2"); shift ;;
    -*)        printf 'check-wikilinks: unknown option: %s\n' "$1" >&2; usage ;;
    *)         [ -z "$ROOT" ] || usage; ROOT="$1" ;;
  esac
  shift
done
[ -n "$ROOT" ] || usage

command -v awk  >/dev/null 2>&1 || die "awk not found on PATH; cannot check"
command -v find >/dev/null 2>&1 || die "find not found on PATH; cannot check"

[ -e "$ROOT" ] || die "no such directory: $ROOT"
[ -d "$ROOT" ] || die "not a directory: $ROOT (give the graph root, not a note)"
ROOT="${ROOT%/}"
[ -n "$ROOT" ] || ROOT="/"

WORK="$(mktemp -d)" || die "mktemp failed"
# FIX_TMP is the one file this script ever creates outside $WORK: the replacement for a
# note, written beside it so the rename is atomic. Removed here if a run dies mid-fix.
FIX_TMP=""
trap 'rm -rf "$WORK"; [ -n "$FIX_TMP" ] && rm -f "$FIX_TMP"' EXIT

# --- what is not read: raw archives -----------------------------------------------

ROOT_PHYS="$(cd "$ROOT" 2>/dev/null && pwd -P)" || die "cannot enter $ROOT"

# Prefixes (in the form find prints them, "$ROOT/sub/dir") of directories to skip, and
# a parallel array saying where each came from, for the report.
EXCLUDES=()
EXCLUDE_WHY=()

# $1 = a directory path, $2 = where it was named. Missing directories and ones outside
# the root are nothing to skip; one that covers the root is an error.
add_exclude() {
  local dir="$1" why="$2" phys
  [ -d "$dir" ] || return 0
  phys="$(cd "$dir" 2>/dev/null && pwd -P)" || return 0
  case "$ROOT_PHYS/" in
    "$phys"/*) die "$why names $dir, which covers the whole graph root; refusing to report a graph clean without reading it" ;;
  esac
  case "$phys" in
    "$ROOT_PHYS"/*)
      if [ "$ROOT" = "/" ]; then EXCLUDES+=("/${phys#"$ROOT_PHYS"/}")
      else EXCLUDES+=("$ROOT/${phys#"$ROOT_PHYS"/}"); fi
      EXCLUDE_WHY+=("$why")
      ;;
  esac
  return 0
}

# The nearest .commons.yml at or above the root. Read for one key only, by pattern: a
# YAML parser is a dependency, and archive: is a plain scalar path in both the block
# form (archive: knowledge/sources/raw/) and the flow form ({ ..., archive: x, ... }).
CONFIG=""
d="$ROOT_PHYS"
while :; do
  if [ -f "$d/.commons.yml" ]; then CONFIG="$d/.commons.yml"; break; fi
  [ "$d" = "/" ] && break
  d="$(dirname "$d")"
done

if [ -n "$CONFIG" ]; then
  [ -r "$CONFIG" ] || die "cannot read $CONFIG, so this graph's raw archives are unknown"
  CONFIG_DIR="$(dirname "$CONFIG")"
  ARCHIVE_RE='(^|[[:space:],{])archive:[[:space:]]*("[^"]*"|'"'"'[^'"'"']*'"'"'|[^[:space:],}]+)'
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"
    [[ "$line" =~ $ARCHIVE_RE ]] || continue
    v="${BASH_REMATCH[2]}"
    v="${v#[\"\']}"; v="${v%[\"\']}"
    [ -n "$v" ] || continue
    case "$v" in
      /*)    ;;
      "~/"*) v="$HOME/${v#"~/"}" ;;
      *)     v="$CONFIG_DIR/$v" ;;
    esac
    add_exclude "$v" "archive: in $CONFIG"
  done < "$CONFIG"
fi

if [ "${#USER_EXCLUDES[@]}" -gt 0 ]; then
  for x in "${USER_EXCLUDES[@]}"; do
    [ -d "$x" ] || die "--exclude: no such directory: $x"
    add_exclude "$x" "--exclude"
  done
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
# One awk program, POSIX features only (no gensub, no match() arrays, no regex
# intervals), so it runs on the awk a stock macOS or Debian has.
#
# It reads a file whole, walks it once to set aside fenced code, and hands each
# paragraph (a run of non-blank lines outside a fence) to check_block as one string.
# The paragraph is the unit for two reasons: an inline code span may wrap within one,
# so spans cannot be masked a line at a time; and a blank line is what stops a stray
# [[ from pairing with an unrelated ]] far below it.
#
# Communication is through the environment rather than -v, because -v interprets
# backslash escapes in the value and a path is not a string literal.
#
#   CW_MODE     check | fix
#   CW_HITLIST  check: append the name of each file with a finding (one per line)
#   CW_OUT      fix:   write the rejoined file content here
#   CW_NONL     fix:   1 if the original has no trailing newline
#
# No apostrophes inside the program: it sits in a quoted heredoc, but keeping it free
# of them means it can be moved into a single-quoted string without re-reading it.

read -r -d '' AWK_PROG <<'AWK' || true
function count_newlines(s,    t) { t = s; return gsub(/\n/, "", t) }

# Replace the characters of every inline code span in B with spaces, keeping newlines,
# so offsets and line numbers still hold. A backtick run opens a span only if a later
# run of exactly the same length closes it within the block; otherwise it is literal.
function mask_code(B,    pos, st, n, q, cs, cl, found, seg) {
  pos = 1
  while (match(substr(B, pos), /`+/)) {
    st = pos + RSTART - 1; n = RLENGTH
    q = st + n; found = 0
    while (match(substr(B, q), /`+/)) {
      cs = q + RSTART - 1; cl = RLENGTH
      if (cl == n) { found = 1; break }
      q = cs + cl
    }
    if (!found) { pos = st + n; continue }
    seg = substr(B, st, cs + cl - st)
    gsub(/[^\n]/, " ", seg)
    B = substr(B, 1, st - 1) seg substr(B, cs + cl)
    pos = cs + cl
  }
  return B
}

# Text --fix will not rejoin, because a note title does not look like this and a shell
# test does. Broad on purpose; see the header. \047 is an apostrophe.
function not_a_title(t) {
  if (index(t, "&&") || index(t, "||") || index(t, "==") || index(t, "!=")) return 1
  if (t ~ /^[ \t]*-[A-Za-z][ \t]/) return 1
  if (t ~ /^[ \t]*[$!("\047]/) return 1
  return 0
}

function check_block(s, e,    B, i, pos, k, st, rest, c, o, text, shown, line, nl, nxt, why) {
  if (s == 0) return
  B = lines[s]
  for (i = s + 1; i <= e; i++) B = B "\n" lines[i]
  if (index(B, "[[") == 0) return
  B = mask_code(B)

  pos = 1
  while ((k = index(substr(B, pos), "[[")) > 0) {
    st = pos + k - 1
    rest = substr(B, st + 2)
    c = index(rest, "]]")
    o = index(rest, "[[")
    # Unclosed, or another link opens first: this [[ is not the start of a link.
    if (c == 0 || (o > 0 && o < c)) { pos = st + 1; continue }
    text = substr(rest, 1, c - 1)
    pos = st + 2 + c + 1
    nl = count_newlines(text)
    if (nl == 0) continue

    line = s + count_newlines(substr(B, 1, st - 1))
    shown = text
    gsub(/[ \t\r]*\n[ \t]*/, " ", shown)

    if (mode == "fix") {
      nxt = lines[line + 1]
      sub(/^[ \t]+/, "", nxt)
      why = ""
      if (nl > 1) why = "crosses more than one line break"
      else if (substr(nxt, 1, 1) == ">") why = "continues inside a blockquote"
      else if (not_a_title(shown)) why = "does not read as a note title"
      if (why == "") {
        joinafter[line] = 1
        printf "rejoined: %s:%d: [[%s]]\n", cur, line, shown
      } else {
        printf "left alone (%s): %s:%d: [[%s]]\n", why, cur, line, shown
      }
      continue
    }
    printf "%s:%d: [[%s]]\n", cur, line, shown
    hit = 1
  }
}

function end_file(    i, S, T, infence, fch, flen, fline, bs, rest, buf, nxt, first) {
  infence = 0; bs = 0; hit = 0
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

    if (S ~ /^[ \t]*$/) { check_block(bs, i - 1); bs = 0; continue }
    if (bs == 0) bs = i
  }
  check_block(bs, n)

  if (infence && mode != "fix") {
    printf "%s:%d: unclosed code fence; the rest of this file was not checked\n", cur, fline
    hit = 1
  }
  if (hit && hitlist != "") print cur >> hitlist

  if (mode == "fix") {
    first = 1
    for (i = 1; i <= n; i++) {
      buf = lines[i]
      while (i in joinafter) {
        nxt = lines[i + 1]
        sub(/[ \t\r]+$/, "", buf)
        sub(/^[ \t]+/, "", nxt)
        buf = buf " " nxt
        i++
      }
      printf "%s%s", (first ? "" : "\n"), buf > out
      first = 0
    }
    if (n > 0 && nonl != "1") printf "\n" > out
    close(out)
  }

  for (i in joinafter) delete joinafter[i]
  n = 0
}

BEGIN {
  mode = ENVIRON["CW_MODE"]; hitlist = ENVIRON["CW_HITLIST"]
  out = ENVIRON["CW_OUT"];   nonl = ENVIRON["CW_NONL"]
  n = 0
}
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

FILES=()
SKIPPED=0
while IFS= read -r -d '' f; do
  if is_excluded "$f"; then SKIPPED=$((SKIPPED + 1)); continue; fi
  FILES+=("$f")
done < "$LIST"

# Say what was not read, every run. A skipped directory nobody is told about is how a
# real note, misfiled under an archive, would go unchecked without anyone knowing.
report_excludes() {
  local i=0
  [ "${#EXCLUDES[@]}" -gt 0 ] || return 0
  while [ "$i" -lt "${#EXCLUDES[@]}" ]; do
    printf 'check-wikilinks: not read (raw archive, %s): %s\n' "${EXCLUDE_WHY[$i]}" "${EXCLUDES[$i]}"
    i=$((i + 1))
  done
  printf 'check-wikilinks: %d archived file(s) skipped; archives are verbatim raw material, not notes.\n' "$SKIPPED"
}

# Zero files is a wrong root far more often than an empty graph, and "0 files, clean"
# is exactly the pass-by-not-looking this script exists to prevent.
[ "${#FILES[@]}" -gt 0 ] || die "no markdown files to check under $ROOT (${SKIPPED} skipped as archived); nothing was checked"

# Run the check over every file, findings to $1, names of files with findings to $2.
# awk runs in the main shell, in batches, with its status checked each time: a scanner
# that died halfway must stop the run, not shorten the list of findings.
scan_all() {
  local findings="$1" hitlist="$2" i=0 total="${#FILES[@]}" rc
  : > "$findings" || die "cannot write to $findings"
  : > "$hitlist"  || die "cannot write to $hitlist"
  while [ "$i" -lt "$total" ]; do
    CW_MODE=check CW_HITLIST="$hitlist" awk "$AWK_PROG" "${FILES[@]:$i:200}" >> "$findings"
    rc=$?
    [ "$rc" -eq 0 ] || die "awk failed (exit $rc) while checking files under $ROOT"
    i=$((i + 200))
  done
}

# --- fix --------------------------------------------------------------------------

if [ "$FIX" -eq 1 ]; then
  scan_all "$WORK/before" "$WORK/hits"
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    [ -f "$f" ] || die "cannot fix: not a file: $f (a path containing a newline is not supported)"
    nonl=0
    [ "$(tail -c 1 "$f" | wc -l)" -eq 0 ] && nonl=1
    : > "$WORK/out"
    CW_MODE=fix CW_OUT="$WORK/out" CW_NONL="$nonl" awk "$AWK_PROG" "$f"
    rc=$?
    [ "$rc" -eq 0 ] || die "awk failed (exit $rc) while fixing $f; the file was not changed"
    if ! cmp -s "$WORK/out" "$f"; then
      # Replace by rename, never by writing through the note: see the header. cp -p
      # makes the temporary file with the note's mode, then the new content goes into
      # it, so the mode survives the rename. The name does not end in .md, so a check
      # running concurrently never reads a half-written note.
      FIX_TMP="$(dirname "$f")/.check-wikilinks.$$.tmp"
      cp -p "$f" "$FIX_TMP"      || die "could not create $FIX_TMP; $f was not changed"
      cat "$WORK/out" > "$FIX_TMP" || die "could not write $FIX_TMP; $f was not changed"
      mv -f "$FIX_TMP" "$f"      || die "could not replace $f; it was not changed"
      FIX_TMP=""
    fi
  done < "$WORK/hits"
fi

# --- check (after a fix, this is the verification) --------------------------------

scan_all "$WORK/findings" "$WORK/hits"
cat "$WORK/findings"
report_excludes

count="$(grep -c '' "$WORK/findings")"
if [ "$count" -eq 0 ]; then
  printf 'check-wikilinks: clean — %d file(s) under %s, no wikilink split across a line break.\n' \
    "${#FILES[@]}" "$ROOT"
  exit "$EXIT_CLEAN"
fi

printf 'check-wikilinks: %d finding(s) under %s. A wikilink stays on one line: rejoin each one (the line break and the indentation after it become one space).\n' \
  "$count" "$ROOT"
exit "$EXIT_FINDINGS"
