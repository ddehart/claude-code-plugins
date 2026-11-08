# Graduation: the shared review procedure

How one open question in a **receiving graph** gets reviewed for graduation. Two callers use this file
and nothing else defines the review:

- **`graduate`** walks a graph's backlog of eligible questions, one at a time.
- **`promote` §7** reviews the one question a promotion just made eligible.

Each caller owns its own trigger, target resolution, refresh, and commit/push policy. This file owns
everything between "here is an eligible question" and "these files changed": the test, the moves, the
writes, the records, and the proposal the reader approves.

A **receiving graph** declares a `question` attractor and its evidence notes carry `domain:` frontmatter,
because evidence arrives there by promotion. A commons is the usual case. A graph whose questions settle
against their own "what would settle it" clause, with single-domain evidence, is not a receiving graph,
and nothing here applies to it.

The **destination attractor** is the receiving graph's attractor type other than `question`. In a
commons that's `principle`, in `principles/`, mapped in `maps/principles.md`. If the graph declares no
other attractor type, or more than one, stop and ask which one graduations go to. Don't guess, and don't
add a `.commons.yml` key for it.

## 1. Count domains and families

For each item in the question's `## evidence` list, take the **first** `[[link]]` on the item. Later
links on the line, and links inside commentary paragraphs, are annotations. Open that claim and read its
`domain:` frontmatter. That value is authoritative: `promote` writes it from the source graph's name.

- **Eligible** means two or more distinct `domain:` values.
- If an evidence item's `(domain)` suffix is missing or disagrees with the claim's `domain:`, report it in
  the proposal and count the frontmatter. Never fix it silently.
- A claim with no `domain:` counts as unknown: report it, and don't add it to the count.
- An evidence item can span several lines or paragraphs. Read its suffix from wherever the item ends.
- A link that doesn't resolve, or a note with no `## evidence`, stops the review of that question:
  report it and skip. Don't review partial evidence.

**Families.** Domain names that share their first hyphen-separated segment form a family: `orchard`,
`orchard-nursery` and `orchard-cidery` are one family. Related projects are not independent observers.
State both numbers in every proposal ("6 domain names, 4 families"), and say when a group is eligible
only because of a sibling in the same family. Eligibility and ordering still use names. The family count
is there so the reader can weigh it.

## 2. The coherence test

Reaching two domains is a prompt to check the question's coherence, not a signal to graduate. A question
broad enough to collect claims quickly is broad enough to collect claims that don't share a mechanism,
so the densest questions are the most likely to be conflated.

State the single **mechanism** the claims share and the single **remedy**, one sentence each. Three
requirements keep the test from passing on generality:

1. **The mechanism sentence must say more than the question's title.** A sentence that restates the
   title fits every claim and excludes nothing. Name where or how the effect enters.
2. **Each claim's own remedy must be an instance of the remedy sentence.** Read every claim's remedy, not
   just the question's prose. If two contradict ("widen the review" against "widening does nothing,
   change the question"), the test fails, however the sentence is worded.
3. **Check the remedy against existing attractors' text**, the `## so what` of each destination note,
   not only their titles. A group whose remedy is already a form of an existing principle belongs under
   that principle (a move, §3), not in a new one.

If the test passes for the whole question, the question can graduate. If it fails, partition the claims
into groups that each pass, and test each group on its own. Show every sentence you wrote, including the
attempts that failed and which requirement they failed, so the reader judges the reasoning and not just
the verdict.

## 3. The moves

A review proposes a **set of moves**, not one outcome: one move per group, plus at most one for the
original note. Every claim must end up in exactly one place.

