---
genitor: "[[observations]]"
tags: [review, verification, security]
date: 2026-08-01
supports: ["[[naming a failure shape confers no immunity to it]]"]
---
A bash secret scanner guarding a public archive was found broken five times across three independent
reviewers — a subagent review twice and a CI check once. Every defect was a fail-open: a real credential
present, the scan reporting clean and exiting 0.

The mechanisms were unrelated to each other. A pattern beginning with `-` eaten by grep as options, with
stderr discarded. A `die` running inside a command substitution, killing only the subshell. Quote
characters in a placeholder class, so quoting a credential made it invisible. Dictionary placeholders
matched as a prefix, so `API_KEY=nullXk29…` was suppressed. Only the first match on a line checked, so a
placeholder shadowed a real credential behind it.

None was visible to reading the code. The reviewer that found the first three said so directly:
*"Everything below was executed, not read."* The author's own reading, twice, found none of them — and
one of the defects falsified a fail-closed claim the author had already published.
