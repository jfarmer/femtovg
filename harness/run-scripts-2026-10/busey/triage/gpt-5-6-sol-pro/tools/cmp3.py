#!/usr/bin/env python3
"""cmp3.py FRAME.png REFDIR KEY : px off all three browsers (>20) and per-region counts"""
import sys, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
o=L(sys.argv[1]); d,k=sys.argv[2],sys.argv[3]
refs=[L(f'{d}/{x}_{k}_z2.png') for x in ('chr','ff','wk')]
off=[np.abs(o-r).max(2)>20 for r in refs]; a=off[0]&off[1]&off[2]
REG={'left':(90,80,140,260),'right':(290,100,360,260),'chin':(140,215,300,260),'top':(140,0,330,80)}
print(sys.argv[1].split('/')[-1], 'all3', int(a.sum()), 'vs_chr20', int(off[0].sum()), {n:int(a[y0:y1,x0:x1].sum()) for n,(x0,y0,x1,y1) in REG.items()})
if len(sys.argv)>4: np.save(sys.argv[4], a)
