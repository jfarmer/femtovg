# cmp.py A B [bbox]: px > 8/255 apart, and the ink difference (sum of darkness of A minus B, in px of full ink)
import sys, numpy as np
from PIL import Image
a=np.asarray(Image.open(sys.argv[1]).convert('RGB'),dtype=np.int32); b=np.asarray(Image.open(sys.argv[2]).convert('RGB'),dtype=np.int32)
if len(sys.argv)>3:
    x0,y0,x1,y1=map(int,sys.argv[3].split(',')); a=a[y0:y1,x0:x1]; b=b[y0:y1,x0:x1]
d=np.abs(a-b).max(axis=2)
ink=((255-a.mean(axis=2))-(255-b.mean(axis=2))).sum()/255
print(f'{sys.argv[1].split("/")[-1]:24s} vs {sys.argv[2].split("/")[-1]:20s} >8: {int((d>8).sum()):4d}  >20: {int((d>20).sum()):4d}  max {d.max():3d}  ink(A-B) {ink:+.2f}')
