"""measure.py [key-substring...] [build=mst4] [frs=z2,hd]: per variant: all3/agreed, off-area, spread, per-region boxes (svg coords)"""
import sys, os, json, numpy as np
from PIL import Image
S='/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2'
sys.path.insert(0,f'{S}/scripts')
from locate import S as FS
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
REG={'o':{'mouthL':[(395,650,425,695)],'mouthR':[(599,650,629,695)],'dashcorner':[(348,912,368,934),(656,912,676,934)],
          'lashes':[(385,438,475,462),(549,438,639,462)],'strands':[(280,80,800,345)]},
     'g':{'nostril':[(500,575,518,595)],'mouthcorners':[(335,665,395,740),(680,665,735,740)],'hairgold':[(285,545,305,570)]},
     'p':{'locks':[(285,225,372,330)]},
     'q':{'L284tip':[(775,355,795,380)],'L145tips':[(370,760,390,780),(632,772,652,792)],'L151tips':[(292,402,308,422),(462,406,478,424)]},
     's':{}}
a=dict(x.split('=',1) for x in sys.argv[1:] if '=' in x); pats=[x for x in sys.argv[1:] if '=' not in x]
b=a.get('build','mst4'); frs=a.get('frs','z2,hd').split(',')
files=json.load(open(f'{S}/files.json'))
def box(fr,u0,v0,u1,v1):
    ox,oy,s=FS[fr]; return (int(ox+u0*s),int(oy+v0*s),int(np.ceil(ox+u1*s)),int(np.ceil(oy+v1*s)))
for f in files:
    k=f['key']
    if pats and not any(p in k for p in pats): continue
    for fr in frs:
        pp=f'{S}/png/{b}_{k}_{fr}.png'
        if not os.path.exists(pp): continue
        o=L(pp); refs=[L(f'{S}/refs/{x}_{k}_{fr}.png') for x in ('chr','ff','wk')]; idr=L(f'{S}/refs/id_{k}_{fr}.png')
        off=[np.abs(o-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
        sp=np.zeros(all3.shape,bool)
        for i in range(3):
            for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
        oi=np.abs(o-idr).max(2)>20
        r=f"all3 {all3.sum():4d} agr {(all3&~sp).sum():4d} offarea {oi.sum():6d} all3&offarea {(all3&oi).sum():4d} spread {sp.sum():6d}"
        t=k[3]
        cov=np.zeros(all3.shape,bool)
        for n,bx in REG.get(t,{}).items():
            m=np.zeros(all3.shape,bool)
            for (u0,v0,u1,v1) in bx:
                x0,y0,x1,y1=box(fr,u0,v0,u1,v1); m[max(y0,0):max(y1,0),max(x0,0):max(x1,0)]=True
            m&=~cov; cov|=m
            r+=f" | {n} {(all3&m).sum()}"
        if REG.get(t): r+=f" | rest {(all3&~cov).sum()}"
        print(f'{k:28s} {fr} {r}')
