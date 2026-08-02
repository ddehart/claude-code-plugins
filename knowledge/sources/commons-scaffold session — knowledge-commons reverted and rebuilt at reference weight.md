---
genitor: "[[sources]]"
source: "session:284b79f5-c34f-4ad3-b97d-9c78cdc9c46f"
tags: [source, knowledge-commons]
processed:
  - date: 2026-07-15
    ran: [5 decisions, 8 patterns, 15 observations, 7 entities, 1 reference]
    skipped: ["version bumps 0.1.1–0.1.7 and one-off fixes (operational)", "repo-revert / PR-close / chronicle-writing logistics (session logistics)", "Aiwyn /process reference particulars (other-domain, stripped)"]
    errored: []
---

The commons-scaffold worktree session in which the **knowledge-commons** plugin was designed and shipped.
It opened with Derek's regret that the design had become "a monstrosity of validation, prematurely
solving a problem I don't have" — an accreted ~1,900-line executable validator, vendored YAML parser,
write-transactions, and lifecycle machinery. Reading the year-old working reference (all prose, a checker
it largely ignored, and thriving) refuted the machinery's premise. The validator PR was closed unmerged,
the design shrank to reference weight (~1,150 lines of prose across a few files), and the plugin then
drove seven use-triggered releases (0.1.0 → 0.1.7) in a single day, each bump from a real defect surfaced
by an actual run.

The durable spine: a knowledge-graph generator whose health rests on an LLM writing to prose conventions
plus a human approving every plan — no validator. This session is **one witness**; the patterns it seeds
are open, not settled.

**Off-tier source.** This is a raw session transcript, not a chronicle path or docs URL, so it is keyed on
the session UUID. `docs/chronicle/2026-07-15.md` is the curated write-up of the same arc and is still in
the processing queue — a later chronicle run should augment these notes rather than duplicate them.

**Transcript:** `~/.claude/projects/-Users-derek-personal-Developer-claude-code-plugins/284b79f5-c34f-4ad3-b97d-9c78cdc9c46f.jsonl`
(2.8 MB / 1,311 lines), with its 14 subagent transcripts alongside it.

**Raw withheld from this repo's archive — 2026-08-02.** The rendered export was put through the preserve
stage's redaction gate so it could move into `knowledge/sources/raw/`, and it **failed the read-through
half**. It names client organisations alongside specific requests, carries an internal assessment of one
client's stated motives, describes an unreleased platform decision as already affecting customers,
references internal strategy artifacts, and discloses the schema and location of a private work vault. The
deterministic floor **passed** it — its eight findings were one false-positive shape, a variable named `key`
followed by a colon. Either half alone would have published this, which is the case for requiring both,
made on the gate's first run against material the pipeline did not produce itself.

The bar is that content, **not the employer's name**, which is not confidential and appears in this repo
already.

So the raw lives at `~/Developer/session-archive/` — a git repository with a **private** remote
(`ddehart/session-archive`), visibility verified before and after its first push. Unscrubbed on purpose:
substituting entities would make it a derived artifact rather than the raw material, and a scrub is only as
good as the enumeration behind it. Private hosting gets the durability D2 wanted without needing the
artifact to be anything other than what it is.

**This is a genuine exception to D2, not a fact about one file.** D2 says raw commits in-repo and its
rationale explicitly rejects an outside-the-repo location; D7's withhold branch says only that such material
"is not archived at all," which reads as discarded. Neither anticipated raw that must be kept and cannot be
published. See [[raw that cannot be published needs a home the spec does not give it]].

**This note recorded no pointer at all until 2026-07-28**, and the graph had come to believe the transcript
was lost — a claim repeated into the process skill, a decision note, and a spec before anyone checked. It
was never lost. The session spanned two repositories (590 turns in `commons`, 190 in `claude-code-plugins`,
across four working directories and three branches), and a transcript gets one home however many projects
it touches; this one landed under a `commons` worktree slug, which the resolver's `*claude-code-plugins*`
glob cannot match. Moved here on 2026-07-28 because this project was its primary subject.
