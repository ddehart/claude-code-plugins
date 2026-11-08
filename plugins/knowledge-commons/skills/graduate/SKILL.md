---
name: graduate
description: "Review a receiving graph's eligible open questions — those with evidence from two or more domains — one at a time, and graduate, split, move claims, retitle, or hold each with human approval. Use when the user asks to graduate questions, review the commons backlog, see which questions are ready to become principles, or invokes /graduate. Triggers: graduate questions, /graduate, what's ready to graduate, review eligible questions, work the commons backlog."
argument-hint: "[graph path or question title]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Graduate

Walks the backlog of a **receiving graph** (usually the commons). A receiving graph collects evidence
from many domains by promotion, and its open questions are supposed to graduate once evidence from a
second domain lands under them. `promote` §7 catches a question at the moment a promotion makes it
eligible. This skill handles everything that was already eligible, and anything that was held or
reviewed and has since gained evidence.

The review itself, meaning the test, the moves, what each one writes, and the proposal, is defined once
in `${CLAUDE_PLUGIN_ROOT}/references/graduation.md`. **Read it before the first review.** This skill owns
only the walk around it: which graph, which questions, in what order, and when to commit and push.

## 1. Resolve the target

Locate the graph to walk from configuration alone. Read no maps or notes yet; that waits for the refresh
in §2.

1. **An explicit path**, if the caller gave one. A question title passed as the argument is not a path
   (see §5).
2. **The current project's graph**, if its `.commons.yml` declares a `question` attractor. This is only
   a candidate until §2's receiving-graph check confirms it.
3. **Otherwise, the graph named by the current project's `promotes-to:`.**

Check that the path holds a `.commons.yml`. If it doesn't, stop and report the exact path that failed to
resolve. Don't search for a commons elsewhere. A `promotes-to:` written on another machine can name a
path that doesn't exist on this one, and guessing would walk the wrong graph or none.

## 2. Refresh before reading anything

The target is usually shared with other machines and sessions. Before you read its maps or notes: if it's
a git repository with a remote, fetch and fast-forward, then say what came in, especially questions,
graduations, and claims. A stale clone can hold questions that already graduated elsewhere, and
everything below reads whatever is on disk.

**A fetch that succeeds is not the same as a target that is current.** Treat the refresh as failed when
the local copy didn't end up at the remote's tip: no remote, no network, a fetch error, or a fetch that
returns cleanly while the fast-forward is refused because the copy has diverged or the tree is dirty.
Check that `HEAD` actually moved to the remote tip, not merely that the fetch returned. On any failure,
continue, but say so, and every proposal must state it was weighed against a possibly stale copy.

**A dirty working tree stops the walk before any write.** Report what's uncommitted and stop. Don't stash
or commit someone else's work.

**Then confirm it's a receiving graph.** It must declare a `question` attractor, and its evidence notes
must carry `domain:` frontmatter; open two or three to check.

- If the candidate was the current project and it fails this check, it's a source graph whose questions
  settle another way. Switch to its `promotes-to:` target, check that path as in §1, refresh it, and
  check again.
- If the target fails the check, say it has no domain-counted questions and stop.

Then find the destination attractor: the attractor type other than `question`. If there is none, or more
than one, stop and ask.

## 3. Build the backlog

For every note in the question directory:

- **Skip graduated questions.** Use the test in `graduation.md` §4: a `> **Graduated` marker, or a
  `## so what` heading. Judge it from the note, never from the map line.
- **Count domains** per `graduation.md` §1. Eligible means two or more distinct `domain:` values.
- **Skip stamped questions** with no new evidence since the stamp, per `graduation.md` §7. The stamp may
  be on the map line or, for older holds, in the note body.

Order by distinct domain names descending, then claim count descending, then title. Show the reader:

- the backlog count;
- the first ten, each with its domain names, family count, and claim count;
- anything skipped for a broken link or a missing `## evidence`.

Expect the top of the list to be large, broad questions that split rather than graduate. That's
deliberate: fixing the catch-all questions early stops them absorbing more claims.

## 4. Walk it

One question at a time, in order:

1. Run the review in `graduation.md` and show the proposal, leading with counts, tests, groups, and the
   calls worth a second look (§9 there).
2. Wait for the reader: approve all, approve some, edit, not now, or stop.
3. **On approval:**
   - write the approved moves, each move's records, and the changelog bullet;
   - verify that every claim in the original ended up in exactly one place, and that every new or renamed
     note's links resolve;
   - commit, naming the paths (never `git add -A`), with a message such as
     `graduate: <question title>: <moves in a phrase>`.
4. **"Not now"** writes nothing. Move to the next question.
5. **"Stop"** ends the walk.

Nothing a review touches comes back in the same walk, because every touched question is stamped. A
split-off group that passed the test waits for the next walk or for new evidence.

Expect each review of a large question to take a while: reading every claim is the work. If the reader is
flagging, offer to stop. Committing after each review means stopping loses nothing.

## 5. A single question

If the argument is a question title rather than a path, resolve the target as in §1 and refresh as in §2.
Then review just that question, regardless of its place in the order. It still has to be eligible. If it
isn't (graduated, single-domain, or stamped with no new evidence), say which, and stop. On approval,
write and commit as in §4, then push as in §6.

## 6. Push and summarize

When the walk ends, whether it finished or was stopped, push if the target has a remote. Say plainly if
the push failed or was blocked. An unpushed review is invisible to every other machine.

**A rejected push means the target moved while you were walking.** Pull and rebase, then read what came
in before resolving anything. If the incoming commits touch a question you reviewed, an attractor you
created, or a map line you edited, don't resolve mechanically. Take that question back through the review
and re-propose. A conflict in a map usually means a review is now wrong, not that a merge needs doing.

Then summarize:

- questions reviewed;
- graduations, with the new notes' titles and steering lines;
- questions split off, claims moved, notes retitled;
- holds;
- what's left in the backlog.

For any new note that isn't yet steering, name `promote`'s instruction-tier branch as the next step. Don't
run it.
