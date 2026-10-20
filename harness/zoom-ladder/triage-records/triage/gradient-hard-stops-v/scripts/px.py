import sys
from PIL import Image
# usage: px.py row x0 x1 img...
row=int(sys.argv[1]); x0=int(sys.argv[2]); x1=int(sys.argv[3])
for p in sys.argv[4:]:
    im=Image.open(p).convert('RGB')
    print(p.split('/')[-1][-40:], [im.getpixel((x,row)) for x in range(x0,x1+1)])
