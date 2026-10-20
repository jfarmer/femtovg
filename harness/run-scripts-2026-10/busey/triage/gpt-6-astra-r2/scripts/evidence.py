"""evidence.py FR x0 y0 x1 y1 scale out: femtovg | Chromium as framed today (root caps dropped) | Chromium with root caps | area ref with root caps | red before | red after"""
import sys, numpy as np
from PIL import Image, ImageDraw
fr=sys.argv[1]; x0,y0,x1,y1,s=map(int,sys.argv[2:7]); out=sys.argv[7]
R='/Users/matt/src/femtovg-wt/runs/busey/refs'; K='corpus__buseybench__gpt-6-astra'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
o=L(f'png/mst4_t__orig_{fr}.png')
old=[L(f'{R}/{b}_{K}_{fr}.png') for b in ('chr','ff','wk')]; new=[L(f'refs/{b}_t__g01_rootcaps_{fr}.png') for b in ('chr','ff','wk')]
idn=L(f'refs/id_t__g01_rootcaps_{fr}.png')
def emap(rs):
    off=[np.abs(o-r).max(2)>20 for r in rs]; a=off[0]&off[1]&off[2]
    g=(0.3*o[...,0]+0.59*o[...,1]+0.11*o[...,2]); em=np.stack([g*0.5+100]*3,-1); em[a]=[230,0,0]; return em, int(a[y0:y1,x0:x1].sum())
e0,n0=emap(old); e1,n1=emap(new)
tiles=[(o,'femtovg master'),(old[0],'Chromium, ref as framed (butt)'),(new[0],'Chromium, root caps kept'),(idn,'area ref, root caps kept'),(e0,f'off all 3, today: {n0}'),(e1,f'off all 3, caps kept: {n1}')]
w=(x1-x0)*s; h=(y1-y0)*s
c=Image.new('RGB',(3*(w+4),2*(h+16)),'white'); d=ImageDraw.Draw(c)
for i,(t,n) in enumerate(tiles):
    X=(i%3)*(w+4); Y=(i//3)*(h+16)
    c.paste(Image.fromarray(np.clip(t[y0:y1,x0:x1],0,255).astype(np.uint8)).resize((w,h),Image.NEAREST),(X,Y+14)); d.text((X+2,Y+1),n,fill='black')
c.save(out); print(out,n0,n1)
