#!/usr/bin/env python3
"""gpu_table.py DIR TAG... : the moving frames (rep >= 1) of frames.py's per-frame GPU records, per variant (the tag's
last part) and file: median GPU time and fragment time, median read + write bandwidth a frame, and the partial
renders summed. Runs of one variant are pooled."""
import collections, json, statistics as st, sys

d = sys.argv[1]
rows = collections.defaultdict(lambda: collections.defaultdict(list))
for tag in sys.argv[2:]:
    variant = tag.rsplit('-', 1)[1]
    for line in open(f'{d}/frames-{tag}.jsonl'):
        r = json.loads(line)
        if r['rep'] >= 1:
            rows[(r['phase'], r['file'])][variant].append(r)
total = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0])
for (phase, name), by in sorted(rows.items()):
    line = f'{phase:6s} {name[2:]:10s}'
    for v in sorted(by):
        fr = by[v]
        gpu, frag = st.median(r['gpu_ms'] for r in fr), st.median(r['frag_ms'] for r in fr)
        # A GPU whose counter set has no bandwidth or partial renders (the A18 Pro's default) leaves them out.
        mb = st.median(r.get('read_mb', 0) + r.get('write_mb', 0) for r in fr)
        partial = sum(r.get('partial', 0) for r in fr)
        t = total[v]; t[0] += gpu; t[1] += frag; t[2] += mb; t[3] += partial
        line += f' | {v:4s} gpu {gpu:6.3f} ms frag {frag:6.3f} ms {mb:6.2f} MB partial {partial:4.0f} ({len(fr)} frames)'
    print(line)
for v, (gpu, frag, mb, partial) in sorted(total.items()):
    print(f'{v}: sum of medians gpu {gpu:.2f} ms, fragment {frag:.2f} ms, bandwidth {mb:.1f} MB; partial renders {partial:.0f}')
