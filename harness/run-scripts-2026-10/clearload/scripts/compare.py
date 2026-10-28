#!/usr/bin/env python3
"""compare.py DEV PREFIX (r2, m) : #368 head (pp) against the clear-on-load fold (pc) on one device, from the
frames-*.jsonl of an ABBA round (frames.py) and the soak CSVs. Steady frames only (rep >= 1: rep 0 pays for
pipelines the previous file's frame evicted). For each frame (phase, file, zoom, rep) it takes each variant's
median over its passes in both recordings, then per phase reports the median frame's value for each variant,
the median of the per-frame differences (fold - head) and the sum over the phase's frames."""
import csv, glob, json, os, statistics as st, sys
from collections import defaultdict

dev = sys.argv[1]
prefix = sys.argv[2]
d = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/{dev}'
metrics = ['gpu_ms', 'frag_ms', 'read_mb', 'write_mb', 'partial']
vals = defaultdict(lambda: defaultdict(list))  # (phase, file, zoom, rep) -> variant:metric -> values
for path in sorted(glob.glob(f'{d}/frames-{prefix}-*.jsonl')):
    variant = path.rsplit('-', 1)[1].split('.')[0]
    for line in open(path):
        r = json.loads(line)
        if r['rep'] < 1:
            continue
        key = (r['phase'], r['file'], r['zoom'], r['rep'])
        for m in metrics:
            if r.get(m) is not None:
                vals[key][f'{variant}:{m}'].append(r[m])
for path in sorted(glob.glob(f'{d}/soak-{prefix}-*.csv')):
    variant = path.rsplit('-', 1)[1].split('.')[0]
    for r in csv.DictReader(open(path)):
        if int(r['rep']) < 1:
            continue
        key = (r['phase'], r['file'], f"z{r['zoom']}" if not r['zoom'].startswith('z') else r['zoom'], int(r['rep']))
        key = (key[0], key[1], 'z' + str(float(r['zoom'])).rstrip('0').rstrip('.'), key[3])
        vals[key][f'{variant}:wall_ms'].append(float(r['wall_ms']))
        vals[key][f'{variant}:encode_ms'].append(float(r['encode_ms']))
        # Submit, GPU execution and completion: the soak waits for the GPU after encoding.
        vals[key][f'{variant}:post_ms'].append(float(r['wall_ms']) - float(r['encode_ms']))

# Frame keys from the signposts carry the zoom as the app formats it (z1, z2, z4); normalise both sides.
merged = defaultdict(lambda: defaultdict(list))
for (phase, name, zoom, rep), per in vals.items():
    z = zoom.lstrip('z')
    z = str(float(z)).rstrip('0').rstrip('.')
    for k, v in per.items():
        merged[(phase, name, z, rep)][k].extend(v)

phases = sorted({k[0] for k in merged}, key=['curve', 'curvehd', 'busey', 'buseyhd', 'empty', 'emptyhd'].index)
for phase in phases:
    keys = [k for k in merged if k[0] == phase]
    print(f'== {dev} {phase}: {len(keys)} steady frames')
    for m in metrics + ['wall_ms', 'encode_ms', 'post_ms']:
        a, b, diff = [], [], []
        for k in keys:
            pa, pb = merged[k].get(f'pp:{m}'), merged[k].get(f'pc:{m}')
            if not pa or not pb:
                continue
            ma, mb = st.median(pa), st.median(pb)
            a.append(ma); b.append(mb); diff.append(mb - ma)
        if not diff:
            continue
        rel = (sum(b) - sum(a)) / sum(a) * 100 if sum(a) else float('nan')
        print(f'  {m:9s} head {st.median(a):9.3f}  fold {st.median(b):9.3f}  median diff {st.median(diff):+9.3f}'
              f'  sum {sum(a):10.1f} -> {sum(b):10.1f} ({rel:+.1f} %)  frames lower {sum(x < 0 for x in diff)}/{len(diff)}')
