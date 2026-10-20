import sys, json, numpy as np
from PIL import Image
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
for k in sys.argv[1:]:
    for fr in ('z2', 'hd'):
        try: refs = {b: L(f'{D}/refs/{b}_t__{k}_{fr}.png') for b in ('chr', 'ff', 'wk', 'id')}
        except FileNotFoundError: continue
        out = []
        for bld in [b for b in ('mst4', 'fm') if __import__('os').path.exists(f'{D}/png/{b}_t__{k}_{fr}.png')]:
            o = L(f'{D}/png/{bld}_t__{k}_{fr}.png')
            off = [np.abs(o - refs[b]).max(2) > 20 for b in ('chr', 'ff', 'wk')]; a3 = off[0] & off[1] & off[2]
            out.append(f'{bld}: all3 {a3.sum():4d} offarea {(np.abs(o - refs["id"]).max(2) > 20).sum():4d}')
        br = ' '.join(f'{b}-offarea {(np.abs(refs[b] - refs["id"]).max(2) > 20).sum():4d}' for b in ('chr', 'ff', 'wk'))
        print(f'{k:12s} {fr} | ' + ' | '.join(out) + ' | ' + br)
