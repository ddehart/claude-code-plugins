# Spec: a mechanical check for wrapped wikilinks

**Status:** Implemented on `claude/kc-wikilink-check-31628d`, draft PR for review; amended twice on
2026-11-25 after review. The second amendment removed the fix mode (W17), which supersedes W8, W15
and W16 and part of W11
**Date:** 2026-11-24
**Plugin:** `knowledge-commons` v0.9.1 → v0.10.0
**Related:** [`knowledge-commons-plugin-references.md`](./knowledge-commons-plugin-references.md) (why
generated skills reach plugin files through a helper skill) ·
[`knowledge-commons-patch-mechanism.md`](./knowledge-commons-patch-mechanism.md) (deltas, D8 fields,
D23 anchors)

## Problem

Graph notes are prose hard-wrapped near 110 columns, written by the generated `process` and
`knowledge-graph` skills. A long `[[note title]]` that straddles the wrap column gets split across two
lines. Obsidian then renders literal brackets and no resolver follows the link. The note still reads
fine in an editor, so nothing surfaces it.

It recurs. The devbox graph was repaired by hand in September 2026 and had 32 more by 2026-11-22; a
review that day found the same defect in four other graphs at once. Nothing in the plugin mentioned
wrapping or keeping a link on one line, and the plugin's only executable was the secret scanner.

The structural condition is that the rule has to be remembered at the one moment the writer's attention
is on the sentence. This graph family's own pattern notes record that guidance which is present and read
does not fire at the moment it is needed. A sentence in the conventions would be that guidance again.

## Interaction model

Nobody invokes this. A generated skill runs it at the end of a run that wrote notes and reports the
result; the human sees a plain statement in the change summary when the graph is not known to be
clean, with each finding the run left alone. It is a check on the result, after the writes. It
does not gate them, and the plugin's "no validator in the write path" stance stands.

## Decisions

**W1. A script with an exit code, beside `scan-secrets.sh`.** `scripts/check-wikilinks.sh <graph-root>`
prints `file:line: [[link text]]` per finding and exits 1; 0 is clean; 2 means it could not run. Bash
plus POSIX awk and find, nothing else. Tested under gawk, mawk, and busybox awk.

**W2. Detection is on raw text.** Whether the target resolves is never consulted. A count taken only
among resolvable targets missed a wrapped link in practice.

**W3. Frontmatter is read like the body.** `supports:` lists wrap too.

**W4. Code is skipped: fenced blocks and inline code spans, including a span that itself wraps.** Notes
quote the broken form as an example, and a note documenting this defect has to be able to pass. The cost
is that a real link written inside backticks is not checked, which is correct: it is not a link there
either. Indented (four-space) code blocks are not recognized, because indented list continuation prose
is far more common in a graph than indented code, and treating it as code would hide real links.

**W5. A link ends at a blank line.** The paragraph is the unit. A stray `[[` and an unrelated `]]`
paragraphs apart are not a link; neither is an unclosed `[[` followed by a whole link.

**W6. An unclosed code fence is a finding.** Everything after it is code to a renderer, so it is not
checked, and a check with an unread region does not get to report clean. Measured on the devbox graph
(503 notes): zero, so this adds no noise there.

**W7. Zero markdown files is exit 2.** It is a wrong root far more often than an empty graph.

> **W8 superseded 2026-11-25 by W17:** the fix mode was removed before release. Kept as design history.

**W8. `--fix` is included.** It rejoins by replacing the line break and the indentation after it with
one space, and changes nothing else; the test proves each fixed file is whitespace-equivalent to its
original. It declines a link whose continuation line starts with a blockquote marker (joining would
leave or drop a `>`, which is not whitespace-only), a link crossing more than one line break (a
guess), and text that does not read as a note title (W15). Its exit code comes from re-running the check on the result. It does not re-wrap the joined
line, which runs long; that is the convention (W11).

**W9. Reached through a helper skill, `knowledge-commons:check-wikilinks`.** Same reason as
`scan-secrets`: a project skill gets no `${CLAUDE_PLUGIN_ROOT}`, and a path into the plugin's install
is a snapshot of one version on one machine. Not user-invocable, matching the other two helpers.

**W10. Anchors.** A commit is not usable as the anchor: a `/process` run does not stage or commit at
all (the session commits graph notes afterward), and a capture is not tied to a commit either.
- `process`: the start of the report step (`## 12. Report`), after the last write. No earlier stage sees
  every write: the run step, the sinks, and the stamp all write notes.
