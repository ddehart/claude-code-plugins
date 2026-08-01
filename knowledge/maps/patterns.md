---
genitor: "[[principium]]"
tags: [map]
---

# Patterns

Open attractors — recurring truths about how plugins, skills, and agents should be built. Each accumulates
evidence and carries a one-clause "so what"; none reaches a verdict. Entries are annotated:
`- [[title]] — the "so what" in one clause`. All below are one-witness (2026-07-15), open.

- [[a generator reproduces its template's flaws]] — generated output is wrong because its template is; fix the root cause upstream, not just the instance.
- [[a scaffolder owns its environmental blast radius]] — landing artifacts in a live repo/machine creates second-order duties (`.gitkeep`, CI triggers, commit-and-push, gap-detection) the tool must own.
- [[added complexity generates its own defect supply]] — a verification loop whose findings are mostly its own prior fixes is debugging itself; flat defect yield measures the process, not the artifact.
- [[ambiguous prose in an LLM-executed skill is a correctness bug]] — a skill is prose an LLM executes, so a misreadable sentence is a defect even with "no executable code"; write for the misreading.
- [[break the self-review chain with a different agent]] — an author agrees with their own intent; a *different* agent briefed to build (not attack) is what measures the artifact.
- [[build enforcement against demonstrated need, not anticipated failure]] — machinery earns its place only against silent, compounding, or frequent errors; defer the rest to an evidence trigger.
- [[execution against real data catches what authoring and review miss]] — run a just-authored mechanism end-to-end on real input; verify guards with a planted failure, never a happy-path pass.
- [[prose conventions plus human approval can replace a validator]] — when a human approves every write, a validator mostly guards an implementer who doesn't exist; conventions carry the structure.
- [[naming a failure shape confers no immunity to it]] — the shape survived being named, specified against, and built around; fluency is not application.
- [[a check inherits the frame of whoever briefed it]] — a different reviewer buys independence from execution, never from the author's intent or scope.
- [[a plausible story arrests the investigation before the mechanism is found]] — a fitting explanation stops the search as effectively as a fitting answer would.
- [[justifying prose drifts from the thing it justifies]] — the instruction stays sound while its stated reason rots, and rationale travels further than the instruction.
- [[a workaround written up as a decision stops reading as a workaround]] — a correct premise with the opposite conclusion drawn from it; locally reasonable, so an audit finds nothing wrong.
- [[a claim restated into several artifacts starts reading as corroborated]] — copies are shaped like independent observations, so mentions get counted as witnesses; the terminus is a copy that has become an instruction.
- [[concurrent writers are invisible until write time]] — no lock, no writer identity, and a screen minutes before a write can read a state that no longer exists.
- [[an index omission silently disables the check that reads it]] — a screen over an incomplete index returns the same shape of answer as one over a complete index.
