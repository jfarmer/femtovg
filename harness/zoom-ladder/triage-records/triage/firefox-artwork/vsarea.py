import sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from zoom_ladder import LADDER, FRAMING_OF
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
A=f'{R}/triage/firefox-artwork/area'
key=sys.argv[1]
extra=dict(a.split('=',1) for a in sys.argv[2:])  # name=dir-with-<fr>.png pattern
def L(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16) if os.path.exists(p) else None
def n8(a,b): return int((np.abs(a-b).max(axis=2)>8).sum()) if a is not None and b is not None else None
print('zoom  fv  chr  ff  wk  (vs area ref) | chr1x-vs-refchr | ' + ' '.join(extra))
for z in sorted(set(LADDER)):
    st=LADDER.index(z); fr=FRAMING_OF[z]
    ar=L(f'{A}/id8_{key}_{fr}.png')
    fv=L(f'{R}/png/zl_zm_svg/{key}/{st:02}.png')
    row=[n8(fv,ar)]+[n8(L(f'{R}/fresh/refs/{b}_{key}_{fr}.png'),ar) for b in ['chr','ff','wk']]
    c1=n8(L(f'{A}/id1_{key}_{fr}.png'),L(f'{R}/fresh/refs/chr_{key}_{fr}.png'))
    ex=[n8(L(p.replace('FR',fr).replace('STEP',f'{st:02}')),ar) for p in extra.values()]
    print(f'{z:<5}', row, c1, ex)
