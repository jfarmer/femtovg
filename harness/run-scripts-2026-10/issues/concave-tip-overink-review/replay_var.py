import re, os, sys, subprocess, numpy as np
src=open('/Users/matt/src/femtovg-wt/da/harness/concave-tip-overink/fringe_model.py').read()
defs=src[:src.index('# Each reduction')].replace("RUN = sys.argv[1] if len(sys.argv) > 1 else '.'","RUN='.'")
ns={}; exec(defs, ns)
CAP=os.path.expanduser('~/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview-verify/tips/cap/target/release/cap')
z2=lambda u,v: np.array([0.390625*u+30,0.390625*v-70])
TIPS=[z2(280,725),z2(744,725)]
wins=[ns['window'](*t) for t in TIPS]
ts=lambda a: sum(a[w].sum() for w in wins)
def cap(d, env):
    out=subprocess.run([CAP,'2',d],capture_output=True,text=True,check=True,env={**os.environ,**env}).stdout.splitlines()
    n=int(out[0].split()[1]); V=np.array([[float(t) for t in l.split()] for l in out[1:1+n]])
    c=[l for l in out[1+n:] if 'ConcaveFill' in l][0]
    dr=[tuple(int(x) for x in t) for t in re.findall(r'fill_verts: Some\(\((\d+), (\d+)\)\), stroke_verts: Some\(\((\d+), (\d+)\)\)',c)]
    return V,dr
for name in sys.argv[1:]:
    d=re.search(r'<path d="([^"]*)"',open(f'/Users/matt/src/femtovg-wt/da/harness/concave-tip-overink/{name}.svg').read()).group(1).replace(',',' ')
    area=ns['load_cov'](f'refs/id_ct__{name}_z2.png'); fv=ns['load_cov'](f'png/red/master_{name}_z2.png')
    for label,env in (('as built',{}),('FV_NO_INNERBEVEL',{'FV_NO_INNERBEVEL':'1'})):
        V,dr=cap(d,env); st=ns['stencil'](V,dr); lay=ns['strip_layers'](V,dr,st); cov=ns['compose'](lay,st)
        print(f'{name:12s} {label:18s} maxdiff-to-frame {255*np.abs(cov-fv).max():6.2f}  excess/tip {(ts(cov)-ts(area))/2:+6.2f}  >20 off area in tips {ts(np.abs(cov-area)>20/255):3d}  stencil0 {ts((np.abs(cov-area)>20/255)&(st==0))}')
