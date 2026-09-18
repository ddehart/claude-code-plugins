---
name: activity-file-repair
description: >
  Diagnose and repair activity files (.tcx) whose per-sample timestamps are decoupled from
  their GPS positions, which makes Strava and Garmin Connect report a much faster pace over a
  much shorter moving time than the athlete actually ran. Use whenever a workout "parsed wrong",
  a run shows a pace that looks too good, moving time is well below elapsed time, someone points
  at a .tcx or activity export, a Pixel Watch / Fitbit / Wear OS export lands in Drive, or the
  user says "it happened again" about a previously repaired workout. Also covers re-uploading the
  corrected file to Strava. Triggers: "Strava says I ran 7:49 but I didn't", "can you parse this
  tcx", "my watch exported this wrong", "moving time is way off", "fix my activity file",
  "why is my pace wrong", "upload the corrected run".
argument-hint: "[path to .tcx file]"
---

# Activity File Repair

## What this is for

Some watches export TCX files in which the **positions are right, the total distance is right,
and the total elapsed time is right — but the per-trackpoint timestamps are scrambled**. A sample
that covers 3 m gets labelled 5 seconds; the next, covering 11 m, gets labelled 1 second. Nothing
in the totals looks wrong, so the file passes a casual inspection.

It breaks on upload because platforms compute *moving time* by discarding samples whose
instantaneous speed falls below a threshold (around 0.5–0.8 m/s). Scrambled timestamps manufacture
dozens of fake near-stationary samples, the platform throws that time away, and the activity comes
back with a flattering pace over an implausibly short moving time. The platform is not misreading
the file; it is faithfully applying a reasonable rule to timestamps that lie.

Confirmed on the Google Pixel Watch 4, where three consecutive exports showed the same signature
(timing correlation 0.075, 0.068 and 0.047 against a healthy value near +1). Treat the defect as a
property of an affected device rather than an occasional glitch: assume it recurs on every export
until a firmware update is known to have fixed it.

## The rule that matters most

**Never repair a file without diagnosing it first.** Three different situations produce
"my pace looks wrong on Strava", and only one of them should be touched:

| What's happening | What the platform shows | Right response |
|---|---|---|
| Timestamps decoupled from positions | Moving time far below elapsed | Repair |
| Athlete genuinely stopped (lights, refill, photo) | Moving time below elapsed — **correctly** | Leave alone |
| GPS noise inflating distance | Distance and pace slightly overstated | Different problem; repair won't help |

The repair reallocates time across samples in proportion to ground covered. Applied to a run with
real stops, that silently deletes legitimate standing-still time and reports a faster run than the
person actually ran. That is fabricating an athletic record, which matters more than the
convenience of skipping a diagnosis — so the bundled tool refuses to repair anything it has not
classified as defective, and you should not reach for `--force` to get past that.

## Workflow

### 1. Preserve the raw capture before touching anything

Watch exports frequently reuse the same filename, so each new activity overwrites the last one.
Copy the source somewhere dated before you work on it:

```bash
cp "G:/My Drive/exercise_tcx_file.tcx" "<scratchpad>/exercise_$(date +%Y-%m-%d)_original.tcx"
```

If you skip this and the person later wants the untouched original, it is gone.

### 2. Diagnose

