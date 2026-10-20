import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
R='/Users/matt/src/femtovg-wt/runs/zoom/fresh/refs/'
K='corpus__babylon__vertex-pulling-normals-uvs-colors-tangents__1'
L=lambda p: np.asarray(Image.open(p).convert('RGB')).astype(int)
try:
    FONT=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 13)
except Exception:
    FONT=ImageFont.load_default()
def diffpanel(a, r):
    d=np.abs(a-r).max(2)
    g=(r.mean(2)*0.25+190).clip(0,255)
    out=np.stack([g,g,g],2)
    out[d>8]=[220,30,30]
    return out.astype(np.uint8), int((d>8).sum())
def panel_row(frames, labels, ref, refname, crop=None, scale=1):
    rows=[]
    for a,lab in zip(frames, labels):
        dp,n=diffpanel(a, ref)
        imgs=[a.astype(np.uint8), ref.astype(np.uint8), dp]
        caps=[lab, refname, f'vs {refname}: {n} px > 8/255 (whole frame)']
        if crop:
            x0,y0,x1,y1=crop; imgs=[i[y0:y1,x0:x1] for i in imgs]
        ims=[Image.fromarray(i).resize((i.shape[1]*scale, i.shape[0]*scale), Image.NEAREST) for i in imgs]
        w,h=ims[0].size
        canvas=Image.new('RGB',(3*w+20, h+22),(255,255,255))
        dr=ImageDraw.Draw(canvas)
        for k,(im,c) in enumerate(zip(ims,caps)):
            canvas.paste(im,(k*(w+10),22)); dr.text((k*(w+10)+2,3),c,fill=(0,0,0),font=FONT)
        rows.append(canvas)
    return rows
def save(rows, name, ms):
    rows[0].save(f'strips/{name}.gif', save_all=True, append_images=rows[1:], duration=ms, loop=0)
    rows[0].save(f'strips/{name}.webp', save_all=True, append_images=rows[1:], duration=ms, loop=0, lossless=True)
    rows[0].save(f'strips/{name}_first.png'); rows[-1].save(f'strips/{name}_last.png')
if __name__=='__main__':
    # zoom 2: frame 00 and 01 of a still scene
    ref=L(f'{R}chr_{K}_z2.png')
    fr=[L('conv/z2.ppm.00.ppm'), L('conv/z2.ppm.01.ppm')]
    save(panel_row(fr, ['master frame 00 (zoom 2)', 'master frame 01 (same scene)'], ref, 'Chromium'), 'babylon_vp1_z2_still', 900)
    # zoom 1.25: frames 0, 8, ..., 64
    ref=L(f'{R}chr_{K}_z125.png')
    idx=list(range(0,65,8))
    fr=[L(f'conv/z1.25.ppm.{i:02d}.ppm') for i in idx]
    save(panel_row(fr, [f'master frame {i:02d} (zoom 1.25)' for i in idx], ref, 'Chromium'), 'babylon_vp1_z125_converge', 500)
