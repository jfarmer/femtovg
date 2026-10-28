#!/usr/bin/env python3
"""corpus.py [BEFORE AFTER [OUT.json]]: every file of $CORPUS_RUN_OUT/files.json at z1, z2 and hd, rendered by both builds
(render.py): frames that change, and per changed frame the pixels more than 20/255 off Chromium (chr), off the area
reference (id), and off all three browsers (chr, ff, wk) where all three references exist, before and after. A
frame moves toward a reference when its count drops. Writes OUT.json (default corpus.json)."""
import json, os, sys
import numpy as np
from PIL import Image
OUT = os.environ['CORPUS_RUN_OUT']; HERE = os.path.dirname(os.path.abspath(__file__))
B, A = (sys.argv[1:3] if len(sys.argv) > 2 else ('mstc', 'caps'))
L = lambda p: np.asarray(Image.open(p).convert('RGB'), np.int16)
fs = json.load(open(f'{OUT}/files.json'))
rows = []
for f in fs:
    if f['key'].startswith('red__'): continue  # the reductions here, measured by measure.py
    for fr in ('z1', 'z2', 'hd'):
        pb, pa = f'{OUT}/png/{B}_{f["key"]}_{fr}.png', f'{OUT}/png/{A}_{f["key"]}_{fr}.png'
        if not (os.path.exists(pb) and os.path.exists(pa)): rows.append({'key': f['key'], 'fr': fr, 'missing': True}); continue
        b, a = L(pb), L(pa)
        changed = int((np.abs(a - b).max(2) > 0).sum())
        row = {'key': f['key'], 'group': f['group'], 'fr': fr, 'round': f.get('round', True), 'changed_px': changed}
        refs = {k: L(f'{OUT}/refs/{k}_{f["key"]}_{fr}.png') for k in ('chr', 'ff', 'wk', 'id') if os.path.exists(f'{OUT}/refs/{k}_{f["key"]}_{fr}.png')}
        h = min([b.shape[0]] + [r.shape[0] for r in refs.values()]); w = min([b.shape[1]] + [r.shape[1] for r in refs.values()])
        off = lambda im, r: np.abs(im[:h, :w] - r[:h, :w]).max(2) > 20
        for k in ('chr', 'id'):
            if k in refs: row[k] = [int(off(b, refs[k]).sum()), int(off(a, refs[k]).sum())]
        if all(k in refs for k in ('chr', 'ff', 'wk')):
            row['all3'] = [int((off(b, refs['chr']) & off(b, refs['ff']) & off(b, refs['wk'])).sum()),
                           int((off(a, refs['chr']) & off(a, refs['ff']) & off(a, refs['wk'])).sum())]
        rows.append(row)
json.dump(rows, open(f'{HERE}/' + (sys.argv[3] if len(sys.argv) > 3 else 'corpus.json'), 'w'), indent=0)
miss = [r for r in rows if r.get('missing')]
done = [r for r in rows if not r.get('missing')]
ch = [r for r in done if r['changed_px']]
print(f'{len(done)} frames ({len(miss)} missing), {len(ch)} change')
for g in sorted({r['group'] for r in done}):
    d = [r for r in done if r['group'] == g]; c = [r for r in d if r['changed_px']]
    print(f'  {g}: {len(d)} frames, {len(c)} change')
for k in ('chr', 'id', 'all3'):
    for fr in ('z1', 'z2', 'hd', None):
        c = [r for r in ch if k in r and (fr is None or r['fr'] == fr)]
        tw = sum(r[k][1] < r[k][0] for r in c); aw = sum(r[k][1] > r[k][0] for r in c); eq = len(c) - tw - aw
        sb = sum(r[k][0] for r in c); sa = sum(r[k][1] for r in c)
        print(f'{k:5} {fr or "all":4}: {len(c):3} changed frames: {tw} toward, {aw} away, {eq} same count; px {sb} -> {sa}')
print('\nframes moving away (chr, id or all3):')
for r in ch:
    if any(k in r and r[k][1] > r[k][0] for k in ('chr', 'id', 'all3')):
        print(' ', r['key'], r['fr'], 'changed', r['changed_px'], {k: r[k] for k in ('chr', 'id', 'all3') if k in r})
