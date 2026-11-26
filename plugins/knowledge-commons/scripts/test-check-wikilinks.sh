#!/usr/bin/env bash
#
# test-check-wikilinks.sh — fixtures for the wrapped-wikilink check.
#
# Run it after any edit to check-wikilinks.sh.
#
#   ./test-check-wikilinks.sh
#
# Exits 0 if every case passes, 1 otherwise.
#
# Set CHECK_WIKILINKS to run the same cases against another copy of the script. That is
# how a case is shown to test something: point it at a copy with one behavior removed
# and the cases for that behavior must fail.
#
# The rules test-scan-secrets.sh states apply here too, and shape the cases below:
#
#   - Every behavior gets a fixture only that behavior decides. Each fixture lives in
#     its own graph root, so a case cannot pass on another fixture's finding.
#   - Assert the reported line, never the count alone. "one finding" is satisfied by a
#     finding on the wrong link.
#   - A negative fixture (code, an unclosed link) is paired with a positive one in the
#     same file wherever the skip could swallow too much, so "nothing reported" cannot
#     be earned by not looking.
#
# No fixture link resolves to a note, on purpose: the check reads raw text and must not
# care. A count taken only among resolvable targets missed a wrapped link in practice.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK="${CHECK_WIKILINKS:-$SCRIPT_DIR/check-wikilinks.sh}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

failures=0

pass() { printf '  ok    — %s\n' "$1"; }
fail() { printf '  FAIL  — %s\n' "$1"; failures=$((failures + 1)); }

[ -x "$CHECK" ] || { printf 'check-wikilinks.sh is not executable at %s\n' "$CHECK" >&2; exit 1; }

# Make a fresh graph root holding one note. $1 = root name, $2 = note path, $3 = content
# (written with printf %s, so the caller controls the trailing newline).
graph() {
  mkdir -p "$TMP/$1/$(dirname "$2")"
  printf '%s' "$3" > "$TMP/$1/$2"
}

# Run the check over a root. Sets OUT and RC.
OUT=""; RC=0
run() { OUT="$("$CHECK" "$@" 2>&1)"; RC=$?; }

want_exit() {
  if [ "$RC" -eq "$2" ]; then pass "$1"; else fail "$1 (wanted exit $2, got $RC)"; fi
}

# The output must contain this exact line.
want_line() {
  if printf '%s\n' "$OUT" | grep -q -x -F -e "$2"; then pass "$1"
  else fail "$1 — no line: $2"; printf '%s\n' "$OUT" | sed 's/^/          | /'; fi
}

# No finding line (path:line: [[...) may mention this text.
want_no_finding() {
  if printf '%s\n' "$OUT" | grep -E '^.+:[0-9]+: ' | grep -q -F -e "$2"; then
    fail "$1 — reported: $2"
  else pass "$1"; fi
}

findings() { printf '%s\n' "$OUT" | grep -c -E '^.+:[0-9]+: '; }

# --- detection --------------------------------------------------------------------

printf 'detection — a wikilink whose text contains a newline\n'

graph body "observations/a.md" '---
genitor: "[[observations]]"
---
A finding that bears on the pattern and is long enough to reach the wrap column, see [[pruning window sets
the whole season'"'"'s timing]] for the claim itself.
'
run "$TMP/body"
want_exit "wrapped link in body prose exits 1" 1
want_line "…and is reported as file:line: link text, at the line the link opens on" \
  "$TMP/body/observations/a.md:4: [[pruning window sets the whole season's timing]]"

graph front "observations/b.md" '---
genitor: "[[observations]]"
supports: ["[[thin before petal fall not after]]", "[[fixed calendar window versus
  triggered timing]]"]
---
Body with a whole link, [[observations]].
'
run "$TMP/front"
want_exit "wrapped link inside a frontmatter string exits 1" 1
want_line "…and is reported at its frontmatter line" \
  "$TMP/front/observations/b.md:3: [[fixed calendar window versus triggered timing]]"
[ "$(findings)" -eq 1 ] && pass "…and the whole links beside it are not reported" \
  || fail "frontmatter fixture should yield exactly 1 finding, got $(findings)"

graph alias "patterns/c.md" 'The alias half of a link can be what straddles the wrap, as in [[thin before petal fall|the thinning
  pattern]] here, and a whole [[a|b]] alias is fine.
