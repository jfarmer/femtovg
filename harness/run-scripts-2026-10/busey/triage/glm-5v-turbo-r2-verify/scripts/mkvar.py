import re, json, os
S='/Users/matt/src/femtovg-wt/runs/busey/triage/glm-5v-turbo-r2-verify'
src=open(f'{S}/svg/g00_orig.svg').read()
def drop(*subs, text=None):
    t=text if text is not None else src
    out=[l for l in t.split('\n') if not any(s in l for s in subs)]
    assert len(out)==len(t.split('\n'))-len(subs), subs
    return '\n'.join(out)
def rep(a,b,text=None):
    t=text if text is not None else src
    assert t.count(a)>=1, a
    return t.replace(a,b)
V={}
V['v01_sideburns_off']=drop('M 235,385 C','M 789,395 C')
V['v02_sliverR_off']=drop('M 815,525 C')
V['v03_mouthUp_off']=drop('M 425,638 Q','M 432,642 Q','M 438,644 Q')
V['v03b_mouthLo_off']=drop('M 446,680 Q','M 454,696 Q','M 422,678 Q','M 438,684 Q')
V['v04_stubble_nofilter']=rep('fill="#ddb89e" filter="url(#stubbleFilter)"','fill="#ddb89e"')
V['v04b_stubble_off']=drop('M 310,560 Q 412,890')
V['v05_lashes_off']=drop('M 324,419 Q 330,408','M 604,419 Q 610,408')
V['v05b_lashes_butt']=rep('stroke="#1a0f0a" stroke-width="2.5" stroke-linecap="round"','stroke="#1a0f0a" stroke-width="2.5" stroke-linecap="butt"')
# iris detail: the two lobes as separate path elements (left eye only; right eye too for symmetry check)
lensL='M 362,426 A 20.8086520466 20.8086520466 0 0 0 362,450 Z'
cresL='M 362,426 A 17 17 0 0 1 396,426 A 20.8086520466 20.8086520466 0 0 0 362,426 Z'
t=rep('<path d="M 362,426 A 15 15 0 0 1 396,426 A 18 18 0 0 0 362,450 Z" fill="#6a8bae" opacity="0.5"/>',
      f'<path d="{lensL}" fill="#6a8bae" opacity="0.5"/><path d="{cresL}" fill="#6a8bae" opacity="0.5"/>')
V['v06_irisL_split']=t
V['v06b_iris_off']=drop('M 362,426 A 15','M 632,426 A 15')
# ears: last cubic without the hairpin past the start point
t=rep('C 260,460 242,465 252,465 Z','C 264,466 258,465 252,465 Z')
t=rep('C 764,460 782,465 772,465 Z','C 760,466 766,465 772,465 Z',text=t)
V['v07_ears_nocusp']=t
V['v08_face_noshadow']=rep('fill="url(#skinGrad)" filter="url(#shadow)"/>','fill="url(#skinGrad)"/>')
V['v09_eyebrows_off']=drop('M 288,362 C','M 298,370 C','M 736,362 C','M 726,370 C')
# every filter attribute removed
V['v10_nofilters']=re.sub(r'\s*filter="url\(#[A-Za-z]+\)"','',src)
files=[{'path':f'{S}/svg/g00_orig.svg','key':'t__g00_orig','group':'t'}]
for k,t in V.items():
    p=f'{S}/svg/{k}.svg'; open(p,'w').write(t)
    files.append({'path':p,'key':f't__{k}','group':'t'})
json.dump(files,open(f'{S}/files.json','w'),indent=0)
for k,t in V.items(): print(k, len(src)-len(t))
