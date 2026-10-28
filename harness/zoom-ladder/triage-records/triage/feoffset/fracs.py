import json, re, glob, os
D='/Users/matt/src/femtovg-wt/da/corpus/wpt-feoffset-reftests/'
over = {  # root-unit device offsets per chain step, where units/transforms scale them
 'offset-primitive-units-non-square':[(30,30)], 'offset-primitive-units-objectboundingbox-25':[(25,25)],
 'offset-primitive-units-objectboundingbox-50':[(40,40)], 'offset-primitive-units-objectboundingbox-negative':[(-20,-30)],
 'offset-with-element-transform-scale':[(20,20)], 'offset-with-parent-transform-scale':[(22.5,22.5)],
}
def shifts(name):
    if name in over: return over[name]
    t=open(D+name+'.svg').read()
    out=[]
    for m in re.finditer(r'<feOffset([^>]*)/>', t):
        a=m.group(1)
        dx=re.search(r'dx="([-\d.]+)"',a); dy=re.search(r'dy="([-\d.]+)"',a)
        out.append((float(dx.group(1)) if dx else 0.0, float(dy.group(1)) if dy else 0.0))
    return out
L={}
for line in open('/Users/matt/src/femtovg-wt/runs/zoom/zoomcmp_zm_svg.jsonl'):
    r=json.loads(line)
    if r['key'].startswith('corpus__wpt-feoffset-reftests__'): L[r['key'].split('__')[-1]]=r
clus=set(v['key'].split('__')[-1] for v in json.load(open('../clusters_compact.json'))['feoffset'])
def frac(v): return abs(v-round(v))
tab=[]
for name,r in sorted(L.items()):
    if name.endswith('-ref'): continue
    sh=shifts(name)
    seen={}
    for s in r['steps']:
        z=s['zoom']
        if z in seen: continue
        best=min(s[b]['n8'] for b in ('chr','ff','wk') if b in s)
        f=max([frac(dx*z) for dx,dy in sh]+[frac(dy*z) for dx,dy in sh]) if sh else 0
        seen[z]=(best,round(f,3))
    tab.append((name,sh,seen))
    fails_int=[z for z,(b,f) in seen.items() if b>24 and f<1e-3]
    fails_frac=[z for z,(b,f) in seen.items() if b>24 and f>=1e-3]
    pass_frac=[z for z,(b,f) in seen.items() if b<=24 and f>=1e-3]
    print(f"{name:52s} {'C' if name in clus else ' '} shifts={sh} fail@int={fails_int} fail@frac={fails_frac} pass@frac={pass_frac}")