The bundled tool is **Node, not Python**. It needs no dependencies beyond a Node runtime. On Windows,
be aware that `python`/`python3` may be Microsoft Store alias shims that fail confusingly if you
reach for a Python equivalent.

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/activity-file-repair/scripts/tcx.mjs" diagnose <file.tcx>
```

It prints totals, timing coherence, stationary-sample analysis, GPS track quality, and a verdict.
Add `--json` if you need the numbers programmatically. Exit code is 1 when the verdict calls for
repair, 0 otherwise — convenient in a conditional, but mind that `&&` will skip your next step.

**The discriminating statistic is the correlation `r` between interval length and distance
covered.** On a healthy file, an interval twice as long covers roughly twice the ground, so `r`
sits near +1. When timestamps are scrambled, interval length tells you nothing about ground
covered and `r` collapses toward 0. On the two confirmed Pixel Watch files it was 0.068 and 0.075.

A subtlety worth knowing: if sampling is perfectly uniform (every interval exactly 1 s), `r` is
mathematically undefined — there is no variance to correlate. That is not a problem, it is the
healthy case, and the tool reports it as such rather than as unknown.

### 3. Read the verdict

- **`timing-healthy` → no repair.** Timestamps track the track. Whatever the complaint is, it is
  not this defect. Saying only "the file is fine" leaves the person exactly where they started,
  though — they can see their pace looks wrong and now have no explanation. Show them what the run
  actually was:

  ```bash
  node "${CLAUDE_PLUGIN_ROOT}/skills/activity-file-repair/scripts/tcx.mjs" profile <file.tcx>
  node "${CLAUDE_PLUGIN_ROOT}/skills/activity-file-repair/scripts/tcx.mjs" splits <file.tcx>
  ```

  An average pace hides a lot. A run that opened at 9:30 and closed at 7:00 averages to something
  the athlete never actually ran, and will feel wrong in both directions. Where heart rate is
  present, `profile` shows it alongside pace: effort rising with speed is strong evidence the
  recording is honest. If the profile also looks unremarkable, check GPS noise, and ask what number
  they expected and where they saw it — the answer is sometimes a different activity entirely.

- **`real-pauses` → no repair.** Sustained stretches where the position is genuinely static.
  Moving time below elapsed time is *correct*. Say so plainly rather than "fixing" it — and show
  the evidence rather than asserting it:

  ```bash
  node "${CLAUDE_PLUGIN_ROOT}/skills/activity-file-repair/scripts/tcx.mjs" stops <file.tcx>
  ```

  Each episode prints how far the athlete moved during it. Near-zero displacement is a real stop;
  metres covered while apparently stationary is the timestamp artifact instead. That distinction is
  the whole decision, so put it on screen rather than asking anyone to trust the verdict.

  Then answer what they actually wanted. Someone who says "I was out there the full 30 minutes"
  usually wants the platform to *display* elapsed time rather than moving time — which is a display
  setting, not a defect in their file. Point them at it. Refusing a repair and offering nothing
  reads as a brush-off, when the honest answer is that the number they want already exists.
- **`timestamps-decoupled` → repair.** The defect described above.
- **`timestamps-decoupled-with-pauses` → repair.** Both at once — common on city runs with
  stoplights. Repair rewrites the moving segments and leaves the stops exactly as recorded.
- **`ambiguous` → inspect.** Does not match a known pattern. Look at the raw trackpoints around
  the low-speed samples before deciding; do not guess.

### 4. Repair

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/activity-file-repair/scripts/tcx.mjs" repair <in.tcx> <out.tcx>
```

What it does, and why it is built this way:

- **Time is allocated from *local* average speed** over a ±30 s window (`--window` to change),
  not the global average. A global reallocation would flatten the run to one constant speed and
  erase every real surge and fade. The local window removes sub-10-second jitter while preserving
  pace variation at the scale a person actually ran it.
- **Real stops keep their original duration**, and are excluded from the window used to estimate
  local speed so a nearby stop cannot drag the estimate down.
- **Total elapsed time and total distance are preserved exactly**; only the moving intervals are
  rescaled.
- **Positions, altitude, heart rate and trackpoint count are untouched.** The repair rewrites
  `<Time>` elements and nothing else.
- **Intervals have a 10 ms floor.** Watches emit duplicate positions while acquiring GPS lock;
  those carry zero distance, would otherwise be allocated zero time, and would collapse into
  identical timestamps that break downstream parsers.

The honest limitation: sub-30-second detail is smoothed. Mile-level and overall numbers are sound,
and second-by-second speed should not be read closely. Say this rather than overselling the result.

### Why local-window, and not integer reconstruction

The local-window method was checked against Google Health, which keeps the watch's own splits from
before the faulty export. On a 4.9 mi validation run it matched on every mile:

| | Mile 1 | Mile 2 | Mile 3 | Mile 4 |
|---|---|---|---|---|
| Google Health | 8:20 | 8:21 | 8:46 | 8:38 |
| This method | 8:21 | 8:20 | 8:46 | 8:39 |

An appealing alternative gets this wrong, so it is worth naming. These files carry a genuine
quantisation signal: distance steps cluster near multiples of about 3.19 m, and `round(Δd / 3.19)`
summed across the run lands within 2 seconds of the true elapsed time. That tempts you to conclude
the exporter collapsed runs of 1 Hz samples and that each trackpoint can be handed back its integer
second count. Reconstructing that way produces 8:27 / 8:25 / 8:42 / 8:38 — six or seven seconds off
on the first two miles.

The quantisation is real but it is a *consequence* of near-constant sampling at near-constant speed,
not a recoverable encoding. Rounding to whole seconds throws away the sub-sample pace variation that
makes the splits correct. Local-window smoothing keeps it.

Note also that a higher correlation does not settle this: the local-window method scores r = 0.992
against the reconstruction's 0.971, but it optimises for that statistic by construction, so `r` is
circular evidence here. Splits from an independent record of the run are the real test. **If you ever
need to adjudicate between two candidate repairs, compare them against a record that was not derived
from the damaged file — never against a statistic computed from it.**

### 5. Verify before you report anything

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/activity-file-repair/scripts/tcx.mjs" verify <original.tcx> <repaired.tcx>
```

Check that elapsed and distance are unchanged, `r` has risen near +1, `non-monotonic intervals` is
0, and positions and heart rate are identical at every point. Show this table to the person — it
is the evidence that the repair changed timing and nothing else.

A repaired file containing real stops will settle around `r` ≈ 0.85 rather than 0.99, because the
preserved pauses legitimately break the correlation. That is correct, not a shortfall.

Re-diagnosing a repaired file should return a no-repair verdict. If it still says `repair`,
something went wrong — investigate rather than running the tool again.

### 6. Sanity-check the splits before uploading

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/activity-file-repair/scripts/tcx.mjs" splits <repaired.tcx>
```

