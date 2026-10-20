import sys, os, subprocess, json
import numpy as np
from PIL import Image
V='/Users/matt/src/femtovg-wt/runs/busey/triage/gpt-5-6-terra-pro-verify'
sys.path.insert(0,'/Users/matt/src/femtovg-wt/da/harness/corpus_run')
from common import FRAMINGS, SWEEP_ENV
BIN='/Users/matt/src/femtovg-wt/bin/_logos_full_mst2'
def load(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def render(name, single, extra={}):
    fr,z=FRAMINGS['z2']
    env={**os.environ,**fr,**SWEEP_ENV,**extra}
    if single: env['SINGLE_SHADOW_LAYER']='1'
    else: env.pop('SINGLE_SHADOW_LAYER',None)
    out=f'{V}/r/{name}_{"s" if single else "m"}.ppm'
    r=subprocess.run([BIN,f'{z:g}',out,f'{V}/svg/{name}.svg'],env=env,capture_output=True,text=True)
    assert r.returncode==0, r.stderr[-300:]
    png=out[:-4]+'.png'; Image.open(out).save(png); os.remove(out)
    return load(png)
def red(img,name):
    refs=[load(f'{V}/refs/{b}_t__{name}_z2.png') for b in ('chr','ff','wk')]
    off=[np.abs(img-r).max(axis=2)>20 for r in refs]
    return off[0]&off[1]&off[2], off[0]
names=sys.argv[1:] or ['orig','min_lin','min_black','min_pre','min_srgbfilter','min_mid','min_midpre']
for n in names:
    s=render(n,True); m=render(n,False)
    rs,cs=red(s,n); rm,cm=red(m,n)
    print(f'{n:16s} single: red3={rs.sum():5d} chr={cs.sum():5d} | merge: red3={rm.sum():5d} chr={cm.sum():5d}')
