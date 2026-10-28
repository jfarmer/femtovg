#!/usr/bin/env python3
"""analyze.py [near=24]: from zoomcmp_zm_svg.jsonl - files near-perfect at 1x against the fresh references (best
browser's pixels beyond 8/255 <= NEAR), and the ladder steps where the best browser available at that zoom is
further off than NEAR. Prints per-zoom fail counts, the failing files with their worst step, and writes fails.json."""
import collections, json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
opts = dict(a.split('=', 1) for a in sys.argv[1:])
NEAR = int(opts.get('near', 24))
rows = [json.loads(l) for l in open(f'{R}/zoomcmp_zm_svg.jsonl')]
def best(step):
    v = [(step[b]['n8'], b) for b in ('chr', 'ff', 'wk') if b in step]
    return min(v) if v else None
stats = collections.Counter(); per_zoom = collections.Counter(); fails = []
for r in rows:
    s0 = best(r['steps'][0])
    if s0 is None:
        stats['no 1x ref'] += 1; continue
    if s0[0] > NEAR:
        stats['not near with fresh refs'] += 1; continue
    stats['near'] += 1
    bad = []
    for i, s in enumerate(r['steps']):
        b = best(s)
        if b is None:
            stats['steps without refs'] += 1; continue
        if b[0] > NEAR:
            bad.append((i, s['zoom'], b[0], b[1], s.get('chr', {}).get('n8'), s.get('ff', {}).get('n8'), s.get('wk', {}).get('n8'), s.get('chr_ff', {}).get('n8')))
    if bad:
        stats['fail'] += 1
        for z in sorted(set(x[1] for x in bad)): per_zoom[z] += 1
        fails.append({'key': r['key'], 'group': r['group'], 'z1': s0, 'bad': bad})
    else:
        stats['pass'] += 1
print(dict(stats)); print('files failing per zoom', sorted(per_zoom.items()))
print('fails by group', collections.Counter(f['key'].split('__')[0] + '/' + f['group'] for f in fails).most_common())
for f in sorted(fails, key=lambda f: -max(b[2] for b in f['bad']))[:int(opts.get('show', 40))]:
    w = max(f['bad'], key=lambda b: b[2])
    print(f"{f['key'][:75]:75s} 1x {f['z1']} steps {len(f['bad'])} worst z{w[1]:g} n8 {w[2]} ({w[3]}) chr/ff/wk {w[4]}/{w[5]}/{w[6]} chr-ff {w[7]}")
json.dump(fails, open(f'{R}/fails.json', 'w'), indent=0)