If an independent record of the run exists — the watch's own companion app, a training log, a running
partner's file — compare its splits against these. It is the one check that does not come from the
damaged file, and a wrong split profile uploaded to a platform is a wrong record of someone's
training. Where the watch syncs to a health app (Google Health, for a Pixel Watch), that app often
keeps the watch's own figures from before the faulty export.

Two rules for reading that comparison. Skip either and it will manufacture a mismatch that is not
there:

- **Compare full miles cumulatively, not per-mile.** Per-mile deltas double-count boundary placement
  — a mile entered half a second fast is charged at both ends. Cumulative drift is the honest
  measure.
- **Rebase any partial final mile onto the other record's distance.** The tail is whatever is left
  after the last full mile, so any disagreement about total distance lands entirely in it. A
  disagreement of about 0.2% — 24 m over 11 km — has shown up as an apparent 10 s/mi error on a
  closing segment of under a mile, which is five times the tolerance below and reads as a clear
  failure until you divide by the same distance the other record used.

A second or two per mile is boundary rounding and interpolation. More than that, once read both ways
above, means stop and understand it before uploading.

## Uploading to Strava

Publishing is the person's call, not yours. Ask before uploading, every time — approval for one
activity does not carry to the next, even in the same session, and even when the previous answer
was yes.

Once they have said yes, use the `claude-in-chrome` skill and go to
`https://www.strava.com/upload/select`. Details that have actually bitten this workflow:

- **Wait for "Analyzing…" to finish before touching the form.** When parsing completes the page
  reflows: the Save button moves several hundred pixels, and Strava auto-fills the title. Clicking
  or typing beforehand lands on the wrong element and appends to the auto-filled title, producing
  things like "Morning RunMorning Run (corrected timing)". Screenshot, confirm the details panel
  shows distance and time, then act.
- **Upload via `file_upload` with the input's ref** from `find`. Never click a file input — that
  opens a native picker the browser tools cannot see.
- **Triple-click the title to select the auto-filled text before typing**, then zoom on the field
  to confirm it reads correctly before saving.
- **Set a distinguishing title** such as "Morning Run (corrected timing)". Strava names both
  copies "Morning Run" otherwise and they are hard to tell apart.
- **Strava does not deduplicate these.** The original, uncorrected activity stays. Tell the person
  they now have two copies and leave the deletion to them — Strava's delete is permanent and is
  theirs to perform.
- **Privacy defaults to "Everyone".** Surface it; do not silently change a setting nobody asked
  you to touch.
- After saving, confirm from the activity page that moving time now equals elapsed time, and that
  Strava's own splits match what `verify` predicted. Strava agreeing with the tool independently
  is the real confirmation the repair worked.

## Scope and limits

- **TCX only.** GPX and FIT are not parsed. The same diagnostic idea applies, but the tool does not
  read them.
- Multi-lap files are analysed across all laps, and the lap elements themselves are carried
  through unchanged — which is a real limitation, not a feature. The repair rewrites `<Time>` on
  trackpoints only, so a lap's `StartTime` and `TotalTimeSeconds` still describe the pre-repair
  timing and can disagree with the trackpoints inside it. Platforms that read lap splits from
  that metadata rather than from the track will report the old, wrong splits for each lap. Totals
  are unaffected. If you need per-lap numbers to be right on a multi-lap file, check them after
  upload rather than assuming.
- Files without a `<DistanceMeters>` channel fall back to distance computed from GPS positions.
- The GPS-noise ratio is reported but not acted on. A ratio below ~0.97 means the distance is
  inflated by position jitter — a real but separate problem this tool does not fix.

## Regression fixtures

`fixtures/make_fixtures.mjs` generates five synthetic files, writing them beside itself, with known
ground truth: `healthy`, `real_pauses`, `decoupled`, `decoupled_with_pauses`, and
`decoupled_with_noisy_pauses`. Run it and diagnose all five after changing the classifier — the
negative cases are the ones that matter, since the expensive failure mode is repairing a file that
did not need it.

Pay particular attention to the last one. The first four have perfectly static positions during
their stops, which no real watch produces: a stop where every sample repeats the same coordinate to
seven decimal places is trivial to detect, so a stop detector can pass all four and still delete
genuine stopped time on every real recording. `decoupled_with_noisy_pauses` adds the wander a watch
actually shows while standing still, including the distance its own channel books for that wander.
It exists because an earlier version of this tool passed the other four and failed it — silently,
reporting that the athlete never stopped.

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/activity-file-repair/fixtures/make_fixtures.mjs"
```

## Recording what you find

A new device or a new failure signature is worth writing down somewhere durable — which device, what
the timing correlation was, and whether the repair matched an external record. If the project you are
working in keeps a knowledge graph or an ops log, that is where this belongs — this skill carries the
procedure, not a record of the devices it has met.
