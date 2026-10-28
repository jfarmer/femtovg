import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom/fresh/refs/')
K='corpus__wpt__tests__mask-on-thin-stroked-path-userspaceonuse'
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',14)
def ld(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)
def diff(a,r):
    d=np.abs(a-r).max(-1); o=np.full(a.shape,255,np.uint8)
    o[(d>8)&(d<=20)]=[255,160,0]; o[d>20]=[220,30,30]; return o,int((d>8).sum())
rows=[
 ('zoom 3, whole frame: the stroke whose centerline is off the canvas', 'all/master_%s_z3.ppm'%K, 'all/cull_%s_z3.ppm'%K, R+'chr_%s_z3.png'%K, 'master','stroke cull by its outline', None, 1),
 ('zoom 1.25, left butt end (x 150-190, y 50-85): two contours\' fringes meet', 'all/master_%s_z125.ppm'%K, 'all/aa1_%s_z125.ppm'%K, R+'chr_%s_z125.png'%K, 'master','AA pass marks the stencil (proof only)', (150,50,40,35), 8),
 ('repro, zoom 1: one stroke, two contours abutting at x=100.5 (crop x 215-245, y 65-95)', 'repro/master_fringe-abutting.ppm','repro/aa1_fringe-abutting.ppm','repro/chr_fringe-abutting.png','master','AA pass marks the stencil (proof only)',(215,65,30,30),8),
]
tiles=[]
W=0
for cap,b,a,r,lb,la,box,z in rows:
    B,A,C=ld(b),ld(a),ld(r)
    db,nb=diff(B,C); da,na=diff(A,C)
    ims=[B.astype(np.uint8),A.astype(np.uint8),C.astype(np.uint8),db,da]
    labs=[lb,la,'Chromium 131',f'{lb} vs Chromium: {nb} px > 8/255',f'after vs Chromium: {na} px']
    out=[]
    for im in ims:
        if box: x,y,w,h=box; im=im[y:y+h,x:x+w]
        p=Image.fromarray(im); p=p.resize((p.width*z,p.height*z),Image.NEAREST) if z>1 else p
        out.append(p)
    tiles.append((cap,out,labs))
pad=8; top=22; lab=20
width=max(sum(p.width for p in o)+pad*(len(o)+1) for _,o,_ in tiles)
height=sum(top+lab+max(p.height for p in o)+pad for _,o,_ in tiles)+pad
S=Image.new('RGB',(width,height),(40,40,40)); d=ImageDraw.Draw(S); y=pad
for cap,o,labs in tiles:
    d.text((pad,y),cap,fill=(255,255,255),font=font); y+=top
    x=pad
    for p,l in zip(o,labs):
        d.text((x,y),l,fill=(220,220,220),font=font); S.paste(p,(x,y+lab)); x+=p.width+pad
    y+=lab+max(p.height for p in o)+pad
S.save(sys.argv[1]); print(S.size)
