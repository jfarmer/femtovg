import numpy as np, math, sys
sys.path.insert(0,'scripts')
from red import red, L
widths=[0.8,1.2,1.5,2.0,2.5,3.0,4.0,6.0]
def tf(fr,u,v):
    z=int(fr[1:]); return (230+z*(130+u-230), 130+z*(30+v-130), z)
for fr in ['z1','z2']:
    print('==',fr)
    imgs={n:{b:L(f'refs/{b}_v__{n}_{fr}.png')[...,0].astype(float) for b in ('chr','ff','wk','id')} for n in ('r1_round','r1_butt','r1_fillcap')}
    for n in imgs: imgs[n]['fv']=L(f'png/mst4_v__{n}_{fr}.png')[...,0].astype(float)
    H,W=imgs['r1_round']['id'].shape
    yy,xx=np.mgrid[0:H,0:W]; cx=xx+.5; cy=yy+.5
    for n in ('r1_round','r1_fillcap','r1_butt'):
        I=imgs[n]; a,_=red(np.repeat(I['fv'][...,None],3,2).astype(np.int16),[np.repeat(I[b][...,None],3,2).astype(np.int16) for b in ('chr','ff','wk')])
        print(n,'off all three:',a.sum(), ' >20 off id: fv',(abs(I['fv']-I['id'])>20).sum(),'chr',(abs(I['chr']-I['id'])>20).sum(),'ff',(abs(I['ff']-I['id'])>20).sum(),'wk',(abs(I['wk']-I['id'])>20).sum())
    print(' per-cap ink / area-ref ink (cap = outer half-plane beyond the endpoint within w/2+2.5 px):')
    print('  width angle | round: fv chr ff wk | fillcap: fv | butt: fv')
    for i,w in enumerate(widths):
        y=12.37+i*23.1
        for j,ang in enumerate([0,33]):
            x0=14.29+j*95; Ln=55.0; a=math.radians(ang)
            ends=[((x0,y),(-math.cos(a),-math.sin(a))),((x0+Ln*math.cos(a),y+Ln*math.sin(a)),(math.cos(a),math.sin(a)))]
            row=[]
            for n in ('r1_round','r1_fillcap','r1_butt'):
                I=imgs[n]; vals={k:0.0 for k in ('fv','chr','ff','wk','id')}
                for (eu,ev),(du,dv) in ends:
                    px,py,z=tf(fr,eu,ev)
                    m=(((cx-px)*du+(cy-py)*dv)>0)&(np.hypot(cx-px,cy-py)<z*w/2+2.5)
                    if not m.any() or py<3 or py>H-3: vals=None; break
                    for k in vals: vals[k]+=I[k][m].sum()
                if vals is None: row=None; break
                row.append(vals)
            if row is None: continue
            r,fc,b=row
            idr=r['id']; 
            print(f'  {w:4.1f} {ang:3d} | {r["fv"]/idr:.3f} {r["chr"]/idr:.3f} {r["ff"]/idr:.3f} {r["wk"]/idr:.3f} | {fc["fv"]/fc["id"]:.3f} (id fill/stroke {fc["id"]/idr:.3f}) | {b["fv"]/b["id"]:.3f}')
