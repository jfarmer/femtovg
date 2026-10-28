"""attr.py FR: attribute every pixel femtovg master draws > 20 off all three browsers (corpus refs) to a cause."""
import sys, json, numpy as np
from PIL import Image
fr=sys.argv[1]
R='/Users/matt/src/femtovg-wt/runs/busey/refs'; K='corpus__buseybench__gpt-6-astra'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def red(o, rs):
    off=[np.abs(o-r).max(2)>20 for r in rs]; return off[0]&off[1]&off[2]
o=L(f'png/mst4_t__orig_{fr}.png'); fm=L(f'png/fm_t__orig_{fr}.png')
old=[L(f'{R}/{b}_{K}_{fr}.png') for b in ('chr','ff','wk')]; old_id=L(f'{R}/id_{K}_{fr}.png')
new=[L(f'refs/{b}_t__g01_rootcaps_{fr}.png') for b in ('chr','ff','wk')]; new_id=L(f'refs/id_t__g01_rootcaps_{fr}.png')
r0=red(o,old); r1=red(o,new); rfm=red(fm,new)
near_id=np.abs(o-new_id).max(2)<=20
caps=r0&~r1
res=r0&r1
print(f'{fr}: red vs corpus refs {r0.sum()}; vanish with root caps restored in the refs {caps.sum()} (femtovg within 20 of the round-cap area ref at {(caps&near_id).sum()}); left {res.sum()}')
fillfix=res&~rfm
print(f'  of the {res.sum()} left: femtovg within 20 of area ref {(res&near_id).sum()}; vanish with exact-area fills {fillfix.sum()} (of which near area ref already {(fillfix&near_id).sum()})')
print(f'  red with exact fills that was not red on master: {(rfm&~r1).sum()}')
rest=res&rfm&~near_id
ys,xs=np.nonzero(rest); print('  rest (femtovg off area ref, not a fill fringe):',list(zip(xs.tolist(),ys.tolist())))
np.save(f'm_caps_{fr}.npy',caps); np.save(f'm_fill_{fr}.npy',fillfix&~near_id); np.save(f'm_nearid_{fr}.npy',res&near_id); np.save(f'm_rest_{fr}.npy',rest)
# the old area reference (butt caps too) at the caps pixels
print(f'  corpus area ref (butt caps) within 20 of femtovg at caps pixels: {(caps&(np.abs(o-old_id).max(2)<=20)).sum()}')
