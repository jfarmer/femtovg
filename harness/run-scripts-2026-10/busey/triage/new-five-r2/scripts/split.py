import sys, numpy as np
sys.path.insert(0,'scripts'); import off3
from off3 import masks
tot={}
for fr in ['z2','hd']:
  for n in ['claude-opus-5-5','claude-sonnet-5-5','gpt-6-1-sol','gpt-6-1-sol-pro','pareto']:
    k='corpus__buseybench__'+n
    off3.fr=fr; off3.b='mst4'; off3.pd='png'
    o,refs,a3,sp,oi=masks(k)
    off3.b='fm'; _,_,f3,_,_=masks(k)
    r=dict(all3=int(a3.sum()), area_ok=int((a3&~oi).sum()), fm_fixed=int((a3&oi&~f3).sum()), fm_left=int((a3&oi&f3).sum()), spread=int((a3&sp).sum()))
    print(fr, f'{n:20s}', r)
