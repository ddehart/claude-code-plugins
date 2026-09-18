// Build synthetic TCX fixtures with known ground truth, so the diagnosis can be
// checked against cases where we know what the right answer is.
import { writeFileSync, mkdirSync } from 'node:fs';

const START = new Date('2026-09-10T08:00:00.000Z').getTime();
const LAT0 = 40.0230, LON0 = -83.0078;
const MPD_LAT = 111320;                                   // metres per degree latitude
const MPD_LON = 111320 * Math.cos(LAT0 * Math.PI / 180);

function tcx(points, sport = 'Running') {
  const tp = points.map(p => `                    <Trackpoint>
                        <Time>${new Date(START + p.t * 1000).toISOString().slice(0, 23)}Z</Time>
                        <Position>
                            <LatitudeDegrees>${p.lat.toFixed(12)}</LatitudeDegrees>
                            <LongitudeDegrees>${p.lon.toFixed(12)}</LongitudeDegrees>
                        </Position>
                        <AltitudeMeters>250.0</AltitudeMeters>
                        <DistanceMeters>${p.d.toFixed(6)}</DistanceMeters>
                        <HeartRateBpm>
                            <Value>${p.hr}</Value>
                        </HeartRateBpm>
                    </Trackpoint>`).join('\n');
  const dur = points[points.length - 1].t - points[0].t;
  return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2">
    <Activities>
        <Activity Sport="${sport}">
            <Id>${new Date(START).toISOString().slice(0, 23)}Z</Id>
            <Lap StartTime="${new Date(START).toISOString().slice(0, 23)}Z">
                <TotalTimeSeconds>${dur.toFixed(3)}</TotalTimeSeconds>
                <DistanceMeters>${points[points.length - 1].d.toFixed(3)}</DistanceMeters>
                <Calories>300</Calories>
                <Intensity>Active</Intensity>
                <TriggerMethod>Manual</TriggerMethod>
                <Track>
${tp}
                </Track>
            </Lap>
            <Creator xsi:type="Device_t" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <Name>Synthetic Test Device</Name>
                <UnitId>0</UnitId>
                <ProductID>0</ProductID>
            </Creator>
        </Activity>
    </Activities>
</TrainingCenterDatabase>
`;
}

// A straight-north run at a varying but always-moving pace.
// speedAt() gives real pace variation so a repair can be checked for preserving it.
const speedAt = t => 3.2 - 0.5 * Math.sin(t / 400) - 0.3 * Math.sin(t / 97);
const hrAt = t => Math.round(140 + 25 * Math.min(1, t / 1200) + 4 * Math.sin(t / 60));

function walk(durationSec, { pauses = [] } = {}) {
  const pts = [];
  let d = 0;
  for (let t = 0; t <= durationSec; t++) {
    const inPause = pauses.some(p => t > p.at && t <= p.at + p.len);
    if (!inPause) d += speedAt(t);
    pts.push({ t, d, lat: LAT0 + d / MPD_LAT, lon: LON0, hr: inPause ? 110 : hrAt(t) });
  }
  return pts;
}

mkdirSync(new URL('.', import.meta.url), { recursive: true });
const here = new URL('.', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');

// 1. HEALTHY — uniform 1 Hz sampling, no stops. Expect: timing-healthy / no-repair.
writeFileSync(here + 'healthy.tcx', tcx(walk(1800)));

// 2. REAL PAUSES — same run with two genuine 90 s stops (position and distance
//    frozen, heart rate drops). Expect: real-pauses / no-repair. Repairing this
//    would delete 3 minutes of legitimate standing-still time.
writeFileSync(here + 'real_pauses.tcx', tcx(walk(1800, { pauses: [{ at: 400, len: 90 }, { at: 1100, len: 90 }] })));

// 3. DECOUPLED — the Pixel Watch 4 defect: correct positions, correct total
//    elapsed, but per-sample timestamps scrambled so interval length no longer
//    tracks ground covered. Built by dropping ~20% of samples and redistributing
//    their time onto neighbours. Expect: timestamps-decoupled / repair.
{
  const clean = walk(1800);
  const kept = clean.filter((_, i) => i % 5 !== 3);           // drop every 5th sample
  const total = clean[clean.length - 1].t - clean[0].t;
  // Assign each kept point a timestamp that ignores how far it actually travelled.
  let acc = 0;
  const jittered = kept.map((p, i) => {
    const slice = (i % 7 === 0) ? 4.5 : (i % 3 === 0) ? 0.35 : 1.0;  // arbitrary, distance-blind
    const out = { ...p, t: acc };
    acc += slice;
    return out;
  });
  const scale = total / acc;
  jittered.forEach(p => { p.t = Math.round(p.t * scale * 1000) / 1000; });
  writeFileSync(here + 'decoupled.tcx', tcx(jittered));
}

// 4. DECOUPLED + REAL PAUSES — the hard case: a city run with genuine stoplight
//    stops AND the timestamp defect. Repair must de-jitter the moving segments
//    while leaving the 2x60 s stops exactly as recorded.
{
  const clean = walk(1800, { pauses: [{ at: 500, len: 60 }, { at: 1200, len: 60 }] });
  const kept = clean.filter((_, i) => i % 5 !== 3);
  const total = clean[clean.length - 1].t - clean[0].t;
  let acc = 0;
  const out = kept.map((p, i) => {
    const moving = i > 0 && p.d !== kept[i - 1].d;
    // Moving samples get distance-blind jitter; paused samples keep honest 1 s ticks.
    const slice = !moving ? 1.0 : (i % 7 === 0) ? 4.5 : (i % 3 === 0) ? 0.35 : 1.0;
    const q = { ...p, t: acc };
    acc += slice;
    return q;
  });
  const scale = total / acc;
  out.forEach(p => { p.t = Math.round(p.t * scale * 1000) / 1000; });
  writeFileSync(here + 'decoupled_with_pauses.tcx', tcx(out));
}

// 5. DECOUPLED + NOISY REAL PAUSES — the same city run, but with the GPS wander a real watch
//    shows while its owner stands still. This is the case the four fixtures above cannot catch:
//    with perfectly static positions a stop is trivial to spot, so a detector that leans on
//    sample-to-sample stillness passes every fixture here and still deletes genuine stopped time
//    on any real recording. Stationary noise is most of the difference between a synthetic file
//    and one a watch produced, and it is exactly where stop detection earns its keep.
{
  const clean = walk(1800, { pauses: [{ at: 500, len: 60 }, { at: 1200, len: 60 }] });
  const kept = clean.filter((_, i) => i % 5 !== 3);
  const total = clean[clean.length - 1].t - clean[0].t;
  let acc = 0, creep = 0;
  const out = kept.map((p, i) => {
    const moving = i > 0 && p.d !== kept[i - 1].d;
    const slice = !moving ? 1.0 : (i % 7 === 0) ? 4.5 : (i % 3 === 0) ? 0.35 : 1.0;
    const q = { ...p, t: acc };
    if (!moving) {
      // ±2 m of positional wander while stationary — ordinary consumer-GPS behaviour. The
      // positions oscillate rather than walk away, so net displacement stays near zero.
      q.lat = p.lat + (Math.sin(i * 1.7) * 2) / 111320;
      // And the watch's own distance channel books that wander as distance travelled, which is
      // what makes the stop invisible to anything measuring ground covered instead of position:
      // a 60 s stop accumulates ~60 m of "movement" without going anywhere.
      creep += 1;
    }
    q.d = p.d + creep;
    acc += slice;
    return q;
  });
  const scale = total / acc;
  out.forEach(p => { p.t = Math.round(p.t * scale * 1000) / 1000; });
  writeFileSync(here + 'decoupled_with_noisy_pauses.tcx', tcx(out));
}

console.log('fixtures written to', here);
