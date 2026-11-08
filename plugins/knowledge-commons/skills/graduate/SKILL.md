---
name: graduate
description: "Review a receiving graph's eligible open questions — those with evidence from two or more domains — one at a time, and graduate each to a principle, split it, move claims, retitle, or hold, with human approval. Use when the user asks to graduate questions into principles, review the commons question backlog, see which questions are ready to become principles, or invokes /graduate. Triggers: graduate questions, graduate this question, /graduate, which questions are ready to graduate, review eligible questions, work the commons backlog. Not for turning a principle into a rule; that is promote's instruction-tier branch."
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

Decide which graph to walk **before refreshing anything**. Only the graph you settle on gets refreshed.
A source project you happen to be standing in must never be fetched, fast-forwarded, or checked for a
dirty tree on this skill's behalf.

1. **An explicit path**, if the caller gave one. A question title passed as the argument is not a path
   (see §5).
2. **The current project's graph**, if it passes `graduation.md`'s receiving-graph check (its opening).
   The check reads only `.commons.yml` and the frontmatter of two or three evidence notes, which are
   stable facts about the graph, so running it before the refresh is safe. The maps and questions are not
   stable; leave them for §3.
3. **Otherwise, the graph named by the current project's `promotes-to:`**, put through the same check.

Check that the chosen path holds a `.commons.yml`. If it doesn't, stop and report the exact path that
failed to resolve. Don't search for a commons elsewhere. A `promotes-to:` written on another machine can
name a path that doesn't exist on this one, and guessing would walk the wrong graph or none.

If the chosen graph fails the check, say it has no domain-counted questions and stop. Otherwise resolve
the destination attractor as `graduation.md`'s opening describes.

## 2. Refresh

Refresh the target exactly as `${CLAUDE_PLUGIN_ROOT}/skills/promote/SKILL.md` §1 describes, before
reading its maps or questions. That covers fetching and fast-forwarding, confirming that `HEAD` actually
reached the remote tip, and saying what came in. If the refresh failed or was refused, continue, but
every proposal must say it was weighed against a possibly stale copy.

**A dirty working tree stops the walk before any write.** Report what's uncommitted and stop. Don't stash
or commit someone else's work.

## 3. Build the backlog

The backlog is every question that is **eligible for review** as `graduation.md` §7 defines it. Apply
that definition; don't restate or vary it here. Build it cheaply, in this order:

1. **Map the claims once.** A single search over the claim directory for `^(domain|date):` gives every
   claim's domain and date. Use this map for the whole walk, including the domain counts inside each
   review (`graduation.md` §1). Don't reopen claims just to read their frontmatter.
2. **Drop questions that aren't open** (`graduation.md` §4) before anything else. Graduated questions
   tend to have the most domains, and they are the cheapest to rule out.
3. **Prefilter on suffixes.** Skip a question whose `(domain)` suffixes are all present and name one
   domain; any disagreement with the frontmatter surfaces when a question is reviewed. For the rest,
   count domains from the claim map.
4. **Apply the stamp check** from the map line, the question's claim count, and the claim map's dates.

Order by distinct domain names descending, then claim count descending, then title. Show the reader:

- the backlog count;
- the first ten, each with its domain names, family count, and claim count;
- anything skipped for a broken link or a missing `## evidence`.

Expect the top of the list to be large, broad questions that split rather than graduate. That's
deliberate: fixing the catch-all questions early stops them absorbing more claims.

## 4. Walk it

**Read once per walk, not once per review:** every destination note's `## so what` (for `graduation.md`
§2's third requirement) and `~/.claude/rules/*.md` (for its §8). When a review writes a new destination
note, add it to what you've read.

Then, one question at a time, in order:

1. Run the review in `graduation.md` and show the proposal (§9 there).
2. Wait for the reader: approve all, approve some, edit, not now, or stop.
3. **On approval:**
   - write the approved moves, their records, and the changelog bullet;
   - verify that every claim in the original ended up in exactly one place, and that every new or renamed
     note's links resolve;
   - commit, naming the paths, with a message such as `graduate: <question title>: <moves in a phrase>`.
4. **"Not now"** writes nothing. Move to the next question.
5. **"Stop"** ends the walk.

Stamps (`graduation.md` §7) keep anything a review touched from coming back in the same walk.

Expect each review of a large question to take a while: reading every claim is the work. If the reader is
flagging, offer to stop. Committing after each review means stopping loses nothing.

## 5. A single question

If the argument is a question title rather than a path, resolve the target as in §1 and refresh as in §2.
Then review just that question, regardless of its place in the order. It still has to be eligible. If it
isn't (graduated, single-domain, or stamped with no new evidence), say which, and stop. On approval,
write and commit as in §4, then push as in §6.

## 6. Push and summarize

When the walk ends, whether it finished or was stopped, push if the target has a remote. Say plainly if
the push failed or was blocked. An unpushed review is invisible to every other machine. Handle a rejected
push as `promote` §6 does: pull, rebase, read what came in, and take any question the incoming commits
touched back through the review instead of resolving the conflict by hand.

Then summarize:

- questions reviewed;
- graduations, with the new notes' titles and steering lines;
- questions split off, claims moved, notes retitled;
- holds;
- what's left in the backlog.

For any new note that isn't yet steering, name `promote`'s instruction-tier branch as the next step. Don't
run it.
