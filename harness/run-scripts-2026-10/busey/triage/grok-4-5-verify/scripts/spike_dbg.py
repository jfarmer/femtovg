import sys, numpy as np
sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
import femsim, shapes
log=[]
img=femsim.render(shapes.spike(),cull_sign=1,log=log)
g=log[0]; P=g['P']
tip=np.array(femsim.dev(80,260))
dd=np.hypot(*(P-tip).T)
print('n points',len(P))
for i in np.argsort(dd)[:14]:
    print(i, P[i].round(3).tolist(), 'd=%.2f'%dd[i], 'flags',g['flags'][i])
print('fill verts near tip'); 
F=g['fill']; df=np.hypot(*(F-tip).T)
for i in np.argsort(df)[:10]: print(i,F[i].round(3).tolist(),'d=%.2f'%df[i])
np.set_printoptions(linewidth=250)
st=g['stencil']; fr=g['fringe']; cv=g['cover']
print('rows: stencil values in row near tip')
for y in range(31,46):
    xs=slice(56,80)
    print(y,'stc',''.join({0:'.',1:'+',-1:'-'}.get(v,'?') for v in st[y,xs]),'cov %.2f fringe %.2f tot %.2f'%(cv[y,xs].sum(),fr[y,xs].sum(),img[y,xs].sum()))
