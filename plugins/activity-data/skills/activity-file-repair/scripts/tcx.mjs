#!/usr/bin/env node
// tcx.mjs — diagnose and repair timing defects in Garmin TCX activity files.
// Node only (this machine has no Python). Usage:
//   node tcx.mjs diagnose <file.tcx> [--json]
//   node tcx.mjs repair   <in.tcx> <out.tcx> [--window 30] [--force]
//   node tcx.mjs verify   <original.tcx> <repaired.tcx>
import { readFileSync, writeFileSync } from 'node:fs';

// ---------- parsing ----------
const num = (b, t) => { const m = b.match(new RegExp(`<${t}>([^<]*)</${t}>`)); return m ? parseFloat(m[1]) : null; };
const raw = (b, t) => { const m = b.match(new RegExp(`<${t}>([^<]*)</${t}>`)); return m ? m[1] : null; };

function parse(path) {
  const xml = readFileSync(path, 'utf8');
  const laps = [...xml.matchAll(/<Lap\b[^>]*>[\s\S]*?<\/Lap>/g)].map(m => m[0]);
  const pts = [];
  (laps.length ? laps : [xml]).forEach((lapXml, lapIdx) => {
    for (const tp of lapXml.matchAll(/<Trackpoint>([\s\S]*?)<\/Trackpoint>/g)) {
      const b = tp[1];
      const time = raw(b, 'Time');
      if (!time) continue;
      pts.push({
        lap: lapIdx,
        t: new Date(time).getTime() / 1000,
        lat: num(b, 'LatitudeDegrees'), lon: num(b, 'LongitudeDegrees'),
        latS: raw(b, 'LatitudeDegrees'), lonS: raw(b, 'LongitudeDegrees'),
        dist: num(b, 'DistanceMeters'),
        hr: num(b, 'Value'),
      });
    }
  });
  if (pts.length < 2) throw new Error(`${path}: fewer than 2 trackpoints with <Time> — not a usable TCX track.`);
  return { xml, pts, lapCount: laps.length };
}

const R = 6371000, rad = d => d * Math.PI / 180;
function haversine(a, b) {
  if (a.lat == null || b.lat == null) return 0;
  const dLat = rad(b.lat - a.lat), dLon = rad(b.lon - a.lon);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

// Cumulative distance: prefer the file's own channel, fall back to GPS positions.
function cumulative(pts) {
  if (pts.every(p => p.dist != null)) return pts.map(p => p.dist);
  const out = [0];
  for (let i = 1; i < pts.length; i++) out.push(out[i - 1] + haversine(pts[i - 1], pts[i]));
  return out;
}

function pearson(xs, ys) {
  const n = xs.length; if (n < 2) return NaN;
  let sx = 0, sy = 0, sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) { sx += xs[i]; sy += ys[i]; sxy += xs[i] * ys[i]; sxx += xs[i] ** 2; syy += ys[i] ** 2; }
  const den = Math.sqrt((n * sxx - sx * sx) * (n * syy - sy * sy));
  return den === 0 ? NaN : (n * sxy - sx * sy) / den;
}

const STOP = 0.5;      // m/s below which a sample looks stationary
const LOWSPD = 0.75;   // m/s — typical moving-time cutoff used by activity platforms
const PAUSE_SEC = 15;  // a stationary stretch this long, going nowhere, is a real stop
const PAUSE_M = 2;     // ...where "nowhere" means less than this much ground covered

