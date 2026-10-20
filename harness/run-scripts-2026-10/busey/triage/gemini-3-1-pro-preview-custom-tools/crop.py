import sys, numpy as np
from PIL import Image
sys.path.insert(0, '/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview-custom-tools')
from emap import L, masks
# crop.py ours.png refdir_prefix x0 y0 x1 y1 scale out
ours_p, k, x0,y0,x1,y1, sc, out = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:8]), sys.argv[8]
refdir = sys.argv[9] if len(sys.argv) > 9 else '/Users/matt/src/femtovg-wt/runs/busey/refs'
ours = L(ours_p); refs = [L(f'{refdir}/{x}_{k}_z2.png') for x in ('chr','ff','wk')]
a, ag, sp = masks(ours, refs)
g = (ours.mean(axis=2)*0.35+120).clip(0,255).astype('uint8'); em = np.stack([g,g,g],2)
off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
some = (off[0]|off[1]|off[2]) & ~a
em[some] = [255,170,0]; em[a] = [230,0,0]
ps = [ours.astype('uint8')] + [r.astype('uint8') for r in refs] + [em]
ps = [Image.fromarray(p[y0:y1, x0:x1]).resize(((x1-x0)*sc, (y1-y0)*sc), Image.NEAREST) for p in ps]
W = sum(p.size[0] for p in ps) + 4*4
s = Image.new('RGB', (W, ps[0].size[1]), 'white'); x = 0
for p in ps: s.paste(p, (x, 0)); x += p.size[0] + 4
s.save(out); print('all3 in crop', a[y0:y1,x0:x1].sum(), 'agreed', ag[y0:y1,x0:x1].sum(), 'total all3', a.sum())
