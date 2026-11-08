# Spec: knowledge-commons question graduation

**Status:** Ready to build. Interviewed 2026-11-08. Phase 0 passed the same day (5 of 5 approvable),
and its findings are folded in (see "Phase 0 findings"). Not built.
**Date:** 2026-11-08
**Plugin:** `knowledge-commons` v0.6.0 → v0.7.0
**Related:** [`knowledge-commons.md`](./knowledge-commons.md) (founding spec),
[`knowledge-commons-patch-mechanism.md`](./knowledge-commons-patch-mechanism.md) (shape reference; the
`/graph-patch` mechanism this spec decides *not* to use, see R16)

## Problem

A question in a receiving graph (today, only the commons at `~/commons`) is supposed to graduate to a
principle once evidence from a second domain lands under it. **Nothing prompts anyone to do it.**

Measured 2026-11-08 against `~/commons` at `bec4085`:

| Quantity | Count |
|---|---|
| Question notes in `questions/` | 142 |
| … already marked graduated (`> **Graduated …` blockquote) | 3 |
| … open | 139 |
| … open with claims from two or more distinct domains | **72** |
| Principle notes in `principles/` | 4 |

The commons has moved since (one more claim, at `5398373`, by the 09:39 check), so these are a snapshot.
The count of 72 reads each evidence line's `(domain)` suffix; R7 changes the counting source to claim
frontmatter, which Phase 0 re-measures.

