import numpy as np, os, sys
from PIL import Image
B=os.path.expanduser('~/src/femtovg-wt/runs/busey/refs')
def load(p): return np.asarray(Image.open(p).convert('RGB'),np.int16)
def z2(u,v): return 0.390625*u+30, 0.390625*v-70
def hd(u,v): return 420+1.0546875*u, 1.0546875*v
def z1(u,v): return 130+0.1953125*u, 30+0.1953125*v
def win(cx,cy,r=14):
    x,y=int(np.floor(cx)),int(np.floor(cy)); return (slice(y-r,y+r),slice(x-r,x+r))
P={'grok-4-5':[(80,260),(944,260)],'gemini-3-7-flash':[(345,645),(679,645)],'gemini-3-1-pro-preview':[(280,725),(744,725)],
'gemini-3-1-pro-preview-custom-tools':[(350,475),(465,480),(559,480),(674,475),(355,760),(675,730)],
'mistral-large-4':[(512,382),(430,742),(594,742),(455,770),(569,770)]}
for name,tips in P.items():
  for fr,fn in (('z2',z2),('hd',hd),('z1',z1)):
    key=f'corpus__buseybench__{name}_{fr}'
    if not os.path.exists(f'png/port/master_{name}_{fr}.png'): continue
    refs={b:load(f'{B}/{b}_{key}.png') for b in ('chr','ff','wk','id')}
    out=[]
    for v in ('master','off','masks'):
        im=load(f'png/port/{v}_{name}_{fr}.png')
        m=np.ones(im.shape[:2],bool)
        for b in ('chr','ff','wk'): m&=np.abs(im-refs[b]).max(axis=2)>20
        out.append([int(m[win(*fn(*t))].sum()) for t in tips])
    print(f'{name:36s} {fr}: master {out[0]} off {out[1]} masks {out[2]}')
