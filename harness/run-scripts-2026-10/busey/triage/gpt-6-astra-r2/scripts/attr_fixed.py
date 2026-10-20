"""attr_fixed.py FR: the red left once the reference keeps the root's round caps (refs of g01_rootcaps), by cause."""
import sys, numpy as np
from PIL import Image
fr=sys.argv[1]
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def red(o, key):
    rs=[L(f'refs/{b}_{key}_{fr}.png') for b in ('chr','ff','wk')]
    off=[np.abs(o-r).max(2)>20 for r in rs]; return off[0]&off[1]&off[2]
o=L(f'png/mst4_t__orig_{fr}.png'); idr=L(f'refs/id_t__g01_rootcaps_{fr}.png')
r1=red(o,'t__g01_rootcaps')
near=np.abs(o-idr).max(2)<=20
fm=red(L(f'png/fm_t__orig_{fr}.png'),'t__g01_rootcaps')
butt_fm=red(L(f'png/fm_t__g02_butt_{fr}.png'),'t__g02_butt')
teeth=red(L(f'png/mst4_t__g03_noteethstroke_{fr}.png'),'t__g03_noteethstroke') if fr=='hd' else r1
c_near=r1&near
c_fill=r1&~near&~fm
c_caps=r1&~near&fm&~butt_fm
c_teeth=r1&~near&fm&butt_fm&~teeth
rest=r1&~(c_near|c_fill|c_caps|c_teeth)
print(f'{fr}: red with round caps in the refs {r1.sum()}: femtovg within 20 of area ref {c_near.sum()}, fill tips {c_fill.sum()}, round caps/joins {c_caps.sum()}, teeth stroke joins {c_teeth.sum()}, rest {rest.sum()} {list(zip(*np.nonzero(rest)[::-1]))}')
for n,m in (('near',c_near),('caps',c_caps)):
    ys,xs=np.nonzero(m); print('  ',n,list(zip(xs.tolist(),ys.tolist())))
