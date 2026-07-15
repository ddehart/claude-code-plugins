---
genitor: "[[patterns]]"
tags: [prose-as-code, skills, precision]
---

# ambiguous prose in an LLM-executed skill is a correctness bug

A skill is prose executed by an LLM, so a sentence that can be misread is a defect on par with a code bug —
even in a change that touches "no executable code." A pronoun that binds to the wrong noun, or a soft
"if applicable" condition, will be executed wrong by some fraction of sessions and can break the very
structure the design rests on. Write for the misreading: when a field is required by the target, instruct
an explicit check rather than a conditional; when a reference could bind two ways, disambiguate it. Two
independent promotion runs disagreeing on whether to add a date is the drift a firmer sentence prevents.

*One witness (2026-07-15). Open.*

## evidence
- [[a soft if-applicable instruction produced two promotion runs that disagreed]]

## related
- [[a generator reproduces its template's flaws]]
- [[the generated process skill]]
