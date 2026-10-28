import sys, numpy as np
sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
import femsim, shapes
log=[]
img=femsim.render(shapes.wedges()[:1],cull_sign=1,log=log)
g=log[0]
np.set_printoptions(precision=3, suppress=True, linewidth=200)
print('points', g['P'].round(3).tolist()); print('flags', g['flags'])
print('fill', g['fill'].round(3).tolist())
print('strip'); [print(' ',np.round(p,3).tolist(),u) for p,u in g['st']]
for x in (330,360,380,395,405,415):
    col=slice(40,55)
    print(x,'stencil',g['stencil'][col,x].tolist(),'fringe',g['fringe'][col,x].round(2).tolist())