| Move | Applies to | When | Writes |
|---|---|---|---|
| **Graduate** | The whole question, or one group | It passes §2 and has two or more domains | §4 |
| **Split off** | A group | It passes §2 but belongs in no existing note | A new question note (§5), evidence moved (§6), each moved claim's `supports:` repointed, a map line for the new question |
| **Move to an existing note** | A group of one or more claims | An existing question or destination attractor already states the group's mechanism, judged from its text | Evidence moved (§6), `supports:` repointed, both notes' map annotations updated if they no longer fit |
| **Stay** | The group left in the original | Always exactly one, possibly empty after a full graduation | Nothing beyond §5's marker and any retitle |
| **Retitle** | The original note | What stays is narrower than the title, so the title would keep attracting claims that belong elsewhere | §5 |
| **Hold** | The whole question | Coherent but not ready, with a stated reason | A map stamp only (§7) |
| **Not now** | The whole review | The reader wants to skip without deciding | Nothing. It stays in the backlog |

Before proposing a new question or principle, check whether an existing note already says it, by
reading the notes rather than matching titles. A title that collides with an existing note means stop
and show both: it's probably a move to the existing note.

Moving a claim in or out changes the domain count of both notes. A note that drops below two domains
leaves the backlog. Say so in the changelog bullet ("single-domain again").

A group that passes §2 can be graduated in the same review. A passing group that isn't graduated stays in
the backlog under §7's stamp.

## 4. What a graduation writes

A graduation writes a **new destination note and keeps the question as its record**. It never rewrites
the question in place.

1. **New note** in the destination directory.
   - **Title:** a stance stated as a sentence, not a question ("thin before petal fall, not after", not
     "when should thinning happen").
   - **Frontmatter:** follow the graph's existing notes of that type. In a commons: `genitor:
     "[[principles]]"` and `tags:`, with no `date:` and no `supports:`.
   - **Body:** `## so what`, then `## evidence`. The `## so what` gives the held stance, its mechanism and
     remedy, its limits, and the steering line (§8). Write a stance, not a summary of the claims: if the
     evidence contradicts the question's own hypothesis, say so and drop it. The `## evidence` section
     lists every claim with its `(domain)` suffix.
