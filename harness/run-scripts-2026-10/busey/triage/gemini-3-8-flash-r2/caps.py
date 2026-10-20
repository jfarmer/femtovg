import numpy as np, math
from PIL import Image
from xy import s2f
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=float)
ends=[((870,100),(820,60)),((900,210),(870,160)),((910,340),(890,280)),((880,480),(870,410)),((730,380),(810,360)),((710,25),(640,5)),((790,110),(730,100)),((720,60),(650,65)),((280,360),(230,300)),((260,160),(220,220))]
bgv=np.array([0x11,0x16,0x1d],float)
for k in ('r20_caps_round','r21_caps_butt'):
  for fr in ('hd','z2'):
    o=L(f'png/mst4_t__{k}_{fr}.png'); r={x:L(f'refs/{x}_t__{k}_{fr}.png') for x in ('chr','ff','wk','id')}
    tot={x:0.0 for x in ('fv','chr','ff','wk','id')}; red=0
    off=[np.abs(o-r[x]).max(2)>20 for x in ('chr','ff','wk')]; a3=off[0]&off[1]&off[2]
    for (e,c) in ends:
        ex,ey=s2f(*e,fr); cx,cy=s2f(*c,fr)
        # window: 3 px around the end point, beyond-the-end half-plane plus 1.5 px back
        dx,dy=ex-cx,ey-cy; n=math.hypot(dx,dy); dx/=n; dy/=n
        ys,xs=np.mgrid[int(ey)-4:int(ey)+5,int(ex)-4:int(ex)+5]
        along=(xs+.5-ex)*dx+(ys+.5-ey)*dy; perp=np.abs(-(xs+.5-ex)*dy+(ys+.5-ey)*dx)
        m=(along>-1.5)&(along<3)&(perp<3)
        for x,img in (('fv',o),*r.items()):
            tot[x]+=((img[ys,xs].mean(2)-bgv.mean())*m).sum()
        red+=(a3[ys,xs]&m).sum()
    print(k,fr,'end-window ink vs area:',' '.join(f'{x} {tot[x]/tot["id"]:.2f}' for x in ('fv','chr','ff','wk')),' red in windows',red,'of',a3.sum())
