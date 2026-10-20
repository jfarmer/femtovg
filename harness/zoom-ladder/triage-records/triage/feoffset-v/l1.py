import json, numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/zoom/'
A='/Users/matt/src/femtovg-wt/runs/zoom/triage/feoffset/area/'
FR={0.25:'z025',0.33:'z033',0.5:'z05',0.75:'z075',1.25:'z125',1.5:'z15',1.75:'z175',3:'z3'}
def L(p):
    try: return np.asarray(Image.open(p).convert('RGB')).astype(float)
    except Exception: return None
cl=[e for e in json.load(open(R+'triage/clusters_compact.json'))['feoffset'] if e['key'].startswith('corpus__')]
tot={k:[] for k in ('fv','chr','ff','wk')}
for e in cl:
    name=e['key'].split('__')[-1]
    for b in e['bad']:
        z=b[0]; fr=FR[z]
        F={'fv':L(f"{R}png/zl_zm_svg/{e['key']}/fresh_{fr}.png")}
        for k in ('chr','ff','wk'): F[k]=L(f"{R}fresh/refs/{k}_{e['key']}_{fr}.png")
        ar=L(f'{A}{name}_{fr}.png')
        if ar is None: print('no area',name,fr); continue
        l1={k:np.abs(F[k]-ar).sum()/255/3 for k in F}   # coverage-pixel units
        cnt={k:int((np.abs(F[k]-ar).max(-1)>8).sum()) for k in F}
        if name not in ('offset-border-stroke-fill','offset-circle-shape','offset-triple-chain-rgb-shadow','offset-sourcealpha-flood'):
            for k in tot: tot[k].append(l1[k])
        print(f"{name[7:47]:40s} {z:5} L1 " + ' '.join(f"{k}={l1[k]:6.2f}" for k in l1) + ' | n8 '+' '.join(f"{k}={cnt[k]}" for k in cnt))
print({k:(len(v),round(float(np.mean(v)),2)) for k,v in tot.items()})