'
run "$TMP/alias"
want_exit "wrapped link with an alias exits 1" 1
want_line "…and is reported with target and alias both" \
  "$TMP/alias/patterns/c.md:1: [[thin before petal fall|the thinning pattern]]"
[ "$(findings)" -eq 1 ] && pass "…and the one-line [[a|b]] is not reported" \
  || fail "alias fixture should yield exactly 1 finding, got $(findings)"

graph two "notes/d.md" 'First [[one wrapped
link]] and then, on the line the first one closes on, a second [[other wrapped
link]] closes here.
'
run "$TMP/two"
want_line "two wrapped links sharing a line: the first is reported" \
  "$TMP/two/notes/d.md:1: [[one wrapped link]]"
want_line "…and so is the second" \
  "$TMP/two/notes/d.md:2: [[other wrapped link]]"

graph "with space" "sub dir/a note.md" 'A path with spaces holds a [[wrapped
link]] too.
'
run "$TMP/with space"
want_line "a path containing spaces is scanned and reported intact" \
  "$TMP/with space/sub dir/a note.md:1: [[wrapped link]]"

graph quote "notes/q.md" '> A quoted passage with a [[wrapped
> link]] inside a blockquote.
'
run "$TMP/quote"
want_line "a link wrapped inside a blockquote is reported, marker and all" \
  "$TMP/quote/notes/q.md:1: [[wrapped > link]]"

graph long "notes/l.md" 'A span that crosses [[more
than
one]] line break.
'
run "$TMP/long"
want_line "a link crossing more than one line break is reported once, where it opens" \
  "$TMP/long/notes/l.md:1: [[more than one]]"
[ "$(findings)" -eq 1 ] && pass "…and only once" || fail "multi-break fixture should yield 1 finding, got $(findings)"

# The scanner runs in the C locale and counts bytes. Multibyte text before, inside and
# after a wrapped link must not shift the line it is reported on or mangle its text.
graph utf8 "notes/café — naïve.md" 'Zażółć gęślą jaźń — 日本語のテキスト, “curly quotes”, and an em dash — before the link.
Then résumé [[größe und maß — the long
  title with ünïcödé]] and after it: ✓ done.
'
run "$TMP/utf8"
want_line "multibyte text around and inside a wrapped link: right line, text intact" \
  "$TMP/utf8/notes/café — naïve.md:2: [[größe und maß — the long title with ünïcödé]]"
[ "$(findings)" -eq 1 ] && pass "…and it is the only finding" || fail "utf8 fixture should yield 1 finding, got $(findings)"

# A multi-line shell test quoted outside a code block has the shape of a wrapped link.
# It is reported; whether it is a link to rejoin or code to fence is a person's call.
graph shell "notes/hook.md" 'The hook bails early: if [[ -f "$lock" &&
  -d "$dir" ]]; then exit.
'
run "$TMP/shell"
want_line "a multi-line shell test outside code is reported like any other" \
  "$TMP/shell/notes/hook.md:1: [[ -f \"\$lock\" && -d \"\$dir\" ]]"

# Several files in one root. Every other fixture root holds a single note, and a scanner
# that reads many files in one pass can name the wrong one: the first version of this
# script attributed each finding to the file read after it, and every single-note case
# stayed green.
graph multi "a/first.md" 'A [[wrapped
link]] in the first note.
'
graph multi "b/second.md" 'Whole [[link]] only.
'
graph multi "c/third.md" 'Another [[split
title]] in the third note.
'
run "$TMP/multi"
want_line "with several notes, a finding names the file it is in" \
  "$TMP/multi/a/first.md:1: [[wrapped link]]"
want_line "…for each file that has one" \
  "$TMP/multi/c/third.md:1: [[split title]]"
want_no_finding "…and never the clean file between them" "second.md"
[ "$(findings)" -eq 2 ] && pass "…two findings in all" \
  || fail "multi-file fixture should yield exactly 2 findings, got $(findings)"

# --- clean ------------------------------------------------------------------------

printf '\nclean — nothing to report\n'

