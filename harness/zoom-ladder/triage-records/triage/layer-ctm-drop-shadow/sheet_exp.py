import numpy as np
from PIL import Image, ImageDraw, ImageFont
E='exp'; z='1.25'
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
rows=[('v0_orig','original: rotate(90), user origin at (142.5,117.5) px'),
      ('v2_norotate','rotation folded into the coordinates (CTM scale+translate)'),
      ('v3_intorigin','rotate(90) kept, user origin moved to (143,118) px'),
      ('v1_nofilter','no filter')]
cols=['fem','area','chr','ff','wk']
names={'fem':'femtovg master','area':'area (Chromium 8x, box-down)','chr':'Chromium 131','ff':'Firefox 159b','wk':'WebKit (macOS)'}
x,y,w,h=222,120,56,20; s=6
def ld(v,c):
    if c=='area':
        a=np.asarray(Image.open(f'{E}/area8_{v}_{z}.png').convert('RGB')).astype(float)[:2080,:3680]
        return a.reshape(260,8,460,8,3).mean((1,3))
    p=f'{E}/fem_{v}_{z}.ppm' if c=='fem' else f'{E}/{c}_{v}_{z}.png'
    return np.asarray(Image.open(p).convert('RGB').crop((0,0,460,260))).astype(float)
pad,top,lab=8,30,22
W=len(cols)*(w*s+pad)+pad; H=top+len(rows)*(h*s+lab+pad)+pad
out=Image.new('RGB',(W,H),(40,40,40)); d=ImageDraw.Draw(out)
d.text((pad,6),f'wpt-2d-layer-ctm-drop-shadow-filter at zoom 1.25, crop x {x}-{x+w}, y {y}-{y+h}, 6x nearest: px > 8/255 off the area reference',fill=(255,255,255),font=font)
for r,(v,desc) in enumerate(rows):
    A=ld(v,'area')
    oy=top+r*(h*s+lab+pad)
    d.text((pad,oy),desc,fill=(255,220,120),font=font)
    for c_i,c in enumerate(cols):
        a=ld(v,c)
        n=int((np.abs(a-A).max(-1)>8).sum())
        im=Image.fromarray(np.clip(a[y:y+h,x:x+w],0,255).astype(np.uint8)).resize((w*s,h*s),Image.NEAREST)
        ox=pad+c_i*(w*s+pad)
        out.paste(im,(ox,oy+lab))
        t=names[c] if c=='area' else f'{names[c]}: {n} px'
        d.text((ox+4,oy+lab+h*s-18),t,fill=(200,0,0),font=font)
out.save('evidence_variants_z125.png')
print(out.size)
