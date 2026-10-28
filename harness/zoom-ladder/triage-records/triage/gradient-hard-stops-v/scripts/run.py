import sys, os, subprocess, json, numpy as np
from PIL import Image
H=os.path.expanduser('~/')
R=H+'src/femtovg-wt/runs/zoom/'
OUT=R+'triage/gradient-hard-stops-v/out/'
Z={'z1':1,'z125':1.25,'z15':1.5,'z175':1.75,'z2':2,'z3':3,'z4':4,'z075':.75,'z05':.5,'z033':.33,'z025':.25}
STEP={'z1':0,'z125':1,'z15':2,'z175':3,'z2':4,'z3':5,'z4':6,'z075':13,'z05':14,'z033':15,'z025':16}
PROBE=R+'triage/gradient-hard-stops-v/bin/_logos_full_probe'
MASTER=H+'src/femtovg-wt/bin/_logos_full_zm2'
variants={'master':(MASTER,{}),'probe_default':(PROBE,{}),
 'c16384n':(PROBE,{'FEMTOVG_PROBE_CENTRE':'16384','FEMTOVG_PROBE_NEAREST':'1'}),
 'c16384l':(PROBE,{'FEMTOVG_PROBE_CENTRE':'16384'}),
 'c256n':(PROBE,{'FEMTOVG_PROBE_CENTRE':'256','FEMTOVG_PROBE_NEAREST':'1'}),
 'c256l':(PROBE,{'FEMTOVG_PROBE_CENTRE':'256'}),
 'c1024l':(PROBE,{'FEMTOVG_PROBE_CENTRE':'1024'}),
}
cl=json.load(open(R+'triage/clusters_compact.json'))['gradient-hard-stops']
want=sys.argv[1].split(',')
env0=dict(os.environ,FRAME_W='460',FRAME_H='260',BOX='200',BOX_X='130',BOX_Y='30',SKIP_UNSUPPORTED_FILTERS='1',VIEWPORT_CLIP='1',TRANSIENT_BUDGET_MB='1024')
def load(p):
    try: return np.asarray(Image.open(p).convert('RGB')).astype(int)
    except Exception: return None
for e in cl:
    key=e['key']; svg=H+e['path']
    for v in want:
        b,extra=variants[v]; row=[]; same=0
        for f,z in Z.items():
            ppm=f'{OUT}{v}_{key}_{f}.ppm'
            subprocess.run([b,str(z),ppm,svg],env=dict(env0,**extra),check=True,capture_output=True)
            img=np.asarray(Image.open(ppm).convert('RGB')).astype(int)
            Image.fromarray(img.astype(np.uint8)).save(ppm[:-4]+'.png'); os.remove(ppm)
            lad=load(f'{R}png/zl_zm_svg/{key}/{STEP[f]:02d}.png')
            same+= int(lad is not None and lad.shape==img.shape and (lad==img).all())
            cnt={}
            for br in ['chr','ff','wk']:
                r=load(f'{R}fresh/refs/{br}_{key}_{f}.png')
                if r is None: continue
                cnt[br]=int((np.abs(img-r).max(axis=2)>8).sum())
            best=min(cnt.items(),key=lambda x:x[1])
            row.append(f'{f}:{best[1]}{best[0][0]}{"!" if best[1]>24 else ""}')
        print(key.split('__')[-1][:34].ljust(34), v.ljust(13), f'ladder-identical {same}/11 ', ' '.join(row), flush=True)
