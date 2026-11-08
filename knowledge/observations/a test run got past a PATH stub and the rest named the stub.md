---
genitor: "[[observations]]"
tags: [testing, stubs, harness]
date: 2026-11-06
supports: ["[[execution against real data catches what authoring and review miss]]"]
---
Stub cases put a fake `agy` first on PATH so they would spend no quota. One run's shell resolved the real binary anyway, for reasons never established, and made two unapproved real passes. A `BASH_ENV` shell function stopped it in the runs after. In the other runs, the model read the stub, said the cross-pass wasn't real, and sometimes ran a costlier fallback. A stub the subject can inspect is part of what is under test.
