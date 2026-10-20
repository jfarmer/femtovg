import sys, os, subprocess, json, numpy as np
from PIL import Image
H='/Users/matt/'
R=H+'src/femtovg-wt/runs/zoom/'
OUT=R+'triage/gradient-hard-stops/out/'
os.makedirs(OUT,exist_ok=True)
Z={'z1':1,'z125':1.25,'z15':1.5,'z175':1.75,'z2':2,'z3':3,'z4':4,'z075':.75,'z05':.5,'z033':.33,'z025':.25}
bins={'master':H+'src/femtovg-wt/bin/_logos_full_zm2','lut':R+'triage/gradient-hard-stops/bin/_logos_full_lut'}
variants={'master':('master',{}),'p256':('lut',{}),'p1024':('lut',{'FEMTOVG_GRADIENT_LUT':'1024'}),'p4096':('lut',{'FEMTOVG_GRADIENT_LUT':'4096'}),
          'near256':('lut',{'FEMTOVG_GRADIENT_NEAREST':'1'}),'near4096':('lut',{'FEMTOVG_GRADIENT_NEAREST':'1','FEMTOVG_GRADIENT_LUT':'4096'})}
cl=json.load(open(R+'triage/clusters_compact.json'))['gradient-hard-stops']
want=sys.argv[1].split(',') if len(sys.argv)>1 else list(variants)
env0=dict(os.environ,FRAME_W='460',FRAME_H='260',BOX='200',BOX_X='130',BOX_Y='30',SKIP_UNSUPPORTED_FILTERS='1',VIEWPORT_CLIP='1',TRANSIENT_BUDGET_MB='1024')
def load(p):
    try: return np.asarray(Image.open(p).convert('RGB')).astype(int)
    except Exception: return None
res={}
for e in cl:
    key=e['key']; svg=H+e['path']
    for v in want:
        b,extra=variants[v]
        row=[]
        for f,z in Z.items():
            ppm=f'{OUT}{v}_{key}_{f}.ppm'
            subprocess.run([bins[b],str(z),ppm,svg],env=dict(env0,**extra),check=True,capture_output=True)
            img=np.asarray(Image.open(ppm).convert('RGB')).astype(int)
            Image.fromarray(img.astype(np.uint8)).save(ppm[:-4]+'.png'); os.remove(ppm)
            best=None
            for br in ['chr','ff','wk']:
                r=load(f'{R}fresh/refs/{br}_{key}_{f}.png')
                if r is None: continue
                n=int((np.abs(img-r).max(axis=2)>8).sum())
                if best is None or n<best[0]: best=(n,br)
            row.append(f'{f}:{best[0]}{"!" if best[0]>24 else ""}')
        print(key.split('__')[-1][:40].ljust(40), v.ljust(8), ' '.join(row), flush=True)
