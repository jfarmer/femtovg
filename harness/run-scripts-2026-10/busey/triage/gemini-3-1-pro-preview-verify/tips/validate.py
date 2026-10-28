import sys, numpy as np
from PIL import Image
sys.path.insert(0,'/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview-verify/tips')
import sim
S=sim.S
D={'lip':"M 280 725 C 344 880 680 880 744 725 C 680 840 344 840 280 725 Z",
   'inner':"M 290 720 C 344 860 680 860 734 720 C 700 820 600 840 512 840 C 424 840 324 820 290 720 Z",
   'wedge':"M 280 725 L 512 841 L 744 725 L 512 811 Z",
   'lens_convex':"M 280 725 C 344 740 680 740 744 725 C 680 710 344 710 280 725 Z"}
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
for name in sys.argv[1:]:
    V,kind,dr,tv=sim.capture(D[name])
    fv=(255-L(f'{S}/png/mst2_t__{name}_z2.png').mean(2))/255
    for flip in (False,True):
        if flip: 
            # mirror facing convention by reversing the sign test
            import types
        r=sim.render(V,kind,dr,tv)
        break
    d=np.abs(r['cov']-fv)*255
    print(f'{name:12s} {kind:8s} fill={dr} cover={tv} sim vs femtovg: max {d.max():.1f}  >2: {(d>2).sum()}  >20: {(d>20).sum()}  ink sim {r["cov"].sum():.1f} fv {fv.sum():.1f}')
