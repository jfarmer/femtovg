import sys, numpy as np
from PIL import Image, ImageDraw
from cmp import *
def panel(key, fr, area, crop, scale, out, extra=()):
    F=frames(key,fr); 
    ims=[('femtovg',F['fv']),('chr',F['chr']),('ff',F['ff']),('wk',F['wk'])]
    if area: ims.append(('area 8x',load(area)))
    for n,p in extra: ims.append((n,load(p)))
    x,y,w,h=crop
    tiles=[]
    for n,a in ims:
        if a is None: continue
        t=Image.fromarray(a[y:y+h,x:x+w,:3].astype(np.uint8)).resize((w*scale,h*scale),Image.NEAREST)
        c=Image.new('RGB',(w*scale,h*scale+14),'white'); c.paste(t,(0,14)); ImageDraw.Draw(c).text((2,1),n,fill='black'); tiles.append(c)
    W=sum(t.width+4 for t in tiles); H=max(t.height for t in tiles)
    o=Image.new('RGB',(W,H),'white'); xx=0
    for t in tiles: o.paste(t,(xx,0)); xx+=t.width+4
    o.save(out)
if __name__=='__main__':
    key,fr,area,crop,scale,out=sys.argv[1:7]
    panel(key,fr,area if area!='-' else None,tuple(map(int,crop.split(','))),int(scale),out)