// Shared measurement pass. `pause` marks intervals belonging to a real stop:
// sustained stretches where the athlete genuinely did not move. Those are the
// intervals a repair must leave alone.
function measure(pts, D) {
  const n = pts.length;
  const dts = [], dds = [], spd = [];
  let dupPos = 0;
  for (let i = 1; i < n; i++) {
    const dt = pts[i].t - pts[i - 1].t, dd = D[i] - D[i - 1];
    dts.push(dt); dds.push(dd); spd.push(dt > 0 ? dd / dt : 0);
    if (pts[i].latS != null && pts[i].latS === pts[i - 1].latS && pts[i].lonS === pts[i - 1].lonS) dupPos++;
  }
  // Group contiguous stationary-looking intervals into episodes.
  const episodes = [];
  let cur = null;
  for (let i = 0; i < spd.length; i++) {
    if (spd[i] < STOP) { cur = cur || { from: i, to: i, dur: 0, dist: 0, n: 0 }; cur.to = i; cur.dur += dts[i]; cur.dist += dds[i]; cur.n++; }
    else if (cur) { episodes.push(cur); cur = null; }
  }
  if (cur) episodes.push(cur);

  const realPauses = episodes.filter(e => e.dur >= PAUSE_SEC && e.dist < PAUSE_M);
  const pause = new Array(spd.length).fill(false);
  for (const e of realPauses) for (let i = e.from; i <= e.to; i++) pause[i] = true;

  const mean = dts.reduce((a, b) => a + b, 0) / dts.length;
  const sd = Math.sqrt(dts.reduce((a, b) => a + (b - mean) ** 2, 0) / dts.length);
  return { dts, dds, spd, dupPos, episodes, realPauses, pause, dtMean: mean, dtCV: mean > 0 ? sd / mean : 0 };
}

// ---------- diagnosis ----------
function analyse(path) {
  const { pts, lapCount } = parse(path);
  const D = cumulative(pts);
  const n = pts.length;
  const dur = pts[n - 1].t - pts[0].t;
  const dist = D[n - 1] - D[0];
  const m = measure(pts, D);
  const r = pearson(m.dts, m.dds);

  // GPS noise: does measured distance shrink when the track is sampled coarsely?
  const step = Math.max(1, Math.round(15 / (dur / (n - 1))));
  const decim = k => { let d = 0; for (let i = k; i < n; i += k) d += haversine(pts[i - k], pts[i]); return d; };
  const gpsFull = decim(1), gpsCoarse = decim(step);
  const noiseRatio = gpsFull > 0 ? gpsCoarse / gpsFull : 1;

  const epDurs = m.episodes.map(e => e.dur).sort((a, b) => a - b);
  const medianEp = epDurs.length ? epDurs[Math.floor(epDurs.length / 2)] : 0;
  const stoppedTime = m.episodes.reduce((a, e) => a + e.dur, 0);
  const pauseTime = m.realPauses.reduce((a, e) => a + e.dur, 0);
  let lowTime = 0;
  for (let i = 0; i < m.spd.length; i++) if (m.spd[i] < LOWSPD) lowTime += m.dts[i];

  // Classification.
  //
  // Two independent questions. (1) Are there real stops? Sustained stretches
  // going nowhere are legitimate stopped time — a platform reporting moving time
  // below elapsed time is CORRECT about those, and a repair must preserve them.
  // (2) Do the timestamps track the ground covered? When sampling is uniform the
  // correlation is undefined (no variance to correlate), and uniform sampling is
  // itself evidence the clock is regular — so that case is healthy, not unknown.
  const uniform = m.dtCV < 0.02;
  const decoupled = !uniform && !Number.isNaN(r) && r < 0.5;
  let verdict, action, why;
  if (decoupled && m.realPauses.length) {
    verdict = 'timestamps-decoupled-with-pauses'; action = 'repair';
    why = `Timestamps are uncorrelated with distance covered (r=${r.toFixed(3)}), and there are also ${m.realPauses.length} genuine stop(s) totalling ${hms(pauseTime)}. Repair rewrites the moving segments and leaves the stops untouched.`;
  } else if (decoupled) {
    verdict = 'timestamps-decoupled'; action = 'repair';
    why = `Interval length is uncorrelated with distance covered (r=${r.toFixed(3)}) across ${m.dts.length} intervals of varying length. The athlete never actually stopped, so the low apparent speeds are a timestamp artifact.`;
  } else if (m.realPauses.length) {
    verdict = 'real-pauses'; action = 'no-repair';
    why = `${m.realPauses.length} sustained episode(s) totalling ${hms(pauseTime)} where the position is genuinely static — real stops. Moving time below elapsed time is correct here; nothing to repair.`;
  } else if (uniform) {
    verdict = 'timing-healthy'; action = 'no-repair';
    why = `Sampling is uniform (${m.dtMean.toFixed(2)}s intervals) with no sustained stationary episodes. Regular timestamps, nothing to repair.`;
  } else if (r >= 0.9) {
    verdict = 'timing-healthy'; action = 'no-repair';
    why = `Interval length tracks distance covered (r=${r.toFixed(3)}). Timestamps are consistent with the track.`;
  } else {
    verdict = 'ambiguous'; action = 'inspect';
    why = `r=${r.toFixed(3)} with interval variation (CV=${m.dtCV.toFixed(2)}) — between the healthy and decoupled patterns. Inspect before repairing.`;
  }

  return {
    file: path, points: n, laps: lapCount,
    elapsedSec: dur, distanceM: dist,
    avgPaceSecPerMile: dist > 0 ? dur / (dist / 1609.344) : null,
    correlation: r, intervalCV: m.dtCV, intervalMeanSec: m.dtMean,
    gpsNoiseRatio: noiseRatio,
    duplicatePositions: m.dupPos,
    stoppedEpisodes: m.episodes.length, medianEpisodeSec: medianEp,
    realPauseCount: m.realPauses.length, realPauseSec: pauseTime,
    stoppedTimeSec: stoppedTime, lowSpeedTimeSec: lowTime,
    projectedMovingTimeSec: dur - lowTime,
    minSpeed: Math.min(...m.spd), maxSpeed: Math.max(...m.spd),
    nonMonotonic: m.dts.filter(d => d <= 0).length,
    verdict, action, why,
  };
}