The only trigger today is a one-line awareness offer (*"Worth promoting [question] to a principle now
that [domain] backs it too?"*) in the commons' own generated skill,
`~/commons/.claude/skills/knowledge-graph/SKILL.md`. That skill loads only in sessions opened inside
`~/commons`. Promotions, the only thing that adds evidence to the commons, run from source-graph sessions
(devbox, daily-briefing, this repo), so the offer never fires. The superseded commons spec
(`~/commons/docs/specs/knowledge-commons-spec.md`) planned a linter that would flag two-domain questions.
The plugin era dropped the validator, and nothing replaced it.

### Two contradictory descriptions of what graduation writes

The plugin's documentation says a question graduates **in place**:
`references/graph-conventions.md` ("it's promoted in place to a proper attractor") and `promote` §3
("Questions graduate in place… check whether it still carries `## question` or now carries `## so
what`").

Every real graduation did something else. The four principles in the commons were each written as a
**new note in `principles/`**, with a stance-shaped title and a rewritten `## so what`. The source
question note was **kept** in `questions/`, still headed `## question`, with a blockquote under the
heading:

```markdown
## question
> **Graduated 2026-10-17** to [[the unit a quantity is stated in decides what it is weighed against before any number is chosen]], on evidence from commonplace and wellstead, after
> one claim was split out to [[does a gain last when the party paying for it can still respond]]: …
```

The claims moved with it: their `supports:` frontmatter was repointed at the principle (all five of that
question's claims now support the principle; none still names the question). The question's map line
stayed in `maps/questions.md`, re-annotated "graduated 2026-10-17 to a principle on …". No question note
in the commons carries `## so what`.

**This contradiction is a live bug.** `promote` §3 decides whether a question is still open by looking
for `## so what`. The three graduated questions never got that heading, so `promote` reads them as open
and can attach new claims to questions that already became principles. The changelog records one such
near-miss, caught only because the session read the note's blockquote rather than trusting the heading: a
claim headed for *why does a confident prior displace a cheap check at the moment of acting*, which
"still carries a `## question` heading but graduated on 2026-07-20" (`~/commons/changelog.md`, the entry
just above the 2026-08-15 one).

### Two domains is a prompt to check, not a signal to graduate

The commons' changelog (2026-07-20, "reviewed the three eligible questions") records what happened the
first four times eligibility was reviewed: **one clean graduation, two splits, one bad attachment that
was reverted.** Its finding: a question broad enough to collect claims quickly is broad enough to collect
claims that don't share a mechanism, so density correlates with conflation. It proposed a test, applied
successfully on the next graduation: *state the single mechanism and the single remedy the claims share,
in one sentence each; if that takes more than one sentence, split first.* This spec builds that test in
(R5).

## Goals

- Make an eligible question visible at the moment it becomes eligible, from the session that made it so.
- Give the 72-question backlog a way to be worked through, one question at a time, without re-raising
  questions already reviewed.
- Settle one documented shape for what a graduation writes, matching what the commons already does.
- Fix `promote`'s graduated-question check.

## Non-goals

- **Source-graph questions** (R3). This repo's `knowledge/questions/` and its siblings graduate into a
  `decision` or `pattern` against each question's own "what would settle it" clause, with single-domain
  evidence. Domain counting doesn't apply. They keep graduating by hand.
- **Principle → rule.** `promote` §4 (the instruction-tier branch) is unchanged and stays separate. A
  graduation may *name* §4 as a next step (R13); it never runs it.
- **Automatic graduation.** Every write passes a human approval, as in `promote` §5.
- **A linter or scheduled job.** The superseded spec's validator is not revived.
- **Fixing `promotes-to: ~/Developer/commons`** in this repo's `.commons.yml` (a Mac path; on devbox the
  commons is `~/commons`). A Todoist task already tracks it. This spec only says how the skills behave
  when that path doesn't resolve (R10).

## Decisions

### Placement

**R1. Two entry points that share one review procedure.** (a) A new final section of `promote`, run
after a promotion is written, which reviews a question the promotion just made eligible. (b) A new
plugin-level `graduate` skill that walks the backlog. Both execute the same review procedure, written
once in a new reference file, `references/graduation.md`, which each skill reads.
*Rationale:* `promote` is the only thing that adds evidence to a receiving graph, so it is the moment a
question becomes eligible, and the session that ran it is the one that can see the new evidence. But
promote only fires on new evidence, so the 72 already-eligible questions need a separate walk. One
reference file keeps the two from drifting, the failure the patch-mechanism spec was built around. (Agreed
with Derek before the interview; the shared reference is this spec's addition.)

**R2. Separate from `promote` §4.** Graduation is question → principle inside a graph. §4 is principle →
rule file across tiers. Different inputs, different screens, different targets.
*Rationale:* agreed before the interview. Folding them together would make every graduation feel like a
step toward a rule, and the commons' own finding is that most principles are already steering (R13).

**R3. Receiving graphs only.** A graph qualifies when it declares a `question` attractor **and** its
evidence notes carry `domain:` frontmatter (i.e. evidence arrives by promotion). Today that is only the
commons. Anything else: `graduate` says the graph has no domain-counted questions and stops; `promote`'s
new section doesn't run.
*Rationale (Derek, interview):* source-graph questions graduate on a per-question settle clause, not a
domain count, and there are five of them. A second test would double the procedure for a population
that doesn't need it.

### What a review can conclude

**R4. A review proposes a set of moves, not one outcome.** It partitions the question's claims into
groups by shared mechanism and remedy (R5), then proposes one move per group, plus at most one move for
the original note itself. The moves:

| Move | Applies to | When | Writes |
|---|---|---|---|
| **Graduate** | The whole question, or one group | The group passes R5 and has two or more domains (R7) | R6 |
| **Split off** | A group | It passes R5 but belongs in none of the existing notes | A new question note (R19), evidence lines moved (R20), each moved claim's `supports:` repointed, a map line for the new question |
| **Move to an existing note** | A group of one or more claims | An existing question or principle already states the group's mechanism (checked against its text, not only its title: R5) | Evidence lines moved (R20); `supports:` repointed; both notes' map annotations updated if they no longer fit |
| **Stay** | The group left in the original | Always exactly one, possibly empty after a full graduation | Nothing beyond R19's retitle and the split marker |
| **Retitle** | The original note | What stays is narrower than the title, so the title would keep attracting claims that belong elsewhere | R19 |
| **Hold** | The whole question | Coherent but not ready, with a stated reason | Map annotation only (R8) |
| **Not now** | The whole review | The reader wants to skip without deciding | Nothing. It stays in the backlog |

The reader approves the set at once or move by move (`y / edit / approve some / not now / stop`). Moves
that aren't approved are dropped, and the remaining ones must still leave every claim in exactly one
place. A group that passes R5 but isn't graduated in this review stays in the backlog under R10.

*Rationale (Derek, interview and Phase 0):* the interview settled on four alternative outcomes (graduate,
split, hold, detach). Phase 0 showed that real reviews combine them. Four of five drafts split a question
*and* moved claims to an existing question, and the fifth moved one claim out and then graduated the
rest, as the commons' own 2026-10-17 graduation did. The old "detach" covered only a claim whose
attachment created the eligibility, but most misfits weren't that: the questions had many domains without
them. Derek chose a set of moves approved together or one by one.

**R5. The coherence test runs before any graduation is proposed.** State the single mechanism the
question's claims share, and the single remedy, in one sentence each. If either takes more than one
sentence, or a claim doesn't fit the sentence, the claims are grouped and each group is tested on its
own (R4). Three requirements keep the test from passing on generality:
1. **The mechanism sentence must say more than the question's title.** A sentence that restates the title
   fits every claim and excludes nothing. Name where or how the effect enters.
2. **Each claim's own remedy must be an instance of the remedy sentence.** Read each claim's remedy. If
   two contradict ("widen the unit" against "widening does nothing, change the question"), the test fails,
   however the sentence is worded.
3. **The remedy is checked against existing principles' `## so what` text**, not only their titles. A
   group whose remedy is already a form of an existing principle is a move to that principle, not a new
   principle.

Show the sentences in every proposal, including holds and failed attempts, so the reader judges the test
and not just the verdict.
*Rationale:* the commons' 2026-07-20 finding (see Problem). Phase 0 added the three requirements. All five
drafts found that a title-level sentence "passes", and three asked for the rule to be explicit. Two
caught overlaps with an existing principle only by reading its body. Derek accepted all three.

**R6. A graduation writes a new attractor note and keeps the question as its record.** Specifically:
1. **New principle note** in the destination attractor's directory (R9). Title: a stance stated as a
   sentence, not a question. Frontmatter follows the target's existing notes of that type (in the commons:
   `genitor: "[[principles]]"`, `tags:`; principles carry no `date:` and no `supports:`). Body:
   `## so what` (the held stance, its mechanism and remedy, its limits, and the steering line from R13),
   then `## evidence` listing every claim with its `(domain)` suffix.
2. **Each claim's `supports:`** is repointed from the question to the principle.
3. **The question note is kept.** Its body and evidence list are left as they are. Insert directly under
   `## question`: `> **Graduated YYYY-MM-DD** to [[principle title]], on evidence from <domains>.`, plus
   a clause for any split that preceded it. A question note may lack a `## question` heading (at least
   one, *when is detecting a problem worse than not detecting it*, opens with an H1 instead); insert the
   marker under the note's first heading in that case.
4. **Maps.** Add the principle to the destination map (`maps/principles.md`) in alphabetical position
   with a one-clause "so what" annotation, per `graph-conventions.md`. Keep the question's line in
   `maps/questions.md` and replace its annotation with `graduated YYYY-MM-DD to a principle on <one
   clause>`.
5. **Changelog** entry (R8) and **commit** (R11).

*Rationale (Derek, interview):* codifies what all four real graduations did. A question title and a
principle title are different kinds of sentence, and the question note with its history ("split once,
then graduated") is the most useful record the commons has of how a stance formed.

**R7. Distinct domains are counted from claim frontmatter.** For each item in the question's
`## evidence` list, take the **first** `[[link]]` on the item (later links, and links inside commentary
paragraphs, are annotations), open that claim, and read its `domain:`. The question is eligible when there are two or more
distinct values. If an evidence line's `(domain)` suffix disagrees with the claim's `domain:`, or is
missing, report it in the proposal and count the frontmatter. Never fix it silently. A claim with no
`domain:` counts as unknown, is reported, and doesn't add to the count.
*Rationale (Derek, interview):* `promote` writes `domain:` from the source graph's `graph.name`, so it is
the authoritative value. All 650 claims carry it (checked 2026-11-08). The suffix is hand-typed
duplication.

**Families are shown, not counted.** Domain names that share their first hyphen-separated segment form a
family (`devbox`, `devbox-daily-digest`, `devbox-log-archaeologist`, `devbox-service-health-monitor`;
`aiwyn`, `aiwyn-macbook`). Every proposal states both numbers, e.g. "13 domain names, 9 families," and
says when a group is eligible only because of a sibling in the same family. Eligibility and R12's
ordering use names.
*Rationale (Derek, Phase 0):* related projects aren't independent observers, which the commons noted on
2026-07-20 ("projects, not observers"), and two of proposal 2's new questions were eligible only through
a devbox sibling. Derek chose to keep counting names and make the family visible, so the reader can
weigh it.

### State

**R8. Where each review is recorded.**
- **Hold:** map annotation only, appended to the question's line in `maps/questions.md`, in the existing
  form: `*(eligible; reviewed YYYY-MM-DD and held: <reason in one clause>)*`. A new review replaces any
  previous review annotation on that line; it doesn't stack. A hold with no reason given is recorded as
  `held: no reason given`.
- **Any other approved review** (one with at least one graduate, split-off, move, or retitle): the map
  edits and note-level markers its moves write (R4, R6, R19), a review stamp on the map line of every
  question the review touched (R10), and **one dated bullet appended at the end of `changelog.md`**, in
  the form the commons' promotions use:
  `- YYYY-MM-DD — reviewed [[question]]: <moves, with the notes they wrote or touched as links>. <the R5
  sentence or sentences in a clause>.` One bullet per review, whether it ran in a `graduate` walk or in
  `promote` §7. A `promote` run's review bullet is separate from its promotion bullet.

*Rationale (Derek, interview and Phase 0):* holds are frequent and low-information, so they belong in the
map, where the next walk reads them. The first draft of this decision said to prepend a `##` prose entry.
Phase 0 found that wrong for current practice: the commons has two live styles, and since September 195
dated bullets have been appended at the end of the file, including every promotion since 2026-10-31 and
the 2026-10-17 graduation itself. Prose `##` entries at the top stop at 2026-10-30. Derek chose the
bullet.

**R9. The destination attractor is the target's attractor type other than `question`.** The commons
declares `principle` and `question`, so it resolves to `principle`, `principles/`, `maps/principles.md`.
If a receiving graph declares zero other attractor types, or more than one, stop and ask which one
graduations go to. Don't guess, and don't add a `.commons.yml` key (graph-init's Never section restricts
keys).
*Rationale:* no config field names the graduation destination today. One unambiguous case covers the
only receiving graph that exists.

**R10. A reviewed question comes back only when new evidence lands.** Every question a review touched
carries a review stamp on its map line: the hold form in R8, or `*(reviewed YYYY-MM-DD: <one clause on
the moves>)*` for the original, each split-off question, and each existing question that received
claims. A newer review replaces the stamp rather than adding to it. A stamped question re-enters the
backlog, and becomes eligible for `promote`'s review again, only when one of its claims has a `date:`
later than the stamp, or (for a question that received moved claims) when it gains a claim it didn't
have at the stamp. There is no calendar expiry.

**Older holds written in the note body**, not on the map line (at least one: *what makes a measurement
report its instrument instead of its subject* carries "Eligible, reviewed 2026-07-22 and held" in its
body), count as stamps for this rule. When the walk finds one, it moves the stamp to the map line as part
of that review.
*Rationale (Derek, interview; widened in Phase 0):* a review records a judgment about the evidence, and
only new evidence can change it. Claim `date:` is the promotion date (promote §2), so "claim newer than
the review" is exactly "evidence that arrived after the review." The interview applied this to holds
only. Phase 0 showed that a split's remainder, and a split-off group that passed R5, are immediately
eligible again, so without a stamp a walk loops on what it just reviewed. A claim moved into an existing
question keeps its old `date:`, so the "gains a claim" clause is what lets the receiving question come
back.

### Running it

**R11. `graduate` runs from anywhere and walks one receiving graph.** If the current project's graph is a
receiving graph (R3), walk it. Otherwise walk the graph named by its `promotes-to:`. A caller may name a
path explicitly. Before reading anything, **refresh the target exactly as `promote` §1 does**:
fetch, fast-forward, confirm `HEAD` reached the remote tip, say what came in, and say plainly if the
refresh failed, was refused, or wasn't possible. If `promotes-to:` doesn't resolve to a directory with a
`.commons.yml` (e.g. this repo's `~/Developer/commons` on devbox), stop and report the path. Don't search
for a commons.
*Rationale (Derek, interview):* you shouldn't have to open a commons session to graduate commons
questions. The refresh comes before any read for the same reason as in `promote`: a stale clone can hold
questions that already graduated.

**R12. The backlog walk.** Eligible = open (judged from the note per R15, never from the map line, whose
graduated annotations vary in wording), two or more distinct domains (R7), and not stamped, or stamped
with newer evidence (R10).
1. Show the count and the first ten in order, with each one's domains and claim count.
2. Order: distinct domains descending, then claim count descending, then title.
3. Review one at a time: show the R5 sentences, the proposed moves and their full writes, and wait for
   approval (R4).
4. **Commit after each approved review** (name the paths; never blanket-stage), with its changelog bullet
   (R8). **Push when the walk ends**, whether it finished or was stopped, and say plainly if the push
   failed. A rejected push follows `promote` §6: pull, rebase, read what came in, and re-review any
   question it touched rather than resolving mechanically.
5. Everything a review touched is stamped (R10), so nothing it produced comes back in the same walk
   unless new evidence arrives.

*Rationale (Derek, interview; confirmed after Phase 0):* breadth of corroboration is the strongest
graduation signal, and the densest questions are the ones most likely to need a split, which is worth
doing early. Phase 0 confirmed the cost: all five of the top questions split, and none graduated whole.
So the first walk is mostly restructuring. It produces more questions than principles at first, and each
review took an agent 5–10 minutes. Derek kept this order anyway, to fix the big catch-all questions
before they absorb more claims. Committing per review means an interrupted walk loses nothing. Pushing
once avoids a push per question across a long walk.

**R13. Every graduation checks the instruction tier.** Read `~/.claude/rules/*.md` and judge whether a
rule already encodes the new principle. Record the answer in the principle's `## so what` and its map
annotation: `**Already steering** as <rule-name>.md` or `**Not yet steering.** No rule encodes this.` For
a not-yet-steering principle, the proposal names `promote` §4 as the next step and does not run it. When a
rule covers part of the principle, keep the binary line and add one sentence naming that rule and the
part it covers, so the uncovered part is what §4 would be asked about. (Phase 0's one graduation wrote
"**Not yet steering.** … `verify-first.md` covers the reader's half"; Derek preferred that to a separate
"partly steering" form.)
Leave the principles map's standing note alone unless this graduation contradicts what it says, in which
case propose the edit.
*Rationale (Derek, interview):* the commons found that three of its four principles were already
steering when they graduated. Keeping that visible per principle is what the standing note was
reaching for.

**R14. `promote` gains a final section, §7 "Graduation check."** It runs after §6 has written, committed,
and pushed the promotion, and only when all of these hold: the target is a receiving graph (R3); the
association was outcome 2 (attached to an existing open question); and after the attachment that question
is eligible (R7) and not stamped without newer evidence (R10). It then runs the review procedure for that
one question in the same session. On approval it writes the approved moves in the target, commits
**separately** from the promotion, and pushes. "Not now" writes nothing; the backlog walk will find it.
Groups the review created or left eligible are stamped (R10) and wait for the backlog walk or new
evidence; §7 never chains into a second review.
Outcome 1 (supports an existing principle) and outcome 3 (new question) never trigger it: a new question
has one claim, and principles aren't graduated again. §4 runs never trigger it.
*Rationale (Derek, interview):* the graduation lands while the session that produced the evidence is
still open. A separate commit means a graduation that gets rejected or reverted doesn't take the
promotion with it. The trigger is "eligible and not reviewed since its newest evidence," which is
broader than "first claim from a second domain." The broader form covers two cases the narrow one
misses: a held question that gains new evidence (R10), and one of the 72 backlog questions that gains a
claim before anyone has walked to it. Both deserve a look while the new evidence is in front of the
reader. Called from a `/process` promotion tail, §7 runs once per promoted candidate, inside that
candidate's `promote` invocation.

**R15. `promote` §3's open-question check reads the Graduated marker.** Replace "whether it still carries
`## question` or now carries `## so what`" with: a question has graduated if its note carries a
`> **Graduated` blockquote under `## question` (or under its first heading, per R6.3), **or** is headed
`## so what` (an in-place graduation from before this spec, in a receiving graph other than the commons).
Either way it's not a valid target as a question. Attach as outcome 1 instead: to the attractor the
marker names, or, for an in-place graduation, to that same note, which is now the attractor. Update `references/graph-conventions.md`'s
question-note paragraph ("promoted in place to a proper attractor") to describe R6.
*Rationale:* fixes the live bug described in Problem. Keeping the `## so what` branch costs one clause
and covers any graph that followed the old documentation.

### Splits and moves (added after Phase 0)

The interview left these unspecified. Every Phase 0 draft that split or moved claims had to improvise
them, and did so differently.

**R19. A split marks the original, and may retitle it.**
- **Split marker.** Insert under the original's `## question` (or first heading, as in R6.3), below any
  earlier marker:
  `> **Split YYYY-MM-DD.** <n> claims moved: <k> to [[new or existing note]], … What stays is <one clause>.`
- **Retitle** when what stays is narrower than the title (R4). Proposal 1's draft warned that its broad
  title "will keep pulling every future measurement claim back into this question, rebuilding the
  conflation the split removes." The retitle:
  - renames the note file to the new title;
  - replaces every `[[old title]]` link in the graph with `[[new title]]`, including claims' `supports:`,
    maps, other notes, and `changelog.md`, since a wikilink is a pointer rather than prose;
  - adds `Formerly titled *<old title>*.` to the split marker;
  - moves the map line to its new alphabetical position.

  Before writing, list every file the rename touches. Proposal 1's question had 46 links to it: 42 in
  claims, 2 in other questions, 1 in a map and 1 in the changelog.
- **A split-off question** opens with one line, `Split out of [[original]] on YYYY-MM-DD.`, then its own
  `## question` body: what the group shares and what's open about it, written fresh rather than copied
  from the original.

*Rationale (Derek, Phase 0):* the marker gives a split the same visible record a graduation has (R6.3),
and past splits in the commons already wrote "split out of" lines. Derek chose to retitle over keeping
the broad title, so the original stops attracting what was just split away.

**R20. Moved evidence lines get annotations written for their new home. The original keeps its
commentary.** When a claim moves, its evidence line moves with it, and its annotation is rewritten to
make sense under the destination: no references to former neighbors ("the entry above", "the ninth
entry", "a fourth parameter of the frame"). The original note's prose and commentary paragraphs stay
where they are, as the record of how the question was understood before the split. Where an evidence
item spans several lines or paragraphs, the whole item moves, and its domain suffix is read from
wherever it ends up.
*Rationale (Derek, Phase 0):* annotations that point at old neighbors become false when moved word for
word. Three drafts moved them verbatim and one rewrote them, and Derek approved the rewrite. He also
approved leaving the long commentary in the original, because it refers to entries by position and
would break if moved.

### Packaging

**R16. No template change, so no `/graph-patch` delta.** All changes are to plugin-owned files: `promote`,
the new `graduate` skill, `references/graduation.md`, `references/graph-conventions.md`, `graph-init`,
README. The plugin's templates (`references/templates/`) carry no graduation text, so
`.claude/rules/template-deltas.md` doesn't fire. The commons' generated skill, which has stale wording, is
fixed by a direct edit (R17).
*Rationale (Derek, interview):* a delta would add graduation text to every generated skill, but only
receiving graphs graduate (R3), and there is one. It also couldn't anchor all of the commons' stale text:
one passage sits under `## How Notes Arrive`, a heading graph-init writes only for a commons, not one
from the template.

**R17. Fix the commons' generated skill by hand, and fix graph-init so a future commons is generated
right.**
- In `~/commons/.claude/skills/knowledge-graph/SKILL.md`: the `## Types in This Graph` sentence ending
  "…to promote it in place to a `principle`", and the `## Awareness Protocol` bullet "…ready to be
  promoted in place to a principle", both rewritten to describe R6. The one-line offer under
  `## Awareness Protocol` becomes *"Worth reviewing [question] for graduation? `/graduate` walks it."*
  Committed and pushed in the commons repo as its own commit during rollout.
- In `skills/graph-init/SKILL.md`: the bullet beginning "For a graph with no sources (the commons)",
  where it says "a question ready to graduate", gains a pointer: the generated skill names `graduate` as
  the way to act on it and describes R6's shape, not an in-place rewrite.
*Rationale (Derek, interview):* only the commons is affected, and graph-init is what wrote that wording
into it. Plugin-skill edits propagate on plugin update. The commons file is project-owned and never
updates, so it needs a hand edit.

**R18. Minor version bump: 0.6.0 → 0.7.0**, in both `plugins/knowledge-commons/.claude-plugin/plugin.json`
and `.claude-plugin/marketplace.json`. Add `graduation` to the plugin's keywords and a clause to both
descriptions.
*Rationale:* `.claude/rules/plugin-updates.md`: a new skill is always minor. The R15 bug fix rides along.

## The `graduate` skill

`plugins/knowledge-commons/skills/graduate/SKILL.md`. Frontmatter in the same shape as `promote`:

```yaml
---
name: graduate
description: "Review a receiving graph's eligible open questions — those with evidence from two or more domains — one at a time, and graduate, split, move claims, retitle, or hold each with human approval. Use when the user asks to graduate questions, review the commons backlog, see which questions are ready to become principles, or invokes /graduate. Triggers: graduate questions, /graduate, what's ready to graduate, review eligible questions, work the commons backlog."
argument-hint: "[graph path or question title]"
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---
```

Body sections, in order: resolve and refresh the target (R11) → check it's a receiving graph (R3) and
resolve the destination (R9) → build the backlog (R7, R10, R12) → walk it, reading
`${CLAUDE_PLUGIN_ROOT}/references/graduation.md` for the review → push and summarize. Given a question
title as an argument, review that one question regardless of position, but still require eligibility
and say why if it isn't eligible.

## `references/graduation.md`: the shared review procedure

Holds R4 through R8, R10's stamp, R13, R19 and R20 as instructions: the coherence test, the moves and
exactly what each writes, the recording rules, the steering check, and the proposal format. Each of the
two callers states its own trigger, target resolution, and commit or push policy, then hands off to this
file for the review itself.

**Proposal format**, shown before any write:
1. **Counts.** The question title, its claim count, its domain names and families (R7), and any suffix
   mismatches.
2. **The whole-question test.** The mechanism and remedy sentences (R5), or the attempt that failed and
   which requirement it failed.
3. **Groups.** For each group: its claims, its own R5 sentences, its move (R4), and whether it's eligible
   only through a family sibling.
4. **Writes.** Every file the moves write or edit: full text for new notes, a diff for edits, and the
   list of files a retitle touches (R19).
5. **Steering.** For each graduation, the steering line (R13).
6. **The calls most worth a second look.** Two to four choices the review made that the reader could
   reasonably make differently, each with the alternative. Phase 0 found that a reviewer can't parse a
   400-line proposal without them.

Phase 0's proposals ran 280–450 lines each. Lead with sections 1–3 and 6; section 4 is for checking, not
for reading first.

## Edge cases

- **Refresh fails or is refused** → continue, but every proposal says it was weighed against a possibly
  stale copy (as `promote` §1).
- **Question note is missing `## evidence`, or a link doesn't resolve** → report it and skip that
  question. Don't review partial evidence.
- **Principle title collides with an existing note** → stop and show both. It may be a duplicate stance,
  which makes the right move "move the claims to the existing principle."
- **A split leaves a group with one claim** → it becomes a single-domain question, which is fine (promote
  §3: single-domain questions are the designed intermediate state).
- **Moves drop a question below two domains** → it leaves the backlog. Say so in the changelog bullet, as
  the 2026-07-20 revert did ("single-domain again").
- **Two reviews in one walk move claims into the same existing question** → expected. Phase 0's
  proposals 1 and 3 both did. The receiving question's stamp (R10) is replaced by the later review's,
  and it comes back once it has gained claims since the stamp.
- **Working tree dirty in the target** → stop before writing. Don't stash someone else's work.
- **`/process` promotion tail runs §7 for several candidates that hit the same question** → the first
  review records its moves and stamps; later ones see a stamped or graduated question and behave per R10 and R15.

## Phase 0: test the premise before building

Per `validate-value-before-build.md`. **The premise:** a session following R5 and R6 against real
commons questions produces proposals Derek would approve or meaningfully redirect, not boilerplate.

**Experiment (no skill, no code):** in a scratch session, take the first five questions in R12's order
from a fresh `~/commons` clone. For each, write the R5 sentences and the full proposal by following this
spec's text by hand. Also recount eligibility with R7 (claim frontmatter) and compare it with the
suffix-based 72. Write nothing to `~/commons`.

**Measure:** the outcome mix, whether the drafted "so what" reads as a stance (not a summary of claims),
how many suffix mismatches R7 finds, and Derek's verdict per proposal.

**Gate:**
- At least three of five are approvable with light edits → build as specced.
- Proposals are plausible but bland (summaries, not stances) → sharpen R5 and R6's instructions, rerun.
- Most are wrong-shaped (e.g. the coherence test can't tell when to split) → revisit R4 and R5 before
  building.

Record what was found in this spec, under a "Phase 0 findings" section.

## Phase 0 findings (2026-11-08)

**Result: passed, 5 of 5 approvable with light edits.** Build, with the amendments below.

**What ran.** A fresh clone of the commons (`334d12f`). The top five questions in R12's order were each
reviewed by a separate agent given only this spec and the clone, writing nothing to the commons. A
sixth agent turned the five proposals into an interactive review page, and Derek answered 29 calls on
it: the five spec questions below, three or four per proposal, and an overall verdict on each.

| # | Question | Claims | Domain names | Proposed moves |
|---|---|---|---|---|
| 1 | what makes a measurement report its instrument instead of its subject | 41 | 13 | Split off 4 questions, move 2 claims to an existing question, 11 stay (Derek: retitle the original) |
| 2 | what makes a failure invisible to the surfaces built to catch it | 31 | 13 | Overturn the 2026-07-21 hold, split off 3, move 1 to an existing question, 15 stay |
| 3 | what can an empty result be taken to mean | 22 | 9 | Split off 2 (reader vs. producer), move 1 to an existing question, 15 stay |
| 4 | what does the frame you examine bound about the conclusion you can draw | 16 | 9 | Move 7 to an existing question, split off 2, 4 stay |
| 5 | what relocates a claim's authority as it moves between documents | 10 | 8 | Move 1 to an existing question, graduate 9 to *a claim takes the standing of wherever it is written unless its origin is written with it* |

**Assumed vs. measured:**
- *Eligible count.* The suffix count gave 72. R7's frontmatter count gives **73** at `334d12f`. It found
  3 suffix mismatches (two missing, one with extra text) and no claim without `domain:`.
- *Stance, not summary.* The one drafted principle reads as a stance. It drops the question's own
  hypothesis (that the cause is the direction of travel) because three of its claims involve no travel.
  Every draft also rejected the title-level mechanism sentence on its own, so the R5 test did real work.
- *Outcome mix.* The spec assumed one outcome per review. **No review produced a single outcome.**
  Graduation was rare: one whole question, none of the others. Twelve groups split off or remaining were
  judged graduatable or probably graduatable, but weren't graduated because the brief said not to.
- *Cost.* 5–10 minutes and about 165k–260k agent tokens per review.

**Spec changes this produced:**
- R4 rewritten as a set of moves.
- R5 gained three requirements.
- R7 counts first links and shows families.
- R8's changelog style is corrected to an appended dated bullet.
- R10 stamps every reviewed question, and treats holds written in the note body as stamps.
- R12's order is kept, with its cost stated.
- R13 gained a partial-coverage sentence.
- R19 (split marker and retitle) and R20 (moved annotations) are new.
- The proposal format leads with the calls worth a second look.

**Not adopted.** Counting domain families instead of names: Derek kept names and made families visible.
A separate "partly steering" form: declined in favor of R13's added sentence.

The five proposals and the review page stay out of this repo, which is public. They quote commons
content from Derek's employer and personal projects. They were working files in the session's
scratchpad.

## Revisions after code review (2026-11-08, PR #79)

A high-effort review of the implementation found defects in decisions as written. The skills implement
the corrected versions below; the decisions above are left as written, as the record.

- **R7, families.** "Share their first hyphen-separated segment" lumped unrelated projects. The commons'
  `claude-code-plugins` and `claude-usage` both start with `claude`. Now a family is a domain name plus
  the names that extend it with a hyphen, **when the root is itself a domain**.
- **R7, cost.** Counting from frontmatter for every question meant hundreds of reads per walk. The
  `(domain)` suffixes are now a prefilter: a question whose suffixes are all present and show one domain
  is skipped. Every other question is counted from frontmatter, which stays authoritative.
- **R10, stamps.** A stamp carrying only a date can't see a claim promoted the same day as the review,
  and the "gains a claim it didn't have" clause had nothing recorded to compare against. Stamps now
  record the claim count too. "New evidence since the stamp" means more claims than the stamp records,
  or a claim dated after it.
  - "Eligible for review" is now defined once, in `graduation.md` §7, and both `promote` §7 and
    `graduate` cite it. The two copies had already drifted once.
- **R11, resolution.** Resolving the target, then refreshing it, then checking it's a receiving graph
  meant that running `/graduate` from a source graph with a `question` attractor (this repo)
  fast-forwarded and dirty-checked the source repo. The receiving-graph check now runs before the
  refresh: it reads only `.commons.yml` and two or three evidence notes' frontmatter, which are stable.
  Only the chosen target is refreshed.
- **R19, retitle.** Links are replaced in all their forms (`|shown text`, `#section`). After writing, the
  graph is searched for remaining links to the old title.
- **R4, partial approval.** A dropped move's claims stay in the original. Anything that depended on what
  stays (a retitle, a graduation of the remainder, the split marker and stamp) is re-checked before
  writing.
- **R17, graph-init.** The generated skill must name the `graduate` skill, never a plugin file path,
  which doesn't resolve from the project.
- **Triggers.** `graduate` and `promote` both answer to "graduate". Each description now names the other
  for the direction it doesn't handle: question → principle, or principle → rule.

## Execution plan

One PR on a `feat/` branch. Everything here is plugin-owned and ships together.

1. `references/graduation.md`: the shared procedure (R4–R8, R10's stamp, R13, R19, R20, and the
   proposal format).
2. `skills/graduate/SKILL.md`: the backlog walk (R3, R9–R12).
3. `skills/promote/SKILL.md`: add §7 (R14) and fix the §3 check (R15). §6's "append one line to the
   target's `changelog.md`" already matches R8 and stays. Keep the closing "A promoted note must stand
   alone" line last. The intro paragraph's list of entry points ("at the tail of a `/process` run…
   mid-session… directly") is unchanged; §7 is a step, not an entry point.
4. `references/graph-conventions.md`: rewrite the question-note paragraph (R15).
5. `skills/graph-init/SKILL.md`: the commons-generation bullet (R17).
6. `README.md`: add `graduate` to the skills table and usage; describe the graduation shape.
7. Version bump to 0.7.0 in both files, plus keywords and descriptions (R18).

**Rollout, after merge and plugin update on devbox:**

8. Hand-edit `~/commons/.claude/skills/knowledge-graph/SKILL.md` (R17). Commit and push in the commons.
9. Run `/graduate` against the commons for the first real walk. Stop whenever Derek says. That run is
   the mechanism's real test.

## Risks and open questions

**Risk 1. The review is an unverified agent drafting a stance.** A "so what" can read well and be wrong.
The R5 sentences shown in every proposal are the mitigation: the reader judges the reasoning, not just the
prose. In Phase 0, Derek approved all five, but through a review page built for the purpose. In the real
walk, the proposal format's "calls most worth a second look" have to carry that weight.

**Risk 2. A 73-question walk is long, and approval fatigue is the failure mode.** Phase 0 measured each
review at 5–10 minutes of agent time and 280–450 lines of proposal, and splits add questions to the
queue. Derek found the raw proposals hard to parse and needed an interactive page to judge them. "Not now"
and "stop" exist, and committing per review makes stopping free. If walks stall, the next levers are a
session cap (review N, then stop) and a review page like Phase 0's. Neither is added until a real walk
shows it's needed.

**Risk 3. The R14 trigger depends on R10's date comparison.** A claim promoted with a wrong `date:`
(older than the review) would keep a held question silent. `promote` §2 already requires the promotion
date, so this would be a promote bug, not a graduation one.

**Risk 4. Ordering by domain count favors broad, conflated questions.** Phase 0 confirmed it: the top
five all split, and one graduated in part. Derek accepted this (R12). Watch whether the first walk ever
reaches the questions that graduate cleanly.

**Risk 5. Some past holds live only in the changelog.** R10 reads holds on the map line and in the note
body. A hold recorded only in a changelog entry is invisible to it, so R12 raises that question again.
Accepted: re-raising it costs one "hold" and writes the stamp R10 expects. Not worth a migration pass
over 3,700 lines of changelog.

**Q1. Does the commons' awareness offer earn its place at all?** R17 keeps it and repoints it at
`graduate`. With R14 covering new evidence and `graduate` covering the backlog, the offer may be
redundant. Settle after the first real walk.

**Q2. When a second receiving graph appears**, R9's "the attractor other than `question`" may not
resolve. Stopping to ask is right for v1; a config key may be warranted then.
