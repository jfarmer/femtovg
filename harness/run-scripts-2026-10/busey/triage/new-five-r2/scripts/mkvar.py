"""mkvar.py: build edited variants and reductions into svg/ and register them in files.json."""
import json, os, re
S='/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2'
C='/Users/matt/src/femtovg-wt/da/corpus/buseybench'
DEFS_END={'claude-opus-5-5':202,'claude-sonnet-5-5':154,'gpt-6-1-sol':256,'gpt-6-1-sol-pro':226,'pareto':99}
def lines(n): return open(f'{C}/{n}.svg').read().split('\n')
def rng(spec):
    out=set()
    for part in str(spec).split(','):
        if '-' in part: a,b=map(int,part.split('-')); out|=set(range(a,b+1))
        else: out.add(int(part))
    return out
def edit(n, dels=(), subs=()):
    ls=lines(n); d=set()
    for s in dels: d|=rng(s)
    for (ln,old,new) in subs:
        assert old in ls[ln-1], (n,ln,old); ls[ln-1]=ls[ln-1].replace(old,new)
    return '\n'.join(l for i,l in enumerate(ls,1) if i not in d)
def reduce(n, body, bg):
    ls=lines(n); head='\n'.join(ls[:DEFS_END[n]])
    return head+f'\n  <rect width="1024" height="1024" fill="{bg}"/>\n'+body+'\n</svg>\n'
def pick(n, spec):
    ls=lines(n); return '\n'.join(ls[i-1] for i in sorted(rng(spec)))
V={}
o='claude-opus-5-5'
V['o01_no_lowerlip']=edit(o,dels=['381'])
V['o02_no_upperlip']=edit(o,dels=['379'])
V['o03_no_lips']=edit(o,dels=['379','381'])
V['o04_dash_solid']=edit(o,subs=[(229,' stroke-dasharray="5 4"',''),(230,' stroke-dasharray="5 4"','')])
V['o05_strands_butt']=edit(o,subs=[(270,'stroke-linecap="round"','stroke-linecap="butt"')])
V['o06_no_lashes']=edit(o,dels=['167-174'])
V['o_r1_lowerlip']=reduce(o,pick(o,'381'),'#c98a6c')
V['o_r2_dash']=reduce(o,pick(o,'229'),'#2c4560')
V['o_r2b_solid']=reduce(o,pick(o,'229').replace(' stroke-dasharray="5 4"',''),'#2c4560')
V['o_r3_strand_round']=reduce(o,'<g fill="none" stroke-linecap="round">'+pick(o,'287-291')+'</g>','#3a5a70')
V['o_r3b_strand_butt']=reduce(o,'<g fill="none" stroke-linecap="butt">'+pick(o,'287-291')+'</g>','#3a5a70')
V['o_r4_lashes']=reduce(o,pick(o,'167-174'),'#d79a78')
s='claude-sonnet-5-5'
V['s01_no_stubble']=edit(s,dels=['268-270'])
V['s02_no_skinnoise']=edit(s,dels=['246'])
V['s03_no_turbulence']=edit(s,dels=['246','268-270'])
V['s_r1_stub']=reduce(s,'<rect x="250" y="560" width="520" height="320" filter="url(#stubble)"/>','#c88c6c')
V['s_r2_stub_shift_z2half']=reduce(s,'<g transform="translate(1.28 1.28)"><rect x="250" y="560" width="520" height="320" filter="url(#stubble)"/></g>','#c88c6c')
g='gpt-6-1-sol'
V['g01_no_nostril']=edit(g,dels=['516'])
V['g02_no_mouthcorners']=edit(g,dels=['621','622'])
V['g03_no_hairgold']=edit(g,dels=['336'])
p='gpt-6-1-sol-pro'
V['p01_no_locks']=edit(p,dels=['615','618','619'])
V['p_r1_locks']=reduce(p,pick(p,'615,618,619'),'#5a5040')
q='pareto'
V['q01_no_L284']=edit(q,dels=['284'])
V['q02_no_L145_L151']=edit(q,dels=['145','151'])
V['q_r1_hair']=reduce(q,pick(q,'269'),'#24344a')
# synthetic: straight-sided spikes, tip angles 20..90 deg, as a convex triangle row and as a concave sawtooth; white on navy
def tri(cx,base_y,h,ang):
    import math
    hw=h*math.tan(math.radians(ang/2)); return (cx,base_y-h),(cx+hw,base_y),(cx-hw,base_y)
import math
body=[]; saw=[]; x=150
for ang in (20,30,45,62,90):
    a,b,c=tri(x,420,60,ang); body.append(f'<path d="M{a[0]:.2f} {a[1]:.2f} L{b[0]:.2f} {b[1]:.2f} L{c[0]:.2f} {c[1]:.2f} Z" fill="#e8d6a8"/>')
    x+=150
# sawtooth: one concave polygon with 5 spikes of the same angles, base at y=700
pts=[]; x=150
for ang in (20,30,45,62,90):
    hw=60*math.tan(math.radians(ang/2)); pts+= [(x-hw,700),(x,640),(x+hw,700)]; x+=150
d='M'+' L'.join(f'{px:.2f} {py:.2f}' for px,py in pts)+' L'+f'{pts[-1][0]:.2f} 760 L{pts[0][0]:.2f} 760 Z'
body.append(f'<path d="{d}" fill="#e8d6a8"/>')
V['q_r2_spikes']=reduce(q,'\n'.join(body),'#24344a')
os.makedirs(f'{S}/svg',exist_ok=True)
files=[]
for n in ['claude-opus-5-5','claude-sonnet-5-5','gpt-6-1-sol','gpt-6-1-sol-pro','pareto']:
    tag={'claude-opus-5-5':'o','claude-sonnet-5-5':'s','gpt-6-1-sol':'g','gpt-6-1-sol-pro':'p','pareto':'q'}[n]
    open(f'{S}/svg/{tag}00_orig.svg','w').write(open(f'{C}/{n}.svg').read())
    files.append({'path':f'{S}/svg/{tag}00_orig.svg','key':f't__{tag}00_orig','group':'t'})
for k,v in V.items():
    open(f'{S}/svg/{k}.svg','w').write(v)
    files.append({'path':f'{S}/svg/{k}.svg','key':f't__{k}','group':'t'})
json.dump(files,open(f'{S}/files.json','w'))
print(len(files),'files')
