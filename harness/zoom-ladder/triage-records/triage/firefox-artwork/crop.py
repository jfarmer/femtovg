import sys, os, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from zoom_ladder import LADDER, FRAMING_OF
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
key, z, crop, scale, out = sys.argv[1], float(sys.argv[2]), [int(v) for v in sys.argv[3].split(',')], int(sys.argv[4]), sys.argv[5]
extra = sys.argv[6:]  # additional image paths labelled
step=LADDER.index(z); fr=FRAMING_OF[z]
def load(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16) if os.path.exists(p) else None
fv=load(f'{R}/png/zl_zm_svg/{key}/{step:02}.png')
panels=[('femtovg',fv)]
for b in ['chr','ff','wk']:
    panels.append((b, load(f'{R}/fresh/refs/{b}_{key}_{fr}.png')))
for e in extra:
    n,p=e.split('=',1); panels.append((n, load(p)))
x,y,w,h=crop
rows=[]
for n,a in panels:
    if a is None: continue
    rows.append((n,a[y:y+h,x:x+w]))
diffs=[]
for n,a in rows[1:]:
    d=np.abs(rows[0][1]-a).max(axis=2)
    img=np.stack([np.clip(d*4,0,255)]*3,-1); img[d>8]=[230,30,30]
    diffs.append(('d_'+n,img))
allp=rows+diffs
cols=len(rows)
W=w*scale; H=h*scale
canvas=Image.new('RGB',(cols*(W+4),2*(H+16)),(40,40,40))
dr=ImageDraw.Draw(canvas)
for i,(n,a) in enumerate(allp):
    r=0 if i<cols else 1; c=i if i<cols else i-cols+1
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).resize((W,H),Image.NEAREST)
    canvas.paste(im,(c*(W+4),r*(H+16)+16)); dr.text((c*(W+4)+2,r*(H+16)+2),n,fill=(255,255,255))
canvas.save(out)
