---
genitor: "[[observations]]"
tags: [silent-failure, verification]
date: 2026-07-22
supports: ["[[naming a failure shape confers no immunity to it]]", "[[break the self-review chain with a different agent]]"]
---
Four bugs were fixed for sharing one shape — absence of signal read as a negative result. The mechanism
built to propagate those fixes then reproduced it four more times: a generator whose re-run path would
stamp every delta as applied against files containing none; a discovery hook that would report "nothing
pending" from a version-pinned stale log; an installed plugin cache that would have re-applied deleted
deltas; a suppression marker whose free-form key let each run look locally correct while re-raising
forever. All four were found by independent review, not by the author, despite the author having named the
shape in the session's first message and restated it in a dozen commits and briefs.
