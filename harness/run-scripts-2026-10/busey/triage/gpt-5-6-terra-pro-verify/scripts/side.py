import sys, os, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0,'/Users/matt/src/femtovg-wt/da/harness/corpus_run')
from common import FRAMINGS, SWEEP_ENV
V='/Users/matt/src/femtovg-wt/runs/busey/triage/gpt-5-6-terra-pro-verify'
R='/Users/matt/src/femtovg-wt/runs/busey'
BIN='/Users/matt/src/femtovg-wt/bin/_logos_full_mst2'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
for n in sys.argv[1:]:
    key=f'corpus__buseybench__{n}'
    refs=[L(f'{R}/refs/{b}_{key}_z2.png') for b in ('chr','ff','wk')]
    out=[]
    for single in (True,False):
        fr,z=FRAMINGS['z2']; env={**os.environ,**fr,**SWEEP_ENV}
        if single: env['SINGLE_SHADOW_LAYER']='1'
        p=f'{V}/r/side_{n}_{int(single)}.ppm'
        subprocess.run([BIN,f'{z:g}',p,f'/Users/matt/src/femtovg-wt/da/corpus/buseybench/{n}.svg'],env=env,capture_output=True,check=True)
        img=L(p); os.remove(p)
        red=np.logical_and.reduce([np.abs(img-r).max(axis=2)>20 for r in refs])
        out.append(int(red.sum()))
    print(n,'single',out[0],'merge',out[1])
