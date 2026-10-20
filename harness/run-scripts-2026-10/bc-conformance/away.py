#!/usr/bin/env python3
"""away.py BEFORE AFTER [n=N] [frames=KEY:FRAMING,...]: the frames AFTER moves away from the area reference on (share of
pixels beyond 20/255), worst first, and what the pixels that got worse are:
  worse    AFTER beyond 20/255 of the area there and farther from it than BEFORE by more than 2/255
  shared   of those, every browser with a reference (chg, chr, wk, ff) within 12/255 of AFTER: conflation at one sample
  over     of those, AFTER darker (more ink on a light ground) than the area: coverage past the true edge
  under    AFTER lighter than the area
  centre   the centre of mass of the worse pixels, for sheet.py at=
Frames are read as ab_refs.py leaves them; writes away_BEFORE_AFTER.jsonl next to this script."""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import OUT, REFS, files

before, after = sys.argv[1:3]
opts = dict(a.split('=', 1) for a in sys.argv[3:])
fs = {f['key']: f['group'] for f in files()}
rec = {}
for line in open(f'{OUT}/accuracy.jsonl'):
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r['build'] in (before, after):
        rec[(r['build'], r['key'], r['framing'])] = r.get('hash')


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None


def frame(b, key, framing):
    for d in ('png_wpt', 'png_nyt', 'png', 'png_changed'):
        a = load(f'{OUT}/{d}/{b}_{key}_{framing}.png')
        if a is not None:
            return a
    return None


lum = lambda im: im @ np.array([0.2126, 0.7152, 0.0722])
if 'frames' in opts:
    todo = [tuple(x.rsplit(':', 1)) for x in opts['frames'].split(',')]
else:
    todo = sorted((k, f) for (b, k, f), h in rec.items() if b == before and rec.get((after, k, f)) not in (None, h))
rows = []
for key, framing in todo:
    idr = load(f'{REFS}/id_{key}_{framing}.png')
    if idr is None:
        continue
    b, a = frame(before, key, framing), frame(after, key, framing)
    if b is None or a is None or b.shape != idr.shape or a.shape != idr.shape:
        continue
    db, da = np.abs(b - idr).max(axis=2), np.abs(a - idr).max(axis=2)
    size = idr.shape[0] * idr.shape[1]
    delta = 100 * ((da > 20).sum() - (db > 20).sum()) / size
    worse = (da > 20) & (da > db + 2)
    near_all = np.ones(worse.shape, bool)
    browsers = []
    for br in ('chg', 'chr', 'wk', 'ff'):
        im = load(f'{REFS}/{br}_{key}_{framing}.png')
        if im is not None and im.shape == idr.shape:
            near_all &= np.abs(a - im).max(axis=2) <= 12
            browsers.append(br)
    over = worse & (lum(a) < lum(idr))
    ys, xs = np.nonzero(worse)
    rows.append({'key': key, 'framing': framing, 'group': fs[key], 'delta': round(delta, 4),
                 'before': round(100 * (db > 20).sum() / size, 3), 'after': round(100 * (da > 20).sum() / size, 3),
                 'px_before': int((db > 20).sum()), 'px_after': int((da > 20).sum()),
                 'worse': int(worse.sum()), 'shared': int((worse & near_all).sum()), 'over': int(over.sum()),
                 'under': int((worse & ~over).sum()), 'browsers': browsers,
                 'centre': [int(xs.mean()), int(ys.mean())] if len(xs) else None,
                 'max_worse_at': (lambda i: [int(xs[i]), int(ys[i])])(int(np.argmax(da[worse] - db[worse]))) if len(xs) else None})
rows.sort(key=lambda r: -r['delta'])
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'away_{before}_{after}.jsonl'), 'w') as out:
    for r in rows:
        out.write(json.dumps(r, ensure_ascii=False) + '\n')
n = int(opts.get('n', 40))
away = [r for r in rows if r['delta'] > 0.005]
print(f'{before} -> {after}: {len(rows)} changed frames with the area reference; away by more than 0.005 points: {len(away)}, '
      f'by more than 0.1: {sum(r["delta"] > 0.1 for r in rows)}; toward by more than 0.1: {sum(r["delta"] < -0.1 for r in rows)}')
print('| frame | framing | group | % beyond 20 before -> after | worse px | shared with all browsers | over-inked | under | centre |')
print('|---|---|---|---|---:|---:|---:|---:|---|')
for r in away[:n]:
    print(f"| {r['key'].split('__')[-1]} | {r['framing']} | {r['group']} | {r['before']:.3f} -> {r['after']:.3f} ({r['delta']:+.3f}) | "
          f"{r['worse']} | {r['shared']} | {r['over']} | {r['under']} | {r['centre']} |")
