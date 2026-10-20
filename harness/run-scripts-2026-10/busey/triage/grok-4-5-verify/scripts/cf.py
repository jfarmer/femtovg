import sys, numpy as np
sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from PIL import Image
import femsim, shapes
L=lambda p: np.asarray(Image.open(p).convert('L'),dtype=np.float64)/255
real=L('png/mst2_t__spike_z2.png'); refs={k:L(f'refs/{k}_t__spike_z2.png') for k in ('chr','ff','wk')}
tx,ty=femsim.dev(80,260); box=(slice(int(ty)-2,int(ty)+22), slice(int(tx)-4,int(tx)+18))
rows=range(31,46)
def rowsum(im): return [im[y,int(tx)-4:int(tx)+18].sum() for y in rows]
runs={'femtovg':real}
log=[]
runs['sim']=femsim.render(shapes.spike(),cull_sign=1,log=log)
st=log[0]['stencil']; vals,c=np.unique(st[st!=0],return_counts=True); print('stencil values and counts over the whole spike',dict(zip(vals.tolist(),c.tolist())))
runs['sim_no_inverted_lobe']=femsim.render(shapes.spike(),cull_sign=1,stencil_mode='no_inverted')
runs['sim_strip_inner_0.5']=femsim.render(shapes.spike(),cull_sign=1,half=True)
for k,v in refs.items(): runs[k]=v
print('%-22s %8s %8s  rows 31-45 (per-row coverage)'%('run','tipbox','whole'))
for k,im in runs.items():
    im2=im[:,30:430]
    print('%-22s %8.2f %8.1f  '%(k,im[box].sum(),im2.sum())+' '.join('%.2f'%r for r in rowsum(im)))
for k in ('sim_no_inverted_lobe','sim_strip_inner_0.5'):
    off=[np.abs(runs[k]-r).max() if False else None for r in []]
    red=np.ones(real.shape,bool)
    for r in refs.values(): red&=np.abs(runs[k]-r)>20/255
    print(k,'px >20/255 off all three:',red[:,30:430].sum())
red=np.ones(real.shape,bool)
for r in refs.values(): red&=np.abs(real-r)>20/255
print('femtovg px >20/255 off all three:',red[:,30:430].sum())
