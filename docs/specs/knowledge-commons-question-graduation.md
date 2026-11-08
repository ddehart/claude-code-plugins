# Spec: knowledge-commons question graduation

**Status:** Draft. Interviewed 2026-11-08; not built. Phase 0 not yet run.
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

**R4. Four outcomes: graduate, split, hold, detach**, plus "not now", which writes nothing.

| Outcome | When | Writes |
|---|---|---|
| **Graduate** | The R5 test passes | R6 |
| **Split** | Claims don't share one mechanism and remedy | New question note(s); evidence lines moved; each moved claim's `supports:` repointed; map lines for the new question(s); original's map annotation updated |
| **Hold** | Coherent but not ready, with a stated reason | Map annotation only (R8) |
| **Detach** | One claim's attachment manufactured the eligibility (it shares wording, not mechanism) | Claim's `supports:` repointed to the right question/principle (or a new question); evidence line moved; both map annotations updated |
| **Not now** | Reader wants to skip without deciding | Nothing. It stays in the backlog |

*Rationale (Derek, interview):* these are the four things that actually happened in the commons' first
reviews. Offering only graduate/hold would push the two most common real outcomes, split and detach,
out to hand edits.

**R5. The coherence test runs before any graduation is proposed.** State the single mechanism the
question's claims share, and the single remedy, in one sentence each. If either takes more than one
sentence, or a claim doesn't fit the sentence, the proposal is a split or a detach, not a graduation.
Show both sentences in every proposal, including holds, so the reader judges the test and not just the
verdict.
*Rationale:* the commons' 2026-07-20 finding (see Problem). The test did real work the first time it was
applied.

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

**R7. Distinct domains are counted from claim frontmatter.** For each `[[link]]` in the question's
`## evidence`, open the claim and read its `domain:`. The question is eligible when there are two or more
distinct values. If an evidence line's `(domain)` suffix disagrees with the claim's `domain:`, or is
missing, report it in the proposal and count the frontmatter. Never fix it silently. A claim with no
`domain:` counts as unknown, is reported, and doesn't add to the count.
*Rationale (Derek, interview):* `promote` writes `domain:` from the source graph's `graph.name`, so it is
the authoritative value. All 650 claims carry it (checked 2026-11-08). The suffix is hand-typed
duplication.

### State

**R8. Where each outcome is recorded.**
- **Hold:** map annotation only, appended to the question's line in `maps/questions.md`, in the existing
  form: `*(eligible; reviewed YYYY-MM-DD and held: <reason in one clause>)*`. A new review replaces any
  previous review annotation on that line; it doesn't stack. A hold with no reason given is recorded as
  `held: no reason given`.
- **Graduate, split, detach:** the map edits and note-level marker each outcome writes (R4, R6), plus one
  dated `changelog.md` entry in the target changelog's current style. In the commons today that is a
  `## YYYY-MM-DD — <what happened>` heading, **prepended** (newest first; only July entries use `###`),
  then prose naming the question, the outcome, and the R5 sentences. A `graduate` session puts all of its
  outcomes in **one** entry, added to as each outcome lands. A `promote` run's graduation gets its own
  entry, separate from the promotion's.

*Rationale (Derek, interview):* matches existing commons practice. Holds are frequent and low-information,
so they belong in the map, where the next walk reads them. Structural changes earn changelog prose, where
the commons keeps its reasoning.

**R9. The destination attractor is the target's attractor type other than `question`.** The commons
declares `principle` and `question`, so it resolves to `principle`, `principles/`, `maps/principles.md`.
If a receiving graph declares zero other attractor types, or more than one, stop and ask which one
graduations go to. Don't guess, and don't add a `.commons.yml` key (graph-init's Never section restricts
keys).
*Rationale:* no config field names the graduation destination today. One unambiguous case covers the
only receiving graph that exists.

**R10. Held questions come back only when new evidence lands.** A held question re-enters the backlog,
and becomes eligible for `promote`'s review again, when any of its claims has a `date:` later than the
hold's review date. There is no calendar expiry.
*Rationale (Derek, interview):* a hold records a judgment about the evidence. Only new evidence can change
it. Claim `date:` is the promotion date (promote §2), so "claim newer than the review" is exactly
"evidence that arrived after the review."

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
graduated annotations vary in wording), two or more distinct domains (R7), and not held, or held with
newer evidence (R10).
1. Show the count and the first ten in order, with each one's domains and claim count.
2. Order: distinct domains descending, then claim count descending, then title.
3. Review one at a time: show the R5 sentences, the proposed outcome and its full writes, and wait for
   approval. `y / edit / <other outcome> / not now / stop`.
4. **Commit after each approved outcome** (name the paths; never blanket-stage), adding to the session's
   changelog entry (R8). **Push when the walk ends**, whether it finished or was stopped, and say plainly
   if the push failed. A rejected push follows `promote` §6: pull, rebase, read what came in, and
   re-review any question it touched rather than resolving mechanically.
5. A split's new questions join the queue in their sorted position if they're eligible. They aren't
   reviewed out of order.

*Rationale (Derek, interview):* breadth of corroboration is the strongest graduation signal, and the
densest questions are the ones most likely to need a split, which is worth doing early. Committing per
outcome means an interrupted walk loses nothing. Pushing once avoids a push per question across a long
walk.

