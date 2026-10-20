import numpy as np, sys; from PIL import Image
B='/Users/matt/src/femtovg-wt/runs/busey/'; K='corpus__buseybench__muse-spark-1-3-contributor'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=float)
ims={n:L(B+p+'_hd.png') for n,p in [('fv','png/mst4_'+K),('chr','refs/chr_'+K),('ff','refs/ff_'+K),('wk','refs/wk_'+K),('id','refs/id_'+K)]}
S=1080/1024
def bez(P,t):
  P=np.array(P,float); t=np.asarray(t)[:,None]
  return (1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t*t*P[2]+t**3*P[3]
ts=np.linspace(0,1,400001)
for name,segs in [('inner-upper',[(512,155),(404,160),(324,200),(294,280)]),('inner-lower',[(294,280),(274,350),(264,550),(250,600)])]:
  b=bez(segs,ts); fx=420+b[:,0]*S; fy=b[:,1]*S
  for Y in range(150,420,15):
    yc=Y+0.5; d=np.abs(fy-yc)
    if d.min()>0.5: continue
    j=np.argmin(d); xa=fx[j]; x0=int(xa)-4
    row={}
    for n,im in ims.items():
      g=im[Y,x0:x0+9,1]
      row[n]=' '.join('%3d'%v for v in g)
    print(name,Y,'true %.2f'%xa, '| fv', row['fv'],'| id',row['id'])
