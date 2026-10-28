import sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from zoom_ladder import LADDER, FRAMING_OF
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
key=sys.argv[1]
zooms=[float(z) for z in sys.argv[2].split(',')] if len(sys.argv)>2 else sorted(set(LADDER))
def load(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16) if os.path.exists(p) else None
for z in zooms:
    step=LADDER.index(z)
    fv=load(f'{R}/png/zl_zm_svg/{key}/{step:02}.png')
    fr=FRAMING_OF[z]
    for b in ['chr','ff','wk']:
        o=load(f'{R}/fresh/refs/{b}_{key}_{fr}.png')
        if o is None: print(z,b,'none'); continue
        d=np.abs(fv-o).max(axis=2)
        m=d>8
        ys,xs=np.nonzero(m)
        bb=(xs.min(),ys.min(),xs.max(),ys.max()) if len(xs) else None
        s=(fv-o).sum(axis=2)
        print(f'z={z} {b}: n={m.sum()} max={d.max()} bbox={bb} signed_mean_on_bad={s[m].mean() if m.any() else 0:.1f}')
    # browsers among themselves
    c=load(f'{R}/fresh/refs/chr_{key}_{fr}.png'); w=load(f'{R}/fresh/refs/wk_{key}_{fr}.png'); f=load(f'{R}/fresh/refs/ff_{key}_{fr}.png')
    for (n1,a),(n2,bb2) in [(('chr',c),('wk',w)),(('chr',c),('ff',f)),(('ff',f),('wk',w))]:
        if a is not None and bb2 is not None:
            print(f'   {n1} vs {n2}: {(np.abs(a-bb2).max(axis=2)>8).sum()}')