graph clean "patterns/e.md" '---
genitor: "[[patterns]]"
tags: [pruning]
---
Every link here is whole: [[thin before petal fall not after]], [[a|b]], [[note#heading]], and a
line that merely ends near one [[observations]]
and starts the next with another [[patterns]].
'
run "$TMP/clean"
want_exit "a clean graph exits 0" 0
[ "$(findings)" -eq 0 ] && pass "…with no finding lines" || fail "clean graph printed findings"

# --- code is not prose ------------------------------------------------------------
#
# Notes quote broken links as examples, and that is the case this check must not punish:
# a note documenting the defect would otherwise fail the check forever. Each fixture
# carries a real wrapped link AFTER the code, which is what proves the skip ended where
# the code did rather than swallowing the rest of the file.

printf '\ncode — a link quoted in code is an example, not a link\n'

graph fence "notes/f.md" 'An example of the defect:

```markdown
see [[quoted wrapped
link]] in a backtick fence
```

~~~
and [[another quoted
one]] in a tilde fence
~~~

After both fences close, a [[real wrapped
link]] still counts.
'
run "$TMP/fence"
want_exit "a file with fenced examples and one real wrapped link exits 1" 1
want_no_finding "a wrapped link inside a backtick fence is not reported" "quoted wrapped"
want_no_finding "a wrapped link inside a tilde fence is not reported" "another quoted"
want_line "the wrapped link after the fences is reported" \
  "$TMP/fence/notes/f.md:13: [[real wrapped link]]"

graph inline "notes/g.md" 'A link opens with `[[` and, some words later on the following line of the same paragraph,
closes with `]]`, which is prose about syntax. A code span can itself wrap: `[[quoted
span]]` is still code. Double backticks too: ``[[double
ticked]]`` here.

Then a [[real wrapped
link]] outside any code.
'
run "$TMP/inline"
want_exit "a file with inline-code examples and one real wrapped link exits 1" 1
want_no_finding "[[ and ]] in separate code spans on adjacent lines are not a link" "opens with"
want_no_finding "…reported under any text" "some words"
want_no_finding "a wrapped link inside a code span that itself wraps is not reported" "quoted span"
want_no_finding "…nor inside a double-backtick span" "double ticked"
want_line "the wrapped link outside code is reported" \
  "$TMP/inline/notes/g.md:6: [[real wrapped link]]"
[ "$(findings)" -eq 1 ] && pass "…and it is the only finding" \
  || fail "inline fixture should yield exactly 1 finding, got $(findings)"

graph lonetick "notes/h.md" 'A lone backtick ` with no partner is a literal character, so this [[wrapped
link]] is still prose.
'
run "$TMP/lonetick"
want_line "an unpaired backtick does not hide the rest of the paragraph" \
  "$TMP/lonetick/notes/h.md:1: [[wrapped link]]"

# A fence that never closes runs to the end of the file, and everything after it would
# go unread. Reported, because a check with an unread region is not a pass.
graph openfence "notes/i.md" 'Text.

