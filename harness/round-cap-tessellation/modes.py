#!/usr/bin/env python3
"""modes.py: every mode of experiment-modes.patch (binary capx, FEMTOVG_CAP_MODE=m, build tag capx<m>) on the
reductions and the corpus files: px more than 20/255 off the exact coverage in the cap and join windows (measure.py)
at z1 / z2 / hd, and corpus frames toward / away from Chromium, the area reference and all three browsers
(corpus.py). Checks that capx0 renders as master (mstc) and capx8 as the prototype (caps), frame for frame."""
import json, os, subprocess, sys
import numpy as np
from PIL import Image
OUT = os.environ['CORPUS_RUN_OUT']; HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {0: 'master', 1: 'chords from the rim radius at tess_tol, +1 point', 2: 'chords from the half width at tess_tol, +1 point',
         3: 'chords from the rim radius at tess_tol / 2, +1 point (the count alone)', 4: 'mode 1, inner points pushed out so the chords straddle the arc',
         5: 'mode 3 with the straddle', 6: 'mode 3, inner points at an approximate equal-ink radius (a ramp a fringe wide assumed)',
         7: 'mode 6 with the straddle', 8: 'mode 3, inner points fitted to the exact area (the prototype)', 9: 'mode 8 at tess_tol'}
fs = json.load(open(f'{OUT}/files.json'))
L = lambda p: np.asarray(Image.open(p).convert('RGB'), np.int16)
for a, b in (('capx0', 'mstc'), ('capx8', 'caps')):
    diff = sum(int((L(f'{OUT}/png/{a}_{f["key"]}_{fr}.png') != L(f'{OUT}/png/{b}_{f["key"]}_{fr}.png')).any())
               for f in fs for fr in ('z1', 'z2', 'hd'))
    print(f'{a} vs {b}: {diff} frames differ')
sys.path.insert(0, HERE)
from measure import caps_windows, joins_windows, tally, frame
for m in range(10):
    t = f'capx{m}'; cells = []
    for name, cap in (('caps', 'round'), ('joins', None)):
        per = []
        for fr in ('z1', 'z2', 'hd'):
            rows = tally(f'red__{name}', caps_windows(cap, fr) if cap else joins_windows(fr), {t: frame(t, f'red__{name}', fr)})
            per.append(sum(r[t][1] for r in rows.values()))
        cells.append(f'{name} {"/".join(map(str, per))}')
    out = subprocess.run([sys.executable, f'{HERE}/corpus.py', 'mstc', t, f'corpus_{t}.json'], capture_output=True, text=True).stdout
    tot = [l for l in out.splitlines() if ' all :' in l]
    tw = ', '.join(l.split()[0] + ' ' + l.split(':')[2].split(',')[0].split()[0] + '/' + l.split(':')[2].split(',')[1].split()[0] for l in tot)
    print(f'mode {m} ({NAMES[m]}): {"; ".join(cells)}; corpus toward/away {tw}')
    os.remove(f'{HERE}/corpus_{t}.json')
