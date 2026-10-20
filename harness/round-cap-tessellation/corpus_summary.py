#!/usr/bin/env python3
"""corpus_summary.py [corpus.json]: corpus.py's rows split into BuseyBench and the other files, per framing."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in json.load(open(f'{HERE}/' + (sys.argv[1] if len(sys.argv) > 1 else 'corpus.json'))) if not r.get('missing')]
for name, sel in (('BuseyBench', lambda r: r['group'] == 'buseybench'), ('other files', lambda r: r['group'] != 'buseybench')):
    d = [r for r in rows if sel(r)]; ch = [r for r in d if r['changed_px']]
    print(f'{name}: {len(d)} frames, {len(ch)} change')
    for k in ('chr', 'id', 'all3'):
        cells = []
        for fr in ('z1', 'z2', 'hd'):
            c = [r for r in ch if k in r and r['fr'] == fr]
            tw = sum(r[k][1] < r[k][0] for r in c); aw = sum(r[k][1] > r[k][0] for r in c)
            cells.append(f'{fr} {tw}/{aw} ({sum(r[k][0] for r in c)} -> {sum(r[k][1] for r in c)} px)')
        print(f'  {k:4} toward/away: ' + ', '.join(cells))
