#!/usr/bin/env python3
"""area_changed.py BEFORE AFTER: area_ab.py's comparison, over only the frames identity.py found to differ between the
two builds (tmp/identity_BEFORE_AFTER.jsonl) that have an area reference: pixels beyond 20/255 of the area, the
browsers' on the same frames, frames nearer and further, by group and by framing."""
import collections, json, os, subprocess, sys
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import *
R = OUT
before, after = sys.argv[1:3]
fs = {f['key']: f for f in files()}
rows = [json.loads(l) for l in open(f'{R}/tmp/identity_{before}_{after}.jsonl')]
changed = [(r['key'], r['framing']) for r in rows if not r.get('same') and not r.get('error')]
def frame(b, key, framing):
    binary, extra = BUILDS[b]; fr, z = FRAMINGS[framing]
    p = f'{R}/png_changed/{b}_{key}_{framing}.png'
    if not os.path.exists(p):
        ppm = p[:-4] + '.ppm'
        subprocess.run([binary, f'{z:g}', ppm, fs[key]['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra}, capture_output=True)
        if not os.path.exists(ppm): return None
        Image.open(ppm).save(p); os.remove(ppm)
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def ref(b, key, framing):
    p = f'{R}/refs/{b}_{key}_{framing}.png'
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None
def one(kf):
    key, framing = kf
    idr = ref('id', key, framing)
    if idr is None: return None
    a, b = frame(before, key, framing), frame(after, key, framing)
    if a is None or b is None: return None
    h, w = idr.shape[:2]
    d = lambda im: np.abs(im[:h, :w] - idr).max(axis=2)
    out = {'key': key, 'framing': framing, 'group': fs[key]['group'], 'a20': int((d(a) > 20).sum()), 'b20': int((d(b) > 20).sum())}
    for br in ('wk', 'chg', 'chr', 'ff'):
        im = ref(br, key, framing)
        if im is not None: out[br + '20'] = int((d(im) > 20).sum())
    return out
os.makedirs(f'{R}/png_changed', exist_ok=True)
with ThreadPoolExecutor(6) as ex:
    res = [r for r in ex.map(one, changed) if r]
json.dump(res, open(f'{R}/tmp/area_changed_{before}_{after}.json', 'w'))
s = lambda sel, k: sum(r.get(k, 0) for r in sel)
print(f'{len(changed)} frames differ; {len(res)} have an area reference')
for label, sel in (('all', res), ('1x and up', [r for r in res if r['framing'] in ('z1', 'z2', 'z4', 'zt2', 'zt4', 'hd')]),
                   ('below 1x', [r for r in res if r['framing'] in ('z01', 'z025', 'z05')])):
    near = sum(r['b20'] < r['a20'] for r in sel); far = sum(r['b20'] > r['a20'] for r in sel)
    print(f'  {label}: {len(sel)} frames, beyond 20/255 {s(sel, "a20")} -> {s(sel, "b20")} px; nearer {near}, further {far} | '
          f'WebKit {s(sel, "wk20")}, GPU Chromium {s(sel, "chg20")}, software Chromium {s(sel, "chr20")}, Firefox {s(sel, "ff20")}')
g = collections.defaultdict(lambda: [0, 0, 0])
for r in res:
    x = g[r['group']]; x[0] += r['a20']; x[1] += r['b20']; x[2] += 1
for name, (a, b, n) in sorted(g.items(), key=lambda kv: kv[1][1] - kv[1][0]):
    print(f'    {name}: {n} frames, {a} -> {b} px')
worst = sorted(res, key=lambda r: r['b20'] - r['a20'])
print('  most improved:', [(r['key'].split('__')[-1][:40], r['framing'], r['a20'], r['b20']) for r in worst[:8]])
print('  most worsened:', [(r['key'].split('__')[-1][:40], r['framing'], r['a20'], r['b20']) for r in worst[-8:]])