```bash
echo "this fence is never closed"

A [[wrapped
link]] the fence swallows.
'
run "$TMP/openfence"
want_exit "an unclosed code fence exits 1 rather than passing unread text" 1
want_line "…and is reported at the line the fence opens on" \
  "$TMP/openfence/notes/i.md:3: unclosed code fence; the rest of this file was not checked"

# --- not a link -------------------------------------------------------------------

printf '\nnot a link — an opener with no closer\n'

graph unclosed "notes/j.md" 'A stray opener [[ in prose, then a whole [[link]] on the same line.
Another stray [[opener at the end of a line
followed by a whole [[link]] on the next, which must not be read as one long link.

And an unclosed [[link at the very end of the file'
run "$TMP/unclosed"
want_exit "unclosed [[ (mid-file, and at end of file with no newline) exits 0" 0
[ "$(findings)" -eq 0 ] && pass "…with no finding lines" || fail "unclosed-link fixture printed findings"

graph para "notes/k.md" 'A stray opener [[ at the end of one paragraph

and a stray closer ]] in the next are not a link: a blank line ends a link.
'
run "$TMP/para"
want_exit "[[ and ]] in different paragraphs exits 0" 0

# A [[ that stays open past 1000 bytes is not a link, however the paragraph ends.
filler="$(printf 'word %.0s' $(seq 1 150))"
graph toolong "notes/m.md" "A stray opener [[ and then
$filler
$filler
and a stray closer ]] far below it in the same paragraph.
"
run "$TMP/toolong"
want_exit "a [[ not closed within 1000 bytes is not a link: exit 0" 0

# Size. One paragraph of 50,000 one-line links and code spans, then a real finding
# after it. The scanner is one pass; this is here so a regression to re-copying the
# paragraph per link shows up as a test that takes minutes, and so the finding after
# a very long paragraph is still on the right line.
mkdir -p "$TMP/big/notes"
awk 'BEGIN { for (i = 1; i <= 50000; i++) printf "- [[note %d]] and `code %d` [[\n", i, i;
             printf "\nA [[wrapped\nlink]] after it.\n" }' > "$TMP/big/notes/map.md"
run "$TMP/big"
want_line "a finding after a 50,000-line paragraph is on the right line" \
  "$TMP/big/notes/map.md:50002: [[wrapped link]]"
[ "$(findings)" -eq 1 ] && pass "…and nothing in the paragraph itself is reported" \
  || fail "big fixture should yield 1 finding, got $(findings)"

# --- what is scanned --------------------------------------------------------------

printf '\nscope — which files are read\n'

graph scope "notes/ok.md" 'Whole [[link]].
'
mkdir -p "$TMP/scope/.git" "$TMP/scope/notes/.git"
printf 'A [[wrapped\nlink]] in git internals.\n' > "$TMP/scope/.git/COMMIT_EDITMSG.md"
printf 'A [[wrapped\nlink]] in a nested git dir.\n' > "$TMP/scope/notes/.git/x.md"
printf 'A [[wrapped\nlink]] in a non-markdown file.\n' > "$TMP/scope/notes/data.txt"
run "$TMP/scope"
want_exit ".git (at the root and nested) and non-markdown files are skipped" 0

printf 'A [[wrapped\nlink]] in a note.\n' > "$TMP/scope/notes/bad.md"
run "$TMP/scope"
want_line "…while a note beside them is still read" "$TMP/scope/notes/bad.md:1: [[wrapped link]]"
[ "$(findings)" -eq 1 ] && pass "…and is the only finding" || fail "scope fixture should yield 1 finding, got $(findings)"

# --- raw archives -----------------------------------------------------------------
#
# A tier's archive: directory holds verbatim raw material, not notes. These fixtures
# are whole projects: a .commons.yml beside (or inside) the graph root, an archive
# holding the two things a real transcript holds that a note must not (a wrapped link
# and an unclosed fence), and a real note. The real note is what keeps "exit 0" from
# being earned by excluding too much.

printf '\narchives — a tier'"'"'s raw archive is not read\n'

# $1 = project name, $2 = .commons.yml content. Graph root is <project>/knowledge.
project() {
  mkdir -p "$TMP/$1/knowledge/notes" "$TMP/$1/knowledge/sources/transcripts"
  printf '%s' "$2" > "$TMP/$1/.commons.yml"
  printf 'Assistant said: see [[some quoted\nwrapped link]] in tool output.\n\n```bash\necho "a fence the export never closed"\n' \
    > "$TMP/$1/knowledge/sources/transcripts/2026-08-01-session.md"
  printf 'A whole [[link]] in a real note.\n' > "$TMP/$1/knowledge/notes/real.md"
}

project blockcfg 'graph:
  name: orchard
  root: knowledge/
sources:
  - name: session
    # archive: knowledge/   <- a commented-out value must not be read as config
    archive: knowledge/sources/transcripts/      # committed; durable copy
    gate: private
'
run "$TMP/blockcfg/knowledge"
want_exit "an archive named in .commons.yml (block form) is not checked: exit 0" 0
want_line "…and the run says which directory it did not read" \
  "check-wikilinks: not read (raw archive, named by archive: in $TMP/blockcfg/.commons.yml): $TMP/blockcfg/knowledge/sources/transcripts"
want_line "…and how many files that was" \
  "check-wikilinks: 1 archived file(s) skipped; archives are verbatim raw material, not notes."

printf 'A [[wrapped\nlink]] in a real note.\n' > "$TMP/blockcfg/knowledge/notes/bad.md"
run "$TMP/blockcfg/knowledge"
want_line "a note beside the archive is still checked" \
  "$TMP/blockcfg/knowledge/notes/bad.md:1: [[wrapped link]]"
[ "$(findings)" -eq 1 ] && pass "…and is the only finding" \
  || fail "archive fixture should yield exactly 1 finding, got $(findings)"

