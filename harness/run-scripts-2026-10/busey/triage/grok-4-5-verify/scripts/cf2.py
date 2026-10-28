import sys, numpy as np
sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from PIL import Image
import femsim, shapes
L=lambda p: np.asarray(Image.open(p).convert('L'),dtype=np.float64)/255
def red(im,refs):
    m=np.ones(im.shape,bool)
    for r in refs: m&=np.abs(im-r)>20/255
    return m[:,30:430].sum()
for name in ['spike','mouth','brow','tongues','wedge']:
    real=L(f'png/mst2_t__{name}_z2.png'); off=L(f'png/mst2_off_t__{name}_z2.png')
    refs=[L(f'refs/{k}_t__{name}_z2.png') for k in ('chr','ff','wk')]
    sh=getattr(shapes,{'wedge':'wedges'}.get(name,name))()
    sim=femsim.render(sh,cull_sign=1)
    noinv=femsim.render(sh,cull_sign=1,stencil_mode='no_inverted')
    half=femsim.render(sh,cull_sign=1,half=True)
    print(f'{name:8s} femtovg==NO_THIN_FILL_MASKS: {np.abs(real-off).max()<1e-9}  sim max|d| {np.abs(sim-real)[:,30:430].max():.3f}  red: femtovg {red(real,refs)} sim {red(sim,refs)} no_inverted_lobe {red(noinv,refs)} strip_inner_0.5 {red(half,refs)}  ink: femtovg {real[:,30:430].sum():.1f} chr {refs[0][:,30:430].sum():.1f}')
