import sys, numpy as np
from PIL import Image
# crop.py out.png x0 y0 x1 y1 scale img...
out, x0, y0, x1, y1, s = sys.argv[1], *map(int, sys.argv[2:7])
ims = [Image.open(p).convert('RGB').crop((x0, y0, x1, y1)) for p in sys.argv[7:]]
ims = [i.resize(((x1-x0)*s, (y1-y0)*s), Image.NEAREST) for i in ims]
W = sum(i.width for i in ims) + 4*(len(ims)-1)
sheet = Image.new('RGB', (W, ims[0].height), 'white')
x = 0
for i in ims: sheet.paste(i, (x, 0)); x += i.width + 4
sheet.save(out)