// ---------- formatting ----------
const hms = s => {
  s = Math.round(s);
  const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
  return h ? `${h}:${String(m).padStart(2, '0')}:${String(x).padStart(2, '0')}`
           : `${m}:${String(x).padStart(2, '0')}`;
};
const pace = s => (s == null || !isFinite(s)) ? 'n/a'
  : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`;

function report(a) {
  const mi = a.distanceM / 1609.344;
  return [
    `File            : ${a.file}`,
    `Trackpoints     : ${a.points} across ${a.laps} lap(s)`,
    `Elapsed         : ${hms(a.elapsedSec)}`,
    `Distance        : ${a.distanceM.toFixed(0)} m (${mi.toFixed(2)} mi)`,
    `Average pace    : ${pace(a.avgPaceSecPerMile)} /mi`,
    ``,
    `Timing coherence (interval length vs distance covered)`,
    `  correlation r : ${Number.isNaN(a.correlation) ? 'undefined (uniform sampling)' : a.correlation.toFixed(3)}   [healthy >= 0.9 | decoupled < 0.5]`,
    `  interval      : mean ${a.intervalMeanSec.toFixed(2)}s, variation CV ${a.intervalCV.toFixed(3)}`,
    `  speed range   : ${a.minSpeed.toFixed(2)} - ${a.maxSpeed.toFixed(2)} m/s`,
    `  non-monotonic : ${a.nonMonotonic} interval(s) <= 0`,
    ``,
    `Stationary-looking samples`,
    `  episodes      : ${a.stoppedEpisodes} (median ${a.medianEpisodeSec.toFixed(1)}s)`,
    `  real stops    : ${a.realPauseCount} totalling ${hms(a.realPauseSec)}  [sustained + genuinely static; preserved by repair]`,
    `  total stopped : ${hms(a.stoppedTimeSec)}`,
    `  below ${LOWSPD} m/s : ${hms(a.lowSpeedTimeSec)}  -> platform would show moving time ${hms(a.projectedMovingTimeSec)} @ ${pace(a.projectedMovingTimeSec / mi)} /mi`,
    ``,
    `GPS track quality`,
    `  coarse/fine distance ratio : ${a.gpsNoiseRatio.toFixed(4)}   [< 0.97 suggests noise-inflated distance]`,
    `  duplicate positions        : ${a.duplicatePositions}`,
    ``,
    `VERDICT: ${a.verdict}  ->  ${a.action}`,
    `  ${a.why}`,
  ].join('\n');
}

// ---------- repair ----------
function repair(inPath, outPath, windowSec, force) {
  const a = analyse(inPath);
  if (a.action !== 'repair' && !force) {
    console.error(report(a));
    console.error(`\nRefusing to repair: verdict is "${a.verdict}".`);
    console.error(`Repair reallocates time by distance, which assumes the athlete never actually stopped.`);
    console.error(`If you have established that assumption holds here, re-run with --force.`);
    process.exit(2);
  }
  const { xml, pts } = parse(inPath);
  const D = cumulative(pts), n = pts.length;
  const t0 = pts[0].t, total = pts[n - 1].t - t0;
  const el = pts.map(p => p.t - t0);
  const m = measure(pts, D);

  // Real stops keep their original duration: the athlete really was standing
  // still, and that time is part of an honest record of the activity. Only the
  // moving intervals get their time reallocated.
  const movingBudget = m.dts.reduce((a, d, i) => a + (m.pause[i] ? 0 : d), 0);

  // Allocate each moving interval's time from the LOCAL average speed rather than
  // the global average, so genuine pace variation across the run survives and only
  // the sample-to-sample jitter is removed. Paused intervals are excluded from the
  // window so a nearby stop cannot drag the local speed estimate down.
  const dtNew = new Array(m.dts.length);
  for (let i = 1; i < n; i++) {
    const k = i - 1;
    if (m.pause[k]) { dtNew[k] = m.dts[k]; continue; }
    let lo = i, hi = i;
    while (lo > 0 && el[i] - el[lo - 1] < windowSec) lo--;
    while (hi < n - 1 && el[hi + 1] - el[i] < windowSec) hi++;
    let wT = 0, wD = 0;
    for (let j = lo; j < hi; j++) if (!m.pause[j]) { wT += m.dts[j]; wD += m.dds[j]; }
    const v = (wT > 0 && wD > 0) ? wD / wT : (D[n - 1] - D[0]) / total;
    // 10 ms floor: duplicate GPS positions carry zero distance and would otherwise
    // be allocated zero time, collapsing into identical timestamps.
    dtNew[k] = Math.max(m.dds[k] / v, 0.01);
  }
  // Rescale only the moving intervals, so total elapsed time is preserved exactly.
  const movingSum = dtNew.reduce((a, d, i) => a + (m.pause[i] ? 0 : d), 0);
  const factor = movingSum > 0 ? movingBudget / movingSum : 1;
  const scaled = dtNew.map((d, i) => m.pause[i] ? d : d * factor);
  const times = [0];
  for (const d of scaled) times.push(times[times.length - 1] + d);

  const stamp = s => new Date((t0 + s) * 1000).toISOString().slice(0, 23) + 'Z';
  let k = 0;
  const out = xml.replace(/(<Trackpoint>[\s\S]*?<Time>)([^<]*)(<\/Time>)/g,
    (m, pre, _old, post) => pre + stamp(times[k++]) + post);
  if (k !== n) throw new Error(`Rewrote ${k} timestamps but parsed ${n} trackpoints — aborting rather than writing a mismatched file.`);
  writeFileSync(outPath, out);
  return { a, outPath, rewritten: k };
}

// ---------- verify ----------
function verify(origPath, newPath) {
  const o = analyse(origPath), p = analyse(newPath);
  const po = parse(origPath).pts, pn = parse(newPath).pts;
  let posSame = 0, hrSame = 0;
  for (let i = 0; i < Math.min(po.length, pn.length); i++) {
    if (po[i].latS === pn[i].latS && po[i].lonS === pn[i].lonS) posSame++;
    if (po[i].hr === pn[i].hr) hrSame++;
  }
  const row = (label, a, b, fmt = x => x) =>
    `  ${label.padEnd(26)} ${String(fmt(a)).padStart(12)}   ${String(fmt(b)).padStart(12)}`;
  const mi = x => x.distanceM / 1609.344;
  return [
    `  ${''.padEnd(26)} ${'ORIGINAL'.padStart(12)}   ${'REPAIRED'.padStart(12)}`,
    row('elapsed', o.elapsedSec, p.elapsedSec, hms),
    row('distance (mi)', mi(o), mi(p), x => x.toFixed(2)),
    row('average pace /mi', o.avgPaceSecPerMile, p.avgPaceSecPerMile, pace),
    row('correlation r', o.correlation, p.correlation, x => x.toFixed(3)),
    row('min speed m/s', o.minSpeed, p.minSpeed, x => x.toFixed(2)),
    row('time below 0.75 m/s', o.lowSpeedTimeSec, p.lowSpeedTimeSec, hms),
    row('projected moving time', o.projectedMovingTimeSec, p.projectedMovingTimeSec, hms),
    row('non-monotonic intervals', o.nonMonotonic, p.nonMonotonic),
    ``,
    `  positions identical: ${posSame}/${po.length}    heart rate identical: ${hrSame}/${po.length}`,
    `  trackpoint count:    ${po.length} -> ${pn.length}`,
  ].join('\n');
}

// ---------- splits ----------
// Split times are what a repair is actually judged on, so they need to come out
// of the same parser rather than a one-off script written at the call site.
function splits(path, unitM, unitName) {
  const { pts } = parse(path);
  const D = cumulative(pts), n = pts.length;
  const t0 = pts[0].t;
  const out = [];
  let mark = 1, prev = 0;
  for (let i = 1; i < n; i++) {
    while (D[i] - D[0] >= mark * unitM) {
      const target = mark * unitM + D[0];
      const span = D[i] - D[i - 1];
      const frac = span > 0 ? (target - D[i - 1]) / span : 0;
      const at = (pts[i - 1].t - t0) + frac * (pts[i].t - pts[i - 1].t);
      out.push({ label: String(mark), sec: at - prev });
      prev = at; mark++;
    }
  }
  const tail = (D[n - 1] - D[0]) / unitM - (mark - 1);
  if (tail > 0.01) out.push({ label: tail.toFixed(2), sec: ((pts[n - 1].t - t0) - prev) / tail, partial: true });
  return [
    `Splits per ${unitName} — ${path}`,
    ...out.map(s => `  ${s.label.padStart(5)}  ${pace(s.sec)}${s.partial ? ` /${unitName} over the final ${s.label} ${unitName}` : ''}`),
  ].join('\n');
}

// Where the stationary episodes are, and whether the athlete truly stood still in each.
// Printed rather than left for each caller to recompute: "artifact or real stop" is the
// judgment the whole workflow turns on, and it deserves the evidence on screen.
function stops(path) {
  const { pts } = parse(path);
  const D = cumulative(pts);
  const m = measure(pts, D);
  const out = [
    `Stationary episodes — ${path}`,
    `  ${m.episodes.length} episode(s); ${m.realPauses.length} classified as real stops`,
    '',
  ];
  if (!m.episodes.length) {
    out.push('  none — no samples fall below the stationary threshold.');
    return out.join('\n');
  }
  out.push('     start       dur     moved   displacement   verdict');
  for (const e of m.episodes) {
    const t0 = pts[e.from].t - pts[0].t;
    const disp = haversine(pts[e.from], pts[Math.min(e.to + 1, pts.length - 1)]);
    const real = m.realPauses.includes(e);
    out.push(
      `  ${hms(t0).padStart(8)}  ${(e.dur.toFixed(0) + 's').padStart(6)}` +
      `  ${(e.dist.toFixed(1) + 'm').padStart(7)}  ${(disp.toFixed(1) + ' m').padStart(12)}` +
      `   ${real ? 'real stop' : 'artifact'}`);
  }
  out.push('');
  out.push("Displacement is straight-line distance between the episode's endpoints. Near zero means the");
  out.push('athlete genuinely did not move, so that time is real and a repair must preserve it. Metres');
  out.push('covered while apparently stationary means the timestamps are lying about how long those');
  out.push('samples took, which is the defect this tool repairs.');
  return out.join('\n');
}

// Pace and effort over time. A healthy file with a complaint attached usually means the run
// was not what the athlete remembers, so show them what it actually was.
function profile(path, segSec) {
  const { pts } = parse(path);
  const D = cumulative(pts);
  const t0 = pts[0].t, total = pts[pts.length - 1].t - t0;
  const hasHr = pts.some(p => p.hr != null);
  const out = [
    `Pace profile — ${path}`,
    '',
    hasHr ? '  segment          distance    pace    avg HR' : '  segment          distance    pace',
  ];
  for (let s0 = 0; s0 < total; s0 += segSec) {
    const s1 = Math.min(s0 + segSec, total);
    let i0 = -1, i1 = -1;
    for (let i = 0; i < pts.length; i++) {
      const rel = pts[i].t - t0;
      if (i0 < 0 && rel >= s0) i0 = i;
      if (rel <= s1) i1 = i;
    }
    if (i0 < 0 || i1 <= i0) continue;
    const d = D[i1] - D[i0], dt = pts[i1].t - pts[i0].t;
    if (d <= 0 || dt <= 0) continue;
    const hrs = pts.slice(i0, i1 + 1).map(p => p.hr).filter(x => x != null);
    const hr = hrs.length ? Math.round(hrs.reduce((x, y) => x + y, 0) / hrs.length) : null;
    const label = `${hms(s0)}-${hms(s1)}`;
    out.push(
      `  ${label.padEnd(16)} ${(d / 1609.344).toFixed(2).padStart(5)} mi` +
      `  ${pace(dt / (d / 1609.344)).padStart(6)}${hr != null ? '   ' + String(hr).padStart(5) : ''}`);
  }
  if (hasHr) {
    out.push('');
    out.push('If pace and heart rate rise and fall together the recording is internally consistent —');
    out.push('effort tracking pace is what a real run looks like, and is evidence against corruption.');
  }
  return out.join('\n');
}

// ---------- cli ----------
const argv = process.argv.slice(2);
const cmd = argv[0];
const has = name => argv.includes(`--${name}`);
const flag = (name, def) => { const i = argv.indexOf(`--${name}`); return i === -1 ? def : argv[i + 1]; };
const positional = [];
for (let i = 1; i < argv.length; i++) {
  if (argv[i].startsWith('--')) { if (argv[i] === '--window') i++; continue; }
  positional.push(argv[i]);
}

try {
  if (cmd === 'diagnose') {
    if (!positional[0]) throw new Error('diagnose requires a file path');
    const a = analyse(positional[0]);
    console.log(has('json') ? JSON.stringify(a, null, 2) : report(a));
    process.exit(a.action === 'repair' ? 1 : 0);
  } else if (cmd === 'repair') {
    if (!positional[1]) throw new Error('repair requires <in> and <out> paths');
    const { a, outPath, rewritten } = repair(positional[0], positional[1], parseFloat(flag('window', 30)), has('force'));
    console.log(report(a));
    console.log(`\nRepaired ${rewritten} timestamps -> ${outPath}`);
  } else if (cmd === 'verify') {
    if (!positional[1]) throw new Error('verify requires <original> and <repaired> paths');
    console.log(verify(positional[0], positional[1]));
  } else if (cmd === 'splits') {
    if (!positional[0]) throw new Error('splits requires a file path');
    console.log(has('km') ? splits(positional[0], 1000, 'km') : splits(positional[0], 1609.344, 'mi'));
  } else if (cmd === 'stops') {
    if (!positional[0]) throw new Error('stops requires a file path');
    console.log(stops(positional[0]));
  } else if (cmd === 'profile') {
    if (!positional[0]) throw new Error('profile requires a file path');
    console.log(profile(positional[0], parseFloat(flag('segment', 300))));
  } else {
    console.error('Usage: node tcx.mjs diagnose <file> [--json]');
    console.error('       node tcx.mjs repair <in> <out> [--window 30] [--force]');
    console.error('       node tcx.mjs verify <original> <repaired>');
    console.error('       node tcx.mjs splits <file> [--km]');
    console.error('       node tcx.mjs stops <file>');
    console.error('       node tcx.mjs profile <file> [--segment 300]');
    process.exit(64);
  }
} catch (e) { console.error(`error: ${e.message}`); process.exit(70); }
