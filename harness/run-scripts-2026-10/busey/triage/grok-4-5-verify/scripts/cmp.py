import sys, numpy as np
sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from PIL import Image
import femsim, shapes
L=lambda p: np.asarray(Image.open(p).convert('L'),dtype=np.float64)/255
for name in ['tongues','wedge','spike']:
    real=L(f'png/mst2_t__{name}_z2.png')[:,30:430]
    sh={'tongues':shapes.tongues,'wedge':shapes.wedges,'spike':shapes.spike}[name]()
    for cs in (1,-1,None):
        sim=femsim.render(sh,cull_sign=cs)[:,30:430]
        d=np.abs(sim-real)
        print(name,'cull',cs,'max|d|',d.max().round(3),'px>2/255',(d>2/255).sum(),'px>20/255',(d>20/255).sum(),'sum sim',sim.sum().round(2),'real',real.sum().round(2))
