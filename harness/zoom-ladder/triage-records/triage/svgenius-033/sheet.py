import numpy as np, os
from PIL import Image, ImageDraw, ImageFont
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
K1="svgenius__page_70_像素鞋子图标_40194_icon_17"; K2="svgenius__page_275_化妆品装饰_25821_icon_24"
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',13)
def L(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def dimg(a,b):
    d=np.abs(a-b).max(-1); img=np.stack([np.clip(d*4,0,255)]*3,-1); img[d>8]=[230,30,30]; return img,int((d>8).sum())
rows=[
 ('shoe, zoom 0.33 (ladder step 16)', 'p_shoe_033_base.png','p_shoe_033_gate.png','p_shoe_033_force.png',f'{H}/fresh/refs/chr_{K1}_z033.png',f'{H}/fresh/refs/wk_{K1}_z033.png',(194,112,72,36),5),
 ('makeup, zoom 0.33 (ladder step 16)', 'p_makeup_033_base.png','p_makeup_033_gate.png','p_makeup_033_force.png',f'{H}/fresh/refs/chr_{K2}_z033.png',f'{H}/fresh/refs/wk_{K2}_z033.png',(194,94,72,72),4),
 ('shoe, zoom 1.1 (off the ladder: shared edges off the pixel grid, squares 8.8 px)', 'p_shoe_11_base.png','p_shoe_11_gate.png','p_shoe_11_force.png','chr_shoe_11.png','wk_shoe_11.png',(150,150,90,40),4),
 ('repro.svg, zoom 1: A one 1.2 px bar | B two in one path | C ring, 1.2 px wall | D 8 squares in one path | E one rect', 'repro_base.png','repro_gate.png','repro_force.png','repro_chr.png','repro_wk.png',(140,44,100,140),2),
]
cols=['master 06243b80','gate fix (multi-contour = concave)','every fill through a mask','Chromium 131','WebKit (macOS)','master vs WebKit','gate fix vs WebKit']
tiles=[]
for title,b,g,f,c,w,(x,y,ww,hh),s in rows:
    B,G,F,C,W=[L(p) for p in (b,g,f,c,w)]
    db,nb=dimg(B,W); dg,ng=dimg(G,W)
    ims=[B,G,F,C,W,db,dg]
    labs=cols[:5]+[f'master vs WebKit: {nb} px',f'gate fix vs WebKit: {ng} px']
    cut=[Image.fromarray(np.clip(a[y:y+hh,x:x+ww],0,255).astype(np.uint8)).resize((ww*s,hh*s),Image.NEAREST) for a in ims]
    tiles.append((title,labs,cut))
pad=8
W=max(sum(im.width+pad for im in cut)+pad for _,_,cut in tiles)
Ht=sum(cut[0].height+44+pad for _,_,cut in tiles)+pad
sheet=Image.new('RGB',(W,Ht),(40,40,40)); d=ImageDraw.Draw(sheet); yy=pad
for title,labs,cut in tiles:
    d.text((pad,yy),title,fill=(255,255,255),font=font); xx=pad
    for lab,im in zip(labs,cut):
        d.text((xx,yy+20),lab,fill=(220,220,220),font=font); sheet.paste(im,(xx,yy+40)); xx+=im.width+pad
    yy+=cut[0].height+44+pad
sheet.save('sheet_svgenius033.png'); print(sheet.size)
