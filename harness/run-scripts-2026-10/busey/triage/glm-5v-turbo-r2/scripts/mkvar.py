import re, json, os
S='/Users/matt/src/femtovg-wt/runs/busey/triage/glm-5v-turbo-r2'
src=open(f'{S}/svg/g00_orig.svg').read()
lines=src.split('\n')
def drop(*subs, text=None):
    t=text if text is not None else src
    out=[]
    for l in t.split('\n'):
        if any(s in l for s in subs): continue
        out.append(l)
    return '\n'.join(out)
def rep(a,b,text=None,count=1):
    t=text if text is not None else src
    assert a in t, a
    return t.replace(a,b,count)
V={}
V['e01_no_irisdetail']=drop('M 362,426 A 15','M 632,426 A 15')
V['e02_no_hairbreak']=drop('M 215,355 C','M 815,525 C','M 455,38 C')
V['e03_no_sideburns']=drop('M 235,385 C','M 789,395 C')
V['e04_no_stubble']=drop('M 310,560 Q 412,890')
V['e04b_stubble_nofilter']=rep('fill="#ddb89e" filter="url(#stubbleFilter)"','fill="#ddb89e"')
V['e05_no_lashes']=drop('M 324,419 Q 330,408','M 604,419 Q 610,408')
V['e06_no_eyebrows']=drop('M 288,362 C','M 298,370 C','M 736,362 C','M 726,370 C')
V['e07_no_ears']=drop('M 252,465 C 218','M 772,465 C 806')
V['e08_face_noshadow']=rep('fill="url(#skinGrad)" filter="url(#shadow)"/>','fill="url(#skinGrad)"/>')
V['e09_no_rim']=drop('M 256,420 C 244,500')
V['e10_no_clipgroup']=re.sub(r'<g clip-path="url\(#faceClip\)">.*?</g>','',src,flags=re.S)
V['e11_no_lidcrease']=drop('M 324,422 Q 372,394','M 604,422 Q 652,394')
# all identified fill-tip and sliver sources removed at once
V['e12_no_mouthfills']=drop('M 425,638 Q 458,615','M 432,642 Q 450,710','M 438,644 Q 465,665','M 446,680 Q 475,702','M 454,696 Q 480,718','M 422,678 Q 458,725','M 438,684 Q 472,708')
files=[]
for k,t in V.items():
    p=f'{S}/svg/{k}.svg'; open(p,'w').write(t)
    files.append({'path':p,'key':f't__{k}','group':'t'})
files.insert(0,{'path':f'{S}/svg/g00_orig.svg','key':'t__g00_orig','group':'t'})
json.dump(files,open(f'{S}/files.json','w'),indent=0)
for k,t in V.items(): print(k, len(src)-len(t))