- `knowledge-graph`: the Workflows section (`## Workflows`), as the last capture step plus one statement
  covering every workflow there that writes. Not the session protocol's end-of-session summary: a
  capture is a numbered procedure followed at the moment a note is written, and a session rarely has an
  end anyone marks.

Both headings exist in every generated skill on devbox as of 2026-11-24 (14 `process`, 15
`knowledge-graph`, counting worktree copies).

**W11. The check covers the whole graph, not the run's own notes.** A wrapped link from a hand edit or
an earlier run is caught by the next run. ~~With `--fix` that means a run may rejoin links in notes
outside its approved plan; the change is whitespace-only and is listed under corrections.~~ Superseded
by W18: a run repairs only the notes it wrote and reports the rest.

**W12. The rule is stated once in `references/graph-conventions.md`** (Naming): a wikilink stays on one
line; let the line run long.

**W13. Two deltas, version 0.10.0 (minor: a new skill).** `report-wrapped-link-check` and
`kg-wrapped-link-check`. Each `satisfied-test` fails a section that states the rule without invoking
the check, since that is the state the delta exists to change.

**W14. Raw archives are not read, and so never written.** Added after review. A source tier too large
to inline keeps its material in a committed directory named by that tier's `archive:` key in
`.commons.yml`, and those files are verbatim session transcripts, not notes. Run against
`~/projects/daily-briefing/knowledge`, the first version reported two unclosed fences inside archived
transcripts and nothing else. Once the deltas rolled out, every run there would have ended "not known
to be clean", with the template telling it to hand-edit a verbatim archive. The location is
configurable and differs across live graphs (`knowledge/sources/transcripts/`, `knowledge/sources/raw/`,
and `docs/transcripts/` outside the graph), so the script reads it: the nearest `.commons.yml` at or
above the root, every `archive:` value, by pattern (block and flow YAML both). It does not take the path
from the calling skill, because that would put the exclusion back in prose a run has to remember.
~~`--exclude <dir>` covers a graph with no config.~~ (Removed with W21: nothing called it.) Every
skipped directory is printed, with a file count.
An exclusion that covers the whole root is exit 2. The templates, both deltas and their
`satisfied-test`s, and the conventions line all say archives are excluded and never edited.

> **W15 and W16 superseded 2026-11-25 by W17.** Both existed only to make the fix mode safe. Kept as
> design history. What survives of W15: a multi-line shell test outside code is still reported, and
> whether it is a link to rejoin or code to fence is the reader's call.

**W15. `--fix` declines text that does not read as a note title; the check still reports it.** Added
after review. A multi-line shell test quoted outside a code block (`if [[ -f x &&` / `-d y ]]; then`)
has the exact shape of a wrapped link, and rejoining it rewrites quoted code. The test: the text
contains `&&`, `||`, `==` or `!=`, or starts with a test operator (`-f`, `-z`, …), `$`, `!`, `(` or a
quote. It is broad on purpose and can trip on a real title (one starting with `$20`, say), which is why
it gates only the fix. A wrongly declined fix costs one hand edit; a wrongly skipped finding is a broken
link nobody hears about. The hand decision is to rejoin it, or to put the code in a span or fence.

**W16. `--fix` replaces a note by rename.** Added after review. It writes a temporary file beside the
note (`cp -p` first, so the mode carries over) and renames it over the original, so an interruption
leaves the old note or the new one. The first version wrote through the note to keep hard links, which
git working trees do not have; a truncated note is the worse failure. Hard links are not preserved.

**W17. No fix mode: the script is read-only.** Decided by Derek on 2026-11-25, after a second review.
Reasons: once the graphs are clean (all six were that day) a run sees at most a few findings, each with
file and line, and the calling agent can rejoin one with a single edit. The fixer was the only code in
the script that wrote, and to be safe it needed a heuristic for what is not a title (W15), an atomic
replace (W16), two declined shapes (W8), and a promptless Bash grant that reached a writer. Three
reviewers traced the PR's size, both of its write-related security findings, and the question of
rewriting notes a run did not write (W11) back to it. The helper skill's `allowed-tools` grant now
reaches a script that cannot change a graph. A fix mode can return as its own change if findings prove
frequent.

**W18. A run repairs only what it wrote.** On findings in notes the run wrote or edited, it rejoins
each by hand and checks once more. A finding in a note it did not touch is not edited: it is listed in
the summary for the user, and the summary says the graph is not known to be clean. An archived file is
never edited. If the check could not run (exit 2, or the skill unavailable), the summary says so in
those words. Both templates and both deltas carry this; the deltas' `satisfied-test`s fail a section
that says to rejoin every finding wherever it is.

