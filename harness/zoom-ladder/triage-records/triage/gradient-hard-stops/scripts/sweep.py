# Run the 4096-texel LUT build on every failing (file, zoom) of every cluster; report the ones that move.
import os, subprocess, json, numpy as np
from PIL import Image
H='/Users/matt/'
R=H+'src/femtovg-wt/runs/zoom/'
T=R+'triage/gradient-hard-stops/'
OUT=T+'sweep/'; os.makedirs(OUT,exist_ok=True)
Zn={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',.75:'z075',.5:'z05',.33:'z033',.25:'z025'}
step={1:0,1.25:1,1.5:2,1.75:3,2:4,3:5,4:6,.75:13,.5:14,.33:15,.25:16}
env=dict(os.environ,FRAME_W='460',FRAME_H='260',BOX='200',BOX_X='130',BOX_Y='30',SKIP_UNSUPPORTED_FILTERS='1',VIEWPORT_CLIP='1',TRANSIENT_BUDGET_MB='1024',FEMTOVG_GRADIENT_LUT='4096')
def load(p):
    try: return np.asarray(Image.open(p).convert('RGB')).astype(int)
    except Exception: return None
def best(img,key,f):
    b=None
    for br in ['chr','ff','wk']:
        r=load(f'{R}fresh/refs/{br}_{key}_{f}.png')
        if r is None: continue
        n=int((np.abs(img-r).max(axis=2)>8).sum())
        if b is None or n<b: b=n
    return b
cl=json.load(open(R+'triage/clusters_compact.json'))
log=open(T+'sweep.txt','w')
for cname,files in cl.items():
    for e in files:
        key=e['key']; svg=H+e['path']
        for bad in e['bad']:
            z=bad[0]; f=Zn[z]
            m=load(f'{R}png/zl_zm_svg/{key}/{step[z]:02d}.png')
            ppm=f'{OUT}x.ppm'
            p=subprocess.run([T+'bin/_logos_full_lut',str(z),ppm,svg],env=env,capture_output=True)
            if p.returncode: print(cname,key,z,'ERR',file=log,flush=True); continue
            img=np.asarray(Image.open(ppm).convert('RGB')).astype(int)
            same=int((img!=m).any(axis=2).sum())
            bm=best(m,key,f); bp=best(img,key,f)
            print(cname,key,z,'master',bm,'lut4096',bp,'px_changed',same,file=log,flush=True)
log.close()
