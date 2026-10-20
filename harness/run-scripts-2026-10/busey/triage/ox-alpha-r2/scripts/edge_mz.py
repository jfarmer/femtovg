import numpy as np, sys; from PIL import Image
B='/Users/matt/src/femtovg-wt/runs/busey/'; K='corpus__buseybench__muse-spark-1-3-contributor'
fr=sys.argv[1]
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=float)
ims={n:L(B+p+'_'+fr+'.png') for n,p in [('fv','png/mst4_'+K),('chr','refs/chr_'+K),('ff','refs/ff_'+K),('wk','refs/wk_'+K),('id','refs/id_'+K)]}
z={'z1':1,'z2':2,'z4':4}[fr]; S=200/1024*z
def tf(x,y): return 230+(x-512)*S, 130+(y-512)*S
def bez(P,t):
  P=np.array(P,float); t=np.asarray(t)[:,None]
  return (1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t*t*P[2]+t**3*P[3]
ts=np.linspace(0,1,400001)
for name,segs in [('outer',[(250,600),(240,450),(270,200),(512,125)]),('inner-upper',[(512,155),(404,160),(324,200),(294,280)]),('inner-lower',[(294,280),(274,350),(264,550),(250,600)])]:
  b=bez(segs,ts); fx,fy=tf(b[:,0],b[:,1])
  for Y in range(0,60,6):
    yc=Y+0.5; d=np.abs(fy-yc)
    if d.min()>0.5: continue
    j=np.argmin(d); xa=fx[j]; x0=int(xa)-3
    print(name,Y,'true %.2f'%xa, '| fv', ' '.join('%3d'%v for v in ims['fv'][Y,x0:x0+7,1]),'| id',' '.join('%3d'%v for v in ims['id'][Y,x0:x0+7,1]), '| chr',' '.join('%3d'%v for v in ims['chr'][Y,x0:x0+7,1]))
