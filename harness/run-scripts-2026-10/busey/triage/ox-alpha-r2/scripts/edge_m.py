import numpy as np; from PIL import Image
B='/Users/matt/src/femtovg-wt/runs/busey/'; K='corpus__buseybench__muse-spark-1-3-contributor'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=float)
ims={n:L(B+p+'_hd.png') for n,p in [('fv','png/mst4_'+K),('chr','refs/chr_'+K),('ff','refs/ff_'+K),('wk','refs/wk_'+K),('id','refs/id_'+K)]}
S=1080/1024
def bez(P,t):
  P=np.array(P,float); t=np.asarray(t)[:,None]
  return (1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t*t*P[2]+t**3*P[3]
ts=np.linspace(0,1,400001)
b=bez([(250,600),(240,450),(270,200),(512,125)],ts)
fx=420+b[:,0]*S; fy=b[:,1]*S
light,dark=199.,161.
for Y in range(150,400,10):
  yc=Y+0.5
  j=np.argmin(np.abs(fy-yc)); xa=fx[j]
  x0=int(xa)-4
  row={}
  for n,im in ims.items():
    g=im[Y,x0:x0+9,1]
    fr=np.clip((g-dark)/(light-dark),0,1)
    row[n]=x0+fr.sum()
  print(Y, 'true %.2f'%xa, ' '.join('%s %.2f'%(n,v-xa) for n,v in row.items()))
