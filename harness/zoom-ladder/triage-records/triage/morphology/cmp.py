import sys
from PIL import Image
import numpy as np
def L(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)
def n(a,b): return int((np.abs(a-b).max(-1)>8).sum())
R='/Users/matt/src/femtovg-wt/runs/zoom'
fr={'0.75':'z075','1.25':'z125','1.75':'z175'}
for ax in ['horizontal','vertical']:
  key=f'corpus__wpt-femorphology-reftests__morphology-dilate-{ax}-only'
  for z in ['0.75','1.25','1.75']:
    c0=L(f'{R}/fresh/refs/chr_{key}_{fr[z]}.png')
    row=[]
    m={r:L(f'out/mst_dil-{ax}-r{r}_{z}.ppm') for r in ['0','1','0p0001']}
    c={r:L(f'out/chr_dil-{ax}-r{r}_{z}.png') for r in ['0','1','0p0001']}
    ladder=L(f'{R}/png/zl_zm_svg/{key}/fresh_{fr[z]}.png')
    print(ax,z,
      'fv(0)=ladder:',n(m['0'],ladder),
      '| chr(0) here vs stored:',n(c['0'],c0),
      '| fv(0) vs chr(0):',n(m['0'],c['0']),
      '| fv(0) == fv(1):', bool((m['0']==m['1']).all()),
      '| fv(1) vs chr(1):',n(m['1'],c['1']),
      '| fv(1e-4) vs chr(0):',n(m['0p0001'],c['0']),
      '| chr(1e-4) vs chr(0):',n(c['0p0001'],c['0']),
      '| chr(1) vs chr(0):',n(c['1'],c['0']))
