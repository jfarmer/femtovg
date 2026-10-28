import sys; sys.path.insert(0,'scripts')
import numpy as np; from PIL import Image
from coords import S as FRS
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
bg=np.array([214.,164.,135.]); fg=np.array([26.,15.,10.])
BOX={'r04_lash_x3':(185,335,578,452)}
for k in sys.argv[1:]:
  for fr in ('z2','hd'):
    ox,oy,s=FRS[fr]; u0,v0,u1,v1=BOX.get(k,(316,392,446,426))
    sl=(slice(max(0,int(oy+v0*s)),int(np.ceil(oy+v1*s))),slice(max(0,int(ox+u0*s)),int(np.ceil(ox+u1*s))))
    ims={'fem':L(f'png/mst4_t__{k}_{fr}.png')[sl],**{b:L(f'refs/{b}_t__{k}_{fr}.png')[sl] for b in ('chr','ff','wk','id')}}
    cov={n:((im-bg)@(fg-bg))/((fg-bg)@(fg-bg)) for n,im in ims.items()}
    o=ims['fem']; off=[np.abs(o-ims[b]).max(2)>20 for b in ('chr','ff','wk','id')]; a=off[0]&off[1]&off[2]
    print(f'{k:14s} {fr} red {int(a.sum()):3d} off_id {int(off[3].sum()):3d} red&off_id {int((a&off[3]).sum()):3d} | ink/id ' + ' '.join(f'{n} {cov[n].sum()/cov["id"].sum():.3f}' for n in ('fem','chr','ff','wk')) + f' (id ink {cov["id"].sum():.1f} px)')
