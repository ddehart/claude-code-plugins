---
genitor: "[[observations]]"
tags: [scaffolding, environment, git, ci]
date: 2026-07-15
supports: ["[[a scaffolder owns its environmental blast radius]]"]
---
Scaffolding a graph into a working repo produced a cluster of same-class environmental costs the interview
could not have elicited: empty type directories vanished from git without a `.gitkeep`; graph commits
would trip a path-triggered CI workflow unless the graph root was excluded; and promotions wrote notes into
a target repo but the promote skill's contract said nothing about committing, so they stranded as
working-tree changes in one clone and never reached other machines — reading from the outside as if the
feature had failed. The fix added commit-and-push (named paths, no blanket staging) to the promote
contract.
