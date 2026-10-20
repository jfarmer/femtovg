#!/usr/bin/env python3
"""score.py SCRATCH [regions] : all3 / agreed counts per t__ file, plus per named region (x0,y0,x1,y1 at z2)"""
import sys, glob, os, json, numpy as np
from PIL import Image
S=sys.argv[1]
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
REG={'left':(90,80,140,260),'right':(290,100,360,260),'chin':(140,215,300,260),'top':(140,0,330,80)}
for f in json.load(open(f'{S}/files.json')):
    k=f['key']
    try:
        o=L(f'{S}/png/mst2_{k}_z2.png'); refs=[L(f'{S}/refs/{x}_{k}_z2.png') for x in ('chr','ff','wk')]
    except FileNotFoundError as e:
        print(k,'missing',e); continue
    off=[np.abs(o-r).max(2)>20 for r in refs]
    a=off[0]&off[1]&off[2]
    sp=np.zeros(a.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
    ag=a&~sp
    np.save(f'{S}/all3_{k}.npy',a)
    reg={n:int(a[y0:y1,x0:x1].sum()) for n,(x0,y0,x1,y1) in REG.items()}
    print(f'{k:40s} all3 {int(a.sum()):5d} agreed {int(ag.sum()):5d} vs_chr20 {int(off[0].sum()):5d} spread {int(sp.sum()):5d}', reg)