project flowcfg 'graph: { name: orchard, root: knowledge/ }
sources:
  - { type: session, resolve: export, archive: "knowledge/sources/transcripts/", gate: public }
'
run "$TMP/flowcfg/knowledge"
want_exit "an archive named in a flow-style, quoted entry is not checked either" 0

# root: "." — the config sits inside the graph root, as it does in a commons.
mkdir -p "$TMP/dotroot/sources/raw" "$TMP/dotroot/notes"
printf 'graph:\n  root: .\nsources:\n  - name: session\n    archive: sources/raw/\n' > "$TMP/dotroot/.commons.yml"
printf 'A [[quoted\nwrapped link]].\n' > "$TMP/dotroot/sources/raw/t.md"
printf 'Whole [[link]].\n' > "$TMP/dotroot/notes/n.md"
run "$TMP/dotroot"
want_exit "a config inside the graph root (root: .) is found too" 0

project nocfg ''
rm "$TMP/nocfg/.commons.yml"
run "$TMP/nocfg/knowledge"
want_exit "with no .commons.yml the same directory IS checked: exit 1" 1
want_line "…the wrapped link in it reported" \
  "$TMP/nocfg/knowledge/sources/transcripts/2026-08-01-session.md:1: [[some quoted wrapped link]]"
project outside 'sources:
  - name: session
    archive: docs/transcripts/
'
mkdir -p "$TMP/outside/docs/transcripts"
run "$TMP/outside/knowledge"
want_exit "an archive outside the graph root excludes nothing inside it: exit 1" 1

project covers 'sources:
  - name: session
    archive: knowledge/
'
run "$TMP/covers/knowledge"
want_exit "an archive: that covers the whole root exits 2, never clean" 2
project covers2 'sources:
  - name: session
    archive: .
'
run "$TMP/covers2/knowledge"
want_exit "…and so does one naming an ancestor of the root" 2

# --- fail-closed ------------------------------------------------------------------

printf '\nfail-closed — a check that cannot run is not a check that passed\n'

run
want_exit "no arguments exits 2" 2
run "$TMP/no-such-root"
want_exit "a missing root exits 2" 2
run "$TMP/clean/patterns/e.md"
want_exit "a file given as the root exits 2" 2
run "$TMP/clean" "$TMP/body"
want_exit "two roots exits 2" 2
run --frobnicate "$TMP/clean"
want_exit "an unknown option exits 2" 2
run --fix "$TMP/body"
want_exit "--fix is not an option: exit 2, never a rewrite" 2

# A finding is one line that starts with a path, so a name holding a newline could
# forge one. Refused, in a file name or a directory name.
graph nlfile "notes/ok.md" 'Whole [[link]].
'
printf 'Whole [[link]].\n' > "$TMP/nlfile/notes/evil
ok.md:1: [[forged]].md"
run "$TMP/nlfile"
want_exit "a file name containing a newline exits 2" 2
want_line "…naming the directory it is in" \
  "check-wikilinks: a file or directory name under $TMP/nlfile/notes contains a newline; rename it, nothing was checked"
want_no_finding "…and prints no finding line it could have forged" "forged"
mkdir -p "$TMP/nldir/a
b"
printf 'Whole [[link]].\n' > "$TMP/nldir/a
b/x.md"
run "$TMP/nldir"
want_exit "a directory name containing a newline exits 2" 2

# Read-only. The graphs with findings above were all checked at least once; none of
# their files may have changed, and nothing may have been created beside them.
before="$(cd "$TMP" && find body front alias two shell quote long -type f -exec cksum {} + | sort)"
for r in body front alias two shell quote long; do "$CHECK" "$TMP/$r" >/dev/null 2>&1; done
after="$(cd "$TMP" && find body front alias two shell quote long -type f -exec cksum {} + | sort)"
[ "$before" = "$after" ] && pass "checking a graph with findings changes no file and creates none" \
  || fail "the check wrote inside a graph"

mkdir -p "$TMP/empty"
run "$TMP/empty"
want_exit "a root with no markdown files exits 2 (nothing was checked)" 2

# --- result -----------------------------------------------------------------------

printf '\n'
if [ "$failures" -eq 0 ]; then
  printf 'all cases passed.\n'
  exit 0
fi
printf '%d case(s) failed.\n' "$failures"
exit 1
