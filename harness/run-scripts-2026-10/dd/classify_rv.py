#!/usr/bin/env python3
"""classify_rv.py BEFORE AFTER [workers=4]  (run through tool.py)

For every frame the two builds differ on: the diagnostic build rvd (path-dedupe + RV_DIAG logging) lists each merge
(position; corner or curve-interior point; onto a corner or interior point; exact or within the tolerance) and each
contour that had one, filled (and whether it now takes the convex path) or stroked (width, join). Then each changed
pixel is checked against those contours' boxes, dilated by 2 px for a fill and by twice the width plus 2 px for a stroke
(a mitre reaches miter_limit * w / 2, 4 * w / 2 by default). Writes classify.jsonl."""
import collections, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
from common import *

before, after = sys.argv[1:3]
opts = dict(a.split('=', 1) for a in sys.argv[3:])
by_key = {f['key']: f for f in files()}
rec = {}
for line in open(f'{OUT}/accuracy.jsonl'):
    r = json.loads(line)
    if r['build'] in (before, after):
        rec[(r['build'], r['key'], r['framing'])] = r.get('hash')
changed = sorted((k, f) for (b, k, f), h in rec.items() if b == before and rec.get((after, k, f)) not in (None, h))
done = set()
outp = f'{OUT}/classify.jsonl'
if os.path.exists(outp):
    for line in open(outp):
        r = json.loads(line)
        done.add((r['key'], r['framing']))
out = open(outp, 'a')


def load(build, key, framing):
    return np.asarray(Image.open(f'{OUT}/png_changed/{build}_{key}_{framing}.png').convert('RGB'), dtype=np.int16)


def job(x):
    key, framing = x
    fr, z = FRAMINGS[framing]
    ppm = f'{OUT}/tmp/cls_{os.getpid()}_{abs(hash(x))}.ppm'
    r = subprocess.run([f'{BIN}/_logos_full_rvd', f'{z:g}', ppm, by_key[key]['path']],
                       env={**os.environ, **fr, **SWEEP_ENV, 'SINGLE_SHADOW_LAYER': '1', 'RV_DIAG': '1'},
                       capture_output=True, text=True, timeout=600)
    same = None
    if os.path.exists(ppm):
        a = load(after, key, framing)
        d = np.asarray(Image.open(ppm).convert('RGB'), dtype=np.int16)
        same = bool(d.shape == a.shape and (d == a).all())
        os.remove(ppm)
    merges = collections.Counter()
    boxes, fills, strokes = [], collections.Counter(), collections.Counter()
    for line in r.stderr.splitlines():
        t = line.split()
        if not t:
            continue
        if t[0] == 'RVMERGE':
            merges[' '.join(t[3:6])] += 1
        elif t[0] == 'RVFILL':
            kv = dict(s.split('=') for s in t[1:5])
            bb = [float(v) for v in [t[5].split('=')[1]] + t[6:9]]
            fills['convex' if kv['convex'] == 'true' else 'concave'] += 1
            boxes.append((bb, 2.0))
        elif t[0] == 'RVSTROKE':
            kv = dict(s.split('=') for s in t[1:6])
            bb = [float(v) for v in [t[6].split('=')[1]] + t[7:10]]
            strokes[kv['join'] + (' closed' if kv['closed'] == 'true' else ' open')] += 1
            boxes.append((bb, 2 * float(kv['width']) + 2))
    b, a = load(before, key, framing), load(after, key, framing)
    dm = np.abs(a - b).max(axis=2)
    diff = dm > 0
    cover = np.zeros_like(diff)
    h, w = diff.shape
    for (x0, y0, x1, y1), pad in boxes:
        c0, r0 = max(int(np.floor(x0 - pad)), 0), max(int(np.floor(y0 - pad)), 0)
        c1, r1 = min(int(np.ceil(x1 + pad)) + 1, w), min(int(np.ceil(y1 + pad)) + 1, h)
        if c0 < c1 and r0 < r1:
            cover[r0:r1, c0:c1] = True
    n = int(diff.sum())
    row = {'key': key, 'framing': framing, 'group': by_key[key]['group'], 'diff_px': n, 'max': int(dm.max()),
           'over20': int((dm > 20).sum()), 'explained': int((diff & cover).sum()), 'merges': dict(merges),
           'fills': dict(fills), 'strokes': dict(strokes), 'rvd_equals_after': same,
           'layers': int(m.group(1)) if (m := re.search(r'layers begun: (\d+)', r.stderr)) else None}
    return row


todo = [x for x in changed if x not in done]
print(f'{len(changed)} changed frames, {len(todo)} to classify', flush=True)
with ThreadPoolExecutor(int(opts.get('workers', 4))) as ex:
    for row in ex.map(job, todo):
        out.write(json.dumps(row) + '\n')
        out.flush()
print('done', flush=True)
