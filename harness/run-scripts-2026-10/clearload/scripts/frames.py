#!/usr/bin/env python3
"""frames.py DIR TAG... : per-frame GPU metrics of run_mst.sh recordings. For each frame signpost
(co.rbckr.femtovgpmu "frames", label phase/file/zZOOM/rREP) it takes the GPU intervals that start inside the
frame's window (the soak waits for the GPU before ending it) and, when the recording has Metal GPU Counters,
the counter samples inside it, and writes DIR/frames-TAG.jsonl with:
  gpu_ms   union of every channel's intervals (vertex, fragment, compute)
  frag_ms  union of the fragment intervals
  span_ms  first interval start to last interval end
  read_mb / write_mb  GPU Read / Write Bandwidth (GB/s) integrated over the window
  partial  Partial Renders Count summed over the window
Times in the export are nanoseconds since the trace start."""
import gzip, json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xtable import rows

# Counter ids differ between GPUs (25/26/29 on the A14, 13/14/17 on the A13): taken by name from the
# recording's gpu-counter-info table.
NAMES = {'GPU Read Bandwidth': 'read', 'GPU Write Bandwidth': 'write', 'Partial Renders Count': 'partial'}


def table(path):
    if not os.path.exists(path):
        return []
    with tempfile.NamedTemporaryFile(suffix='.xml') as t:
        t.write(gzip.open(path).read())
        t.flush()
        return rows(t.name)


def union(intervals):
    total, end = 0, None
    for s, e in sorted(intervals):
        if end is None or s > end:
            total += e - s
            end = e
        elif e > end:
            total += e - end
            end = e
    return total


def frames(directory, tag):
    sp = table(f'{directory}/os-signpost-{tag}.xml.gz')
    begins, windows = {}, []
    for r in sp:
        if r[9][0] != 'co.rbckr.femtovgpmu' or r[6][0] != 'frames':
            continue
        t, kind, ident, label = int(r[0][1]), r[3][0], r[5][0], r[11][0]
        if kind == 'Begin':
            begins[ident] = (t, label)
        elif kind == 'End' and ident in begins:
            b, label = begins.pop(ident)
            windows.append((b, t, label))
    # The export holds the signpost table once per instrument that records it.
    windows = sorted(set(windows))
    gi = table(f'{directory}/metal-gpu-intervals-{tag}.xml.gz')
    intervals = sorted((int(r[0][1]), int(r[0][1]) + int(r[1][1]), r[2][0]) for r in gi)
    ids = {NAMES[r[2][0]]: int(r[1][1]) for r in table(f'{directory}/gpu-counter-info-{tag}.xml.gz')
           if r[2][0] in NAMES}
    READ, WRITE, PARTIAL = ids.get('read'), ids.get('write'), ids.get('partial')
    counters = {}
    for r in table(f'{directory}/gpu-counter-value-{tag}.xml.gz'):
        counters.setdefault(int(r[1][1]), []).append((int(r[0][1]), float(r[2][1])))
    for samples in counters.values():
        samples.sort()
    # A sample's value is the rate over the interval since the previous sample; a gap longer than a few
    # intervals is idle time, which counts as one interval.
    step = None
    if READ in counters and len(counters[READ]) > 2:
        gaps = sorted(b[0] - a[0] for a, b in zip(counters[READ], counters[READ][1:]))
        step = gaps[len(gaps) // 2]

    def integrate(cid, b, e):
        total = 0.0
        samples = counters.get(cid, [])
        prev = None
        for t, v in samples:
            if t > e:
                break
            if t >= b:
                dt = min(t - prev, 2 * step) if prev is not None else step
                total += v * dt  # GB/s x ns = bytes
            prev = t
        return total

    # The GPU instrument's stream can stop seconds before the app exits (the A13's r2-4-pp lost its last 45
    # frames): a frame past the end of the GPU data is missing, not idle.
    gpu_end = max((t for _, t, _ in intervals), default=0)
    out = []
    j = 0
    for b, e, label in windows:
        while j < len(intervals) and intervals[j][0] < b:
            j += 1
        inside = []
        k = j
        while k < len(intervals) and intervals[k][0] <= e:
            inside.append(intervals[k])
            k += 1
        phase, name, zoom, rep = label.split('/')
        row = {
            'tag': tag, 'phase': phase, 'file': name, 'zoom': zoom, 'rep': int(rep[1:]),
            'window_ms': (e - b) / 1e6,
            'gpu_ms': union([(s, t) for s, t, _ in inside]) / 1e6,
            'frag_ms': union([(s, t) for s, t, c in inside if c == 'Fragment']) / 1e6,
            'span_ms': (max(t for _, t, _ in inside) - min(s for s, _, _ in inside)) / 1e6 if inside else 0.0,
            'intervals': len(inside),
        }
        # Dropped data: a frame past the stream's end, or a long frame with next to no GPU time. A steady
        # frame of this corpus never does that (0 of 4,224 in the clean legs); the A13's r2-4-pp lost 32.
        if e > gpu_end or (row['window_ms'] > 20 and row['gpu_ms'] < 0.02 * row['window_ms']):
            for k in ('gpu_ms', 'frag_ms', 'span_ms'):
                row[k] = None
            row['dropped'] = True
            out.append(row)
            continue
        if step:
            row['read_mb'] = integrate(READ, b, e) / 1e6
            row['write_mb'] = integrate(WRITE, b, e) / 1e6
            row['partial'] = sum(v for t, v in counters.get(PARTIAL, []) if b <= t <= e)
        out.append(row)
    return out


if __name__ == '__main__':
    directory = sys.argv[1]
    for tag in sys.argv[2:]:
        rows_ = frames(directory, tag)
        with open(f'{directory}/frames-{tag}.jsonl', 'w') as f:
            for r in rows_:
                f.write(json.dumps(r) + '\n')
        print(tag, len(rows_), 'frames')
