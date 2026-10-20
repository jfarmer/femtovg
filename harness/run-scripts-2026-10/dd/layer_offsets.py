"""For a frame whose changed pixels fall outside the merged contours' boxes: rerun rvd, then find the translations
(integer, within +-W) that move those boxes onto the outside pixels - a layer's origin."""
import collections, os, subprocess, sys
import numpy as np
from PIL import Image
from common import *
by_key = {f['key']: f for f in files()}
for spec in sys.argv[1:]:
    key, framing = spec.rsplit(':', 1)
    fr, z = FRAMINGS[framing]
    r = subprocess.run([f'{BIN}/_logos_full_rvd', f'{z:g}', f'{OUT}/tmp/lo.ppm', by_key[key]['path']],
                       env={**os.environ, **fr, **SWEEP_ENV, 'SINGLE_SHADOW_LAYER': '1', 'RV_DIAG': '1'}, capture_output=True, text=True)
    boxes = []
    for line in r.stderr.splitlines():
        t = line.split()
        if t and t[0] in ('RVFILL', 'RVSTROKE'):
            i = next(j for j, s in enumerate(t) if s.startswith('bbox='))
            bb = [float(t[i].split('=')[1])] + [float(v) for v in t[i + 1:i + 4]]
            pad = 2.0 if t[0] == 'RVFILL' else 2 * float(t[2].split('=')[1]) + 2
            boxes.append((bb, pad))
    L = lambda b: np.asarray(Image.open(f'{OUT}/png_changed/{b}_{key}_{framing}.png').convert('RGB'), dtype=np.int16)
    diff = np.abs(L('rv') - L('m8')).max(axis=2) > 0
    h, w = diff.shape
    def cover(dx, dy):
        c = np.zeros_like(diff)
        for (x0, y0, x1, y1), pad in boxes:
            c0, r0 = max(int(np.floor(x0 + dx - pad)), 0), max(int(np.floor(y0 + dy - pad)), 0)
            c1, r1 = min(int(np.ceil(x1 + dx + pad)) + 1, w), min(int(np.ceil(y1 + dy + pad)) + 1, h)
            if c0 < c1 and r0 < r1:
                c[r0:r1, c0:c1] = True
        return c
    left = diff & ~cover(0, 0)
    print(f'{key} {framing}: {int(diff.sum())} changed, {int(left.sum())} outside the boxes; {len(boxes)} boxes')
    # candidate offsets: from each box corner to each outside pixel cluster's corner
    ys, xs = np.nonzero(left)
    cands = collections.Counter()
    for (x0, y0, x1, y1), pad in boxes:
        for x, y in list(zip(xs, ys))[::max(1, len(xs) // 200)]:
            if x1 - x0 < 2000:
                for dx in range(int(x - x1 - pad) - 1, int(x - x0 + pad) + 2):
                    for dy in range(int(y - y1 - pad) - 1, int(y - y0 + pad) + 2):
                        cands[(dx, dy)] += 1
    best = []
    total = left.copy()
    for (dx, dy), _ in cands.most_common(400):
        got = int((total & cover(dx, dy)).sum())
        if got:
            best.append((got, dx, dy))
    best.sort(reverse=True)
    for got, dx, dy in best[:3]:
        print(f'   offset ({dx:+d}, {dy:+d}) covers {got} of the {int(left.sum())}')
    rem = left.copy()
    for got, dx, dy in best:
        rem &= ~cover(dx, dy)
    print(f'   after every candidate offset: {int(rem.sum())} left')