2. **Each claim's `supports:`** is repointed from the question to the new note.
3. **The question note is kept.** Its body and evidence list stay as they are. Insert directly under
   `## question` (or under the note's first heading, if it has no `## question`), below any earlier
   marker:
   `> **Graduated YYYY-MM-DD** to [[new note title]], on evidence from <domains>.`
   Add a clause for anything split or moved out in the same review.
4. **Maps.**
   - Add the new note to the destination map in alphabetical position, with a one-clause "so what"
     annotation (`graph-conventions.md`).
   - Keep the question's line in its map, and replace its annotation with
     `graduated YYYY-MM-DD to a <destination type> on <one clause>`.
5. **Changelog bullet** (§7).

A question has graduated when its note carries a `> **Graduated` marker. Judge that from the note, never
from its map line, whose wording varies. A note headed `## so what` instead of `## question` graduated
in place under older conventions, and counts as graduated too.

## 5. What a split writes

- **Split marker** on the original, under `## question` (or its first heading), below any earlier marker:
  `> **Split YYYY-MM-DD.** <n> claims moved: <k> to [[note]], <k> to [[note]]. What stays is <one clause>.`
- **Retitle**, when what stays is narrower than the title:
  - rename the note file;
  - replace every `[[old title]]` link anywhere in the graph with `[[new title]]`. That includes claims'
    `supports:`, maps, other notes, and `changelog.md`, because a wikilink is a pointer, not prose;
  - add `Formerly titled *<old title>*.` to the split marker;
  - move the map line to its new alphabetical position.

  List every file the rename touches in the proposal, before writing anything. A large question can have
  dozens of links.
- **A split-off question** follows the graph's question shape. It opens with one line,
  `Split out of [[original]] on YYYY-MM-DD.`, then its own `## question` body. Write that body fresh: what
  the group shares, and what's still open about it. Don't copy it from the original. Then `## evidence`
  with the moved items (§6).

## 6. Moving evidence

When a claim moves, its whole evidence item moves with it: the line, and any continuation lines or
paragraphs that belong to that item. Rewrite its annotation so it makes sense in the new note, with no
references to former neighbors ("the entry above", "the ninth entry", "a fourth form of this question").

The original's own prose and commentary paragraphs stay where they are. They record how the question was
understood before the split, and they often refer to entries by position, so they would break if moved.

Each moved claim's `supports:` is repointed to its new note. A claim that supported several notes keeps
the others.

## 7. Records

**Stamps.** Every question a review touched gets a stamp on its map line. A newer stamp replaces the old
one instead of adding to it.

- **Hold:** `*(eligible; reviewed YYYY-MM-DD and held: <reason in one clause>)*`. A hold with no reason
  given is recorded as `held: no reason given`.
- **Everything else:** `*(reviewed YYYY-MM-DD: <one clause on the moves>)*`. This goes on the original,
  each split-off question, and each existing question that received claims.

A stamped question comes back into the backlog, and into `promote` §7, only when new evidence arrives:

- one of its claims has a `date:` later than the stamp, or
- for a question that received moved claims, it has gained a claim it didn't have at the stamp. Moved
  claims keep their old `date:`, so the date check alone would never bring it back.

There is no calendar expiry. A review records a judgment about the evidence, and only new evidence can
change it.

**Older holds written in the note body** (a paragraph such as "Eligible, reviewed YYYY-MM-DD and held")
count as stamps. When a review finds one, it moves the stamp onto the map line.

**Changelog.** Every approved review except a pure hold gets **one dated bullet appended at the end of
`changelog.md`**, in the form promotions use:

```
- YYYY-MM-DD — reviewed [[question]]: <the moves, linking the notes they wrote or touched>. <The
  mechanism and remedy in a clause.>
```

That's one bullet per review. A `promote` run's review bullet is separate from its promotion bullet.

## 8. The steering check

Every graduation checks the instruction tier. Read `~/.claude/rules/*.md` and judge whether a rule
already encodes the new stance. Write the answer at the end of the new note's `## so what`, and in its map
annotation:

- `**Already steering** as <rule-name>.md.`, or
- `**Not yet steering.** No rule encodes this.`

When a rule covers part of the stance, keep the line binary and add one sentence naming that rule and
the part it covers. The uncovered part is what a rule would be proposed for. For a stance that isn't yet
steering, the proposal names `promote`'s instruction-tier branch (§4) as the next step. It never runs it.

If the destination map carries a standing note about steering, leave it alone unless this graduation
contradicts what it says. If it does, propose the edit.

## 9. The proposal

Nothing is written before the reader approves. The proposal has six parts. **Lead with 1, 2, 3 and 6.**
Part 4 is for checking, not for reading first: a review of a large question runs to hundreds of lines,
and a reader handed all of it at once can't find what needs their judgment.

1. **Counts.** The question title, its claim count, its domain names and families (§1), any suffix
   mismatches, and any existing stamp with the evidence that arrived since.
2. **The whole-question test.** The mechanism and remedy sentences (§2), or the attempt that failed and
   which requirement it failed.
3. **Groups.** For each group:
   - its claims;
   - its own mechanism and remedy sentences;
   - its move (§3) and destination;
   - whether it is eligible only through a family sibling.
4. **Writes.**
   - full text for every new note;
   - a diff for every edited note, map line, and `supports:` field;
   - the changelog bullet;
   - for a retitle, the list of every file the rename touches.
5. **Steering.** For each graduation, the steering line (§8).
6. **The calls most worth a second look.** Two to four choices this review made that the reader could
   reasonably make differently. For each, give what the review chose and the most plausible alternative.
   Typical calls:
   - whether a group goes to an existing note or a new one;
   - whether a borderline claim belongs in a group;
   - whether a passing group graduates now;
   - whether to retitle.

The reader can approve the whole set, approve some moves, edit, choose "not now", or stop. Drop any move
that isn't approved. The approved moves must still leave every claim in exactly one place; if they don't,
say which claims are left without a home and re-propose for them.
