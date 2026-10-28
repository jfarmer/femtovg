import os, json, numpy as np
from PIL import Image
H=os.path.expanduser('~/'); R=H+'src/femtovg-wt/runs/zoom/'
A=R+'triage/gradient-hard-stops/out/'; B=R+'triage/gradient-hard-stops-v/out/'
Z=['z1','z125','z15','z175','z2','z3','z4','z075','z05','z033','z025']
cl=json.load(open(R+'triage/clusters_compact.json'))['gradient-hard-stops']
def load(p):
    try: return np.asarray(Image.open(p).convert('RGB')).astype(int)
    except Exception: return None
V=[(A,'master'),(A,'p1024'),(A,'p4096'),(A,'near256'),(A,'near4096'),(B,'c256l'),(B,'c256n'),(B,'c1024l'),(B,'c16384l'),(B,'c16384n')]
for e in cl:
    key=e['key']; print(key.split('__')[-1])
    for d,v in V:
        row=[]
        for f in Z:
            img=load(f'{d}{v}_{key}_{f}.png')
            if img is None: row.append(f'{f}:-'); continue
            cnt={}
            for br in ['chr','ff','wk']:
                r=load(f'{R}fresh/refs/{br}_{key}_{f}.png')
                if r is None: continue
                cnt[br]=int((np.abs(img-r).max(axis=2)>8).sum())
            b=min(cnt.items(),key=lambda x:x[1])
            row.append(f'{f}:{b[1]}{b[0][0]}' + ('' if len(cnt)==3 else f'({len(cnt)})'))
        print('  ',v.ljust(9),' '.join(row))

# The 640 px repro (repro.svg; FRAME_W=640 FRAME_H=20 BOX=640 BOX_X=0 BOX_Y=0) at zoom 1 and 2, against Chromium 131.
RP = os.path.dirname(os.path.abspath(__file__)) + '/repro/'
ref = {1: load(RP + 'chr_z1.png'), 2: load(RP + 'chr_z2.png')}
print('repro.svg, px > 8/255 off Chromium (columns)')
for v in ['master', 'near256', 'p1024', 'c1024l', 'p4096']:
    out = []
    for z in (1, 2):
        a = load(f'{RP}{v}_z{z}.png')
        d = np.abs(a - ref[z]).max(axis=2)
        out.append(f'z{z}: {int((d > 8).sum())} {np.where((d > 8).any(axis=0))[0].tolist()}')
    print('  ', v.ljust(9), ' | '.join(out))
