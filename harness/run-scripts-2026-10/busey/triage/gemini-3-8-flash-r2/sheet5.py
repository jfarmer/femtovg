# sheet5.py OUT.png ROW... ; ROW = fr:x0,y0,x1,y1:zoom  -> before(mst4) | after(FILL_MASKS) | Chromium | area | before vs Chromium | after vs Chromium | before vs area
import sys, numpy as np
from PIL import Image, ImageDraw
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
K='corpus__buseybench__gemini-3-8-flash'; R='/Users/matt/src/femtovg-wt/runs/busey/refs'
def diff(a,b):
    d=np.abs(a-b).max(2); o=np.full(a.shape,255,np.int16); o[d>8]=[255,170,0]; o[d>20]=[220,0,0]; return o
rows=[]
for spec in sys.argv[2:]:
    fr,box,z=spec.split(':'); x0,y0,x1,y1=map(int,box.split(',')); z=int(z)
    bf=L(f'png/mst4_t__g00_orig_{fr}.png'); af=L(f'png/fm_t__g00_orig_{fr}.png'); ch=L(f'{R}/chr_{K}_{fr}.png'); ff=L(f'{R}/ff_{K}_{fr}.png'); wk=L(f'{R}/wk_{K}_{fr}.png'); idr=L(f'{R}/id_{K}_{fr}.png')
    def off3(o): 
        m=(np.abs(o-ch).max(2)>20)&(np.abs(o-ff).max(2)>20)&(np.abs(o-wk).max(2)>20); im=np.full(o.shape,255,np.int16); im[m]=[220,0,0]; return im,m
    b3,bm=off3(bf); a3,am=off3(af)
    tiles=[bf,af,ch,idr,b3,a3,diff(bf,idr),diff(af,idr)]
    names=['femtovg master','exact-area fill masks','Chromium 131','area reference',f'before: off all 3 ({bm[y0:y1,x0:x1].sum()})',f'after: off all 3 ({am[y0:y1,x0:x1].sum()})','before vs area','after vs area']
    w=(x1-x0)*z; h=(y1-y0)*z
    row=Image.new('RGB',(len(tiles)*(w+4),h+16),'white'); d=ImageDraw.Draw(row)
    for i,(t,n) in enumerate(zip(tiles,names)):
        row.paste(Image.fromarray(np.clip(t[y0:y1,x0:x1],0,255).astype(np.uint8)).resize((w,h),Image.NEAREST),(i*(w+4),16)); d.text((i*(w+4)+2,2),f'{n} [{fr}]',fill='black')
    rows.append(row)
W=max(r.width for r in rows); H=sum(r.height+6 for r in rows)
out=Image.new('RGB',(W,H),'white'); y=0
for r in rows: out.paste(r,(0,y)); y+=r.height+6
out.save(sys.argv[1]); print(out.size)