**R13. Every graduation checks the instruction tier.** Read `~/.claude/rules/*.md` and judge whether a
rule already encodes the new principle. Record the answer in the principle's `## so what` and its map
annotation: `**Already steering** as <rule-name>.md` or `**Not yet steering.** No rule encodes this.` For
a not-yet-steering principle, the proposal names `promote` §4 as the next step and does not run it.
Leave the principles map's standing note alone unless this graduation contradicts what it says, in which
case propose the edit.
*Rationale (Derek, interview):* the commons found that three of its four principles were already
steering when they graduated. Keeping that visible per principle is what the standing note was
reaching for.

**R14. `promote` gains a final section, §7 "Graduation check."** It runs after §6 has written, committed,
and pushed the promotion, and only when all of these hold: the target is a receiving graph (R3); the
association was outcome 2 (attached to an existing open question); and after the attachment that question
is eligible (R7) and not held without newer evidence (R10). It then runs the review procedure for that one
question in the same session. On approval it writes in the target, commits **separately** from the
promotion, and pushes. "Not now" writes nothing; the backlog walk will find it.
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
description: "Review a receiving graph's eligible open questions — those with evidence from two or more domains — one at a time, and graduate, split, hold, or detach each with human approval. Use when the user asks to graduate questions, review the commons backlog, see which questions are ready to become principles, or invokes /graduate. Triggers: graduate questions, /graduate, what's ready to graduate, review eligible questions, work the commons backlog."
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

Holds R4 through R8 and R13 as instructions: the coherence test, the four outcomes and exactly what each
writes, the recording rules, the steering check, and the proposal format. Each of the two callers states
its own trigger, target resolution, and commit or push policy, then hands off to this file for the
review itself.

**Proposal format**, shown before any write:
1. The question title, its distinct domains (from R7) and claim count, and any suffix mismatches.
2. The mechanism sentence and the remedy sentence (R5), or the attempt that failed.
3. The proposed outcome and why.
4. Every file it will write or edit, in full for new notes and as a diff for edits.
5. For a graduation, the steering line (R13).

## Edge cases

- **Refresh fails or is refused** → continue, but every proposal says it was weighed against a possibly
  stale copy (as `promote` §1).
- **Question note is missing `## evidence`, or a link doesn't resolve** → report it and skip that
  question. Don't review partial evidence.
- **Principle title collides with an existing note** → stop and show both. It may be a duplicate stance,
  which makes the right outcome "detach the claims to the existing principle."
- **A split leaves a side with one claim** → it becomes a single-domain question, which is fine (promote
  §3: single-domain questions are the designed intermediate state).
- **A detach drops a question below two domains** → it leaves the backlog. Say so in the changelog entry,
  as the 2026-07-20 revert did ("single-domain again").
- **Working tree dirty in the target** → stop before writing. Don't stash someone else's work.
- **`/process` promotion tail runs §7 for several candidates that hit the same question** → the first
  review records its outcome; later ones see a held or graduated question and behave per R10 and R15.

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

## Execution plan

One PR on a `feat/` branch. Everything here is plugin-owned and ships together.

1. `references/graduation.md`: the shared procedure (R4–R8, R13).
2. `skills/graduate/SKILL.md`: the backlog walk (R3, R9–R12).
3. `skills/promote/SKILL.md`: add §7 (R14) and fix the §3 check (R15). Also correct §6's "append one
   line to the target's `changelog.md`" to "add an entry in the changelog's own order and heading style"
   (the commons prepends; R8). Keep the closing "A promoted note must stand alone" line last. The intro paragraph's list of
   entry points ("at the tail of a `/process` run… mid-session… directly") is unchanged; §7 is a step,
   not an entry point.
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
prose. Phase 0 tests whether that's enough.

**Risk 2. A 72-question walk is long, and approval fatigue is the failure mode.** "Not now" and "stop"
exist, and committing per outcome makes stopping free. If walks stall, the next lever is a session cap
(review N, then stop); not added until a real walk shows it's needed.

**Risk 3. The R14 trigger depends on R10's date comparison.** A claim promoted with a wrong `date:`
(older than the review) would keep a held question silent. `promote` §2 already requires the promotion
date, so this would be a promote bug, not a graduation one.

**Risk 4. Ordering by domain count may favor broad, conflated questions.** That's partly the point (they
need splitting), but a walk could spend its energy on splits and graduate little. Watch the first walk's
outcome mix.

**Risk 5. Some past holds live only in the changelog.** The changelog records at least one question held
on 2026-07-22 (*what makes a measurement report its instrument instead of its subject*) whose map line
carries no review annotation, so R12 will raise it again. Accepted: re-raising a held question costs one
"hold" and writes the annotation R8 expects. Not worth a migration pass over 3,700 lines of changelog.

**Q1. Does the commons' awareness offer earn its place at all?** R17 keeps it and repoints it at
`graduate`. With R14 covering new evidence and `graduate` covering the backlog, the offer may be
redundant. Settle after the first real walk.

**Q2. When a second receiving graph appears**, R9's "the attractor other than `question`" may not
resolve. Stopping to ask is right for v1; a config key may be warranted then.