**W19. awk runs in the C locale.** The program only looks for ASCII (`[[`, `]]`, backticks,
whitespace), so byte offsets are self-consistent, and in a UTF-8 locale awk re-walks multibyte text on
every `index()` and `substr()`. A fixture with multibyte text before, inside and after a wrapped link
(and in the file name) pins the line number and the text.

**W20. The scanner is one pass, with no size cap.** The first scanner built each paragraph into one
string and re-copied the remainder per link and per code span: 35 s on a 200 KB line of `[[`. A cap on
paragraph size was the other option and was rejected because the commons' claims map is already one
139 KB paragraph with 725 links and grows with every promotion, so any cap small enough to bound the
work would one day make that graph permanently "not checked". The scanner now lists a paragraph's
backtick runs once (with, for each, the next run of the same length), then walks its lines feeding the
text outside code spans to a function that tracks at most one open link. Two bounds follow from the
design: a `[[` not closed within 1000 bytes is not a link (a title is a file name; the bound also caps
what a stray opener costs), and nothing is concatenated per token. Same 200 KB shape after: 0.05 s
(gawk), 0.01 s (mawk), 0.20 s (busybox). Findings are identical to the old scanner's on all six graphs,
this repo's graph, and `docs/`.

**W21. Smaller surface.** A collected path containing a newline is exit 2, naming the directory: a
finding is one line that starts with a path, and such a name could forge one. `--exclude` is removed
(nothing called it, and the skill passes nothing extra). `archive:` is resolved only as a
project-relative directory, which is what the conventions define it as. The script header is cut to
usage, format, exit codes and what is read, with this spec holding the reasons. The templates carry the
instruction only; the reasons stay here and in the delta `rationale` fields, because a generated skill
is reloaded on every run. The archive clause is dropped from both `satisfied-test`s, since the script
never lists an archived file.

**Version stays 0.10.0.** Nothing was released between the amendments, and the capability is still one
new skill.

## Verification

- `scripts/test-check-wikilinks.sh`, 70 cases: wrapped link in body, in frontmatter, with an alias, two
  sharing a line, inside a blockquote, across more than one line break, with multibyte text around
  it, a shell test, several files in one root, a path with spaces; clean file; backtick and tilde
  fences; inline code on adjacent lines, a wrapping code span, double backticks, an unpaired backtick;
  an unclosed fence; unclosed `[[` mid-file and at end of file; a `[[` open past 1000 bytes; a
  50,000-line paragraph; `.git` and non-markdown files skipped; archives named in block and flow
  config, with the config inside the root, with no config, outside the root, and covering the root;
  a newline in a file name and in a directory name; no file changed by a check; every exit-2 path.
- Shown to test something: the test fails with the script absent, and with each of twelve behaviors
  removed from a copy (set `CHECK_WIKILINKS` to the copy), the cases for that behavior fail. Switching
  the locale back to UTF-8 fails nothing, as intended: W19 changes speed, not output.
- Real data, read-only, 2026-11-25: devbox, commons, daily-briefing, email-triggers, log-archaeologist
  and airbnb-prep all exit 0. `~/commons` (970 notes): 2.2 s before W19 and W20, 0.10 s after.
- Script size: 475 lines with the fix mode, 315 without.
- Not tested on bash 3.2 or BSD userland; the script avoids features they lack, but no macOS run backs
  that.

## Left open

- **A pre-commit hook would see more.** It would catch hand edits and the `promote` and `graduate`
  writes at the moment they are committed, which the generated skills' anchors do not. It is not the
  first delivery because hooks are per-clone, the plugin has no installer to place one, and some graph
  repos already use the hook slot (`secret-scan`). The script is read-only and takes one argument, so
  a hook can call it unchanged.
- **`promote` and `graduate` write notes into the receiving graph and do not run the check.** The
  commons is written mostly by them and has no `process` skill. Its `knowledge-graph` skill gets the
  check through the delta, which covers direct captures only. Both are plugin skills, so wiring them
  needs no delta.
- **Cross-graph links.** A link from a project graph to a commons note does not resolve locally. This
  check never resolves targets, so it neither helps nor hinders; a convention for those links is not
  designed here.
- **The generated `knowledge-graph` skill's frontmatter has no `Skill` entry in `allowed-tools`,** so
  invoking the helper may prompt once. It already invokes `knowledge-commons:conventions` under the
  same frontmatter, and a delta cannot patch frontmatter (anchors are `##` headings).
- **Existing graphs** get the check only when `/graph-patch` is run in each. Not done here.
