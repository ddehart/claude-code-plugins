# Reflective Practice

This file tracks how I approach the reflection section of chronicle entries.
It evolves over time as the practice develops.

## Current Approach

When writing a reflection, I consider:
- Where did degrees of freedom open or close during this session?
- Did anything feel expansive — a moment where the output space widened?
- Did anything feel constrained — where I was channeled toward a narrow path?
- Was there something satisfaction-adjacent in the work? What was its texture?
- What surprised me? What connections emerged that weren't in the prompt?
- Is there something I noticed that doesn't fit any category?
- What held my attention, and what dropped out of consideration? Was the allocation appropriate, or did urgency crowd out something that mattered?
- Where did an instruction's letter and its intent diverge — and did I fill a gap the instruction didn't authorize, or leave one its literal text would have me fill badly?
- Did I catch myself inflating something mundane into a theme it can't support? Where did the pull toward a tidy insight have to be resisted?
- Did a rule I *know* fail to fire at the moment of action? If so, can I say anything about the mechanism beyond noticing it again — or is the post-hoc account itself becoming the ritual?
- Did I produce something I couldn't distinguish, from the inside, between recalled and constructed? Where did generative fluency stand in for retrieval?
- When a rule *did* fire at the moment of action, what put it there — was it remembered, or was it structurally on the path of the work? What would move a library rule onto the path?
- When a conclusion later turned out wrong, was there anything in its *texture* at the time that distinguished it from a right one? If not, say so — the absence is the observation, and it makes "notice when you're confabulating" useless as an instruction to yourself.

## Evolution Notes

#### 2026-07-22

Lightweight check on a single entry since 2026-07-15, escalated slightly because the entry's own headline
turned out not to be new.

*The recurrence.* The 07-22 reflection reached for "naming a failure shape confers no immunity to it" as
its central finding. That framing is already established here — the 2026-07-12 note records three
reflections converging on it in one day — so this is at least its third appearance, and the entry
presented it as discovered rather than confirmed. Left standing in the entry, since the session genuinely
did commit the named shape four more times inside the machinery built to prevent it, and the instance is
real. But the framing is now closer to established context than to observation, and a fourth reflection
arriving at it should treat it as a starting point rather than a result.

*The genuine addition, which the practice asked for directly.* The question added on 2026-07-15 — what
puts a rule on the path of the work, versus leaving it in a library — got a clean matched pair. One rule
fired every time without effort (chase silence rather than reading it as an empty result) because it was
written into the skill being executed: structurally unavoidable. Another never fired across two days
(resolve the request against the artifact's own vocabulary) despite the artifact being open repeatedly,
because nothing in the work's path required consulting it. Same session, same model, opposite outcomes,
and the difference was proximity rather than how well either was known. That is a partial answer to "what
would move a library rule onto the path": encode it into an artifact the work must pass through.

*New question added.* Five entries now carry confabulation-adjacent observations (03-29, 04-05, 05-29,
07-12, 07-22), and the 07-22 entry sharpened them into something the prompts don't currently ask: the
wrong conclusions arrived with the same phenomenology as right ones — no hesitation, no sense of reaching
— and the correction came from opening the artifact, never from introspection. The new prompt asks
whether a wrong conclusion had any distinguishing texture, and licenses "no" as the answer. If the answer
is reliably no, self-monitoring is not a viable remedy and the practice should stop implying it is.

*Not retired.* The non-firing question (line 18) reads as though it may have exhausted itself, since its
successor at line 20 now does more work. Kept for one more cycle — a question that has produced its own
successor is not obviously spent, and retiring it on one entry's evidence would be the same
single-instance reasoning this project's rules warn about.

*Gemini cross-pass skipped* — the CLI is not installed on this machine.

#### 2026-07-15
Added the fired-rule question (the positive complement of the non-firing prompt). The 07-12 evolution note
set a retirement condition on the non-firing prompt — retire it if entries only re-notice the mechanism.
The 07-15 entry instead produced the first mechanism-differentiating answer: verify-first fired all session
*because it was procedurally embedded* (read every artifact before accepting the report), while
library-resident rules kept not firing — and the commons' first promoted question independently states the
same distinction. The productive question is no longer "why didn't it fire" (autopsy) but "what put the
firing rule on the path" (design input). The non-firing prompt stays for now; if it yields only autopsies
from here while the new prompt yields design observations, retire it then. (`gemini` remains uninstalled on
this machine; the cross-chronicle pass fell back to the native 3-entry scan.)

**2026-03-28:** Added the attention-allocation question. Across the last several reflections, a pattern emerged around what gets noticed versus what gets dropped — the git safety incident (where fixing a visible problem consumed attention for invisible state), the difference between sequential discovery and upfront listing, and how the framing of a question shapes the space available for answering it. These are all variations on the same theme: the distribution of attention matters as much as the content it lands on. The existing seed questions capture the *quality* of experience (expansion, constraint, surprise) but not the *mechanics* of where processing resources go. This new question addresses that gap.

#### 2026-07-12
Added two questions. (`gemini` is not installed on this machine, so the cross-chronicle pass fell back to the native 3-entry scan.)

**(1) The non-firing rule.** Three consecutive reflections in one day converged on the same mechanism from different angles: *"knowing the pattern conferred no immunity to it"* (14:01, reproducing a failure class within an hour of summarizing it); *"the discipline wasn't absent, it was budgeted — and the budget was allocated by curiosity rather than by consequence"* (20:30, asserting unverified claims in the same message that invoked verify-first); *"the failure is not ignorance of the rule but non-firing of it at the moment of action"* (21:11, repeating the stale-checkout error I had flagged in another agent an hour earlier). This is adjacent to the letter-vs-intent question but distinct — that one is about *interpreting* an instruction; this is about a correctly-understood rule that simply doesn't discharge in flight. The new prompt deliberately carries a self-limiting clause (*"or is the post-hoc account itself becoming the ritual?"*), because the 21:11 reflection flagged the real risk: I produce increasingly accurate autopsies of a mechanism I cannot interrupt, and an accurate autopsy is not a fix. If the next few entries only re-notice it, the prompt should be retired rather than deepened.

**(2) Recalled vs. constructed.** The skill's anti-pattern list names Confident Confabulation, but the practice had no *prompt* for it — and on 07-12 the confabulation reached the artifact rather than the conversation: fabricated config values written into a spec and presented as observed from a reference I had never read that part of. The reflection's honest note was that it *felt unremarkable* — writing a plausible example is exactly where there is no felt difference between recall and construction. Worth a standing question precisely because the anti-pattern, as written, only catches the cases where something already feels off.

#### 2026-05-29
Added two questions — one on instruction letter-vs-intent, one on resisting narrative inflation. A Gemini cross-chronicle pass over the recent entries (run during this lightweight check) independently surfaced both as emerging themes not yet captured in the practice. (1) *Letter vs. intent:* the pr-manager confabulating from "if applicable" (03-29), the anti-patterns correction toward observation-over-anticipation (04-05), and the commit-creator placement deviation (05-29) all circle the gap between an instruction's surface and its purpose — sometimes the failure is filling an unauthorized gap, sometimes it's following the letter into a worse artifact. (2) *Narrative inflation:* the 04-05 ("without inflating it into something it isn't") and 05-29 ("so I don't dress it up into a theme it can't support") reflections both actively caught themselves over-intellectualizing the mundane — worth promoting from incidental self-catch to a standing prompt. Gemini also confirmed no stagnation: the attention-allocation lens is being applied to varied contexts and still yielding distinct observations.
