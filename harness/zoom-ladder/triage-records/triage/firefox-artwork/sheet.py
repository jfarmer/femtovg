# sheet.py OUT crop scale name=path ... : panels in a row, then diffs of each vs the LAST panel (the reference)
import sys, numpy as np
from PIL import Image, ImageDraw
out=sys.argv[1]; x,y,w,h=map(int,sys.argv[2].split(',')); s=int(sys.argv[3])
P=[(a.split('=',1)[0],np.asarray(Image.open(a.split('=',1)[1]).convert('RGB'),dtype=np.int16)[y:y+h,x:x+w]) for a in sys.argv[4:]]
ref=P[-1][1]
W,H=w*s,h*s
c=Image.new('RGB',(len(P)*(W+4),2*(H+16)),(40,40,40)); dr=ImageDraw.Draw(c)
for i,(n,a) in enumerate(P):
    c.paste(Image.fromarray(a.astype(np.uint8)).resize((W,H),Image.NEAREST),(i*(W+4),16)); dr.text((i*(W+4)+2,2),n,fill=(255,255,255))
    if i<len(P)-1:
        sd=(a.astype(int)-ref).mean(axis=2)  # >0: lighter than ref (less ink)
        m=np.abs(a.astype(int)-ref).max(axis=2)
        img=np.zeros(a.shape,np.uint8)+20
        img[...,0]=np.clip(-sd*6,0,255)+20  # more ink: red
        img[...,2]=np.clip(sd*6,0,255)+20   # less ink: blue
        img[m>8]=np.where((sd[m>8]<0)[:,None],[255,60,60],[80,140,255])
        c.paste(Image.fromarray(img.astype(np.uint8)).resize((W,H),Image.NEAREST),(i*(W+4),H+32)); dr.text((i*(W+4)+2,H+18),f'{n} - {P[-1][0]}: >8 {int((m>8).sum())} (red=more ink)',fill=(255,255,255))
c.save(out)
