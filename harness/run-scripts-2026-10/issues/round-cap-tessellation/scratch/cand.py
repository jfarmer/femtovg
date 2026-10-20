import sys, numpy as np
from PIL import Image, ImageDraw
L=lambda p: np.asarray(Image.open(p).convert('RGB'),np.int16)
def heat(a,b):
    d=np.abs(a-b).max(2); h=np.full(d.shape+(3,),255,np.uint8); h[d>8]=[255,160,0]; h[d>20]=[255,0,0]; return h
rows=[]
for spec in sys.argv[2:]:
    key,fr,x,y,w,z=spec.split(':'); x,y,w,z=int(x),int(y),int(w),int(z)
    k=key if key.startswith('red__') else f'corpus__buseybench__{key}'
    b=L(f'png/mstc_{k}_{fr}.png'); a=L(f'png/caps_{k}_{fr}.png'); c=L(f'refs/chr_{k}_{fr}.png'); i=L(f'refs/id_{k}_{fr}.png')
    ps=[b,a,c,i,heat(b,c),heat(a,c),heat(b,i),heat(a,i)]
    tiles=[Image.fromarray(p[y:y+w,x:x+w].astype(np.uint8)).resize((w*z,w*z),Image.NEAREST) for p in ps]
    row=Image.new('RGB',(sum(t.width+6 for t in tiles),tiles[0].height+6),'gray')
    xx=0
    for t in tiles: row.paste(t,(xx,3)); xx+=t.width+6
    rows.append(row)
H=sum(r.height for r in rows); W=max(r.width for r in rows)
out=Image.new('RGB',(W,H),'gray'); yy=0
for r in rows: out.paste(r,(0,yy)); yy+=r.height
out.save(sys.argv[1]); print(out.size)
