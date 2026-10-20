import json, os, subprocess, sys
import numpy as np
from PIL import Image
from common import *
by_key = {f['key']: f for f in files()}
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
for spec in sys.argv[1:]:
    k, fr = spec.rsplit(':', 1)
    f, z = FRAMINGS[fr]
    r = subprocess.run([f'{BIN}/_logos_full_ddd10', f'{z:g}', f'{OUT}/tmp/g.ppm', by_key[k]['path']],
                       env={**os.environ, **f, **SWEEP_ENV, 'SINGLE_SHADOW_LAYER': '1', 'RV_DIAG': '1'}, capture_output=True, text=True)
    merges = [tuple(map(float, l.split()[1:3])) + (l.split()[3], l.split()[5]) for l in r.stderr.splitlines() if l.startswith('RVMERGE')]
    fills = [l for l in r.stderr.splitlines() if l.startswith(('RVFILL', 'RVSTROKE'))]
    lay = [l for l in r.stderr.splitlines() if 'layers begun' in l]
    b=L(f'png_changed/m10_{k}_{fr}.png'); a=L(f'png_changed/dd10_{k}_{fr}.png')
    refs={x: L(f'refs/{x}_{k}_{fr}.png') for x in ('id','chr','ff')}
    d=(a!=b).any(2)
    agree=np.ones(d.shape,bool); ks=list(refs)
    for i in range(3):
        for j in range(i+1,3): agree&=np.abs(refs[ks[i]]-refs[ks[j]]).max(2)<=20
    fa=np.ones(d.shape,bool)
    for v in refs.values(): fa&=(np.abs(a-v).max(2)-np.abs(b-v).max(2))>20
    ys,xs=np.nonzero(d&fa&agree)
    print(f'== {k} {fr}: {len(merges)} merges, {lay}')
    for y,x in zip(ys,xs):
        dist = min(((mx-x-0.5)**2+(my-y-0.5)**2)**0.5 for mx,my,_,_ in merges) if merges else -1
        print(f'   ({x},{y}) m8 {b[y,x].tolist()} rv {a[y,x].tolist()} area {refs["id"][y,x].tolist()} chr {refs["chr"][y,x].tolist()} ff {refs["ff"][y,x].tolist()}  nearest merge {dist:.1f} px')
    for l in fills[:6]: print('   ', l)
