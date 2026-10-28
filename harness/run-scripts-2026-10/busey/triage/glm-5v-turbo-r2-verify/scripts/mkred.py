import json
S='/Users/matt/src/femtovg-wt/runs/busey/triage/glm-5v-turbo-r2-verify'
HEAD='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="100%" height="100%">\n'
def svg(body, bg='#ffffff'):
    return HEAD+f'<rect width="1024" height="1024" fill="{bg}"/>\n'+body+'\n</svg>\n'
R={}
iris='M 362,426 A 15 15 0 0 1 396,426 A 18 18 0 0 0 362,450 Z'
lens='M 362,426 A 20.8086520466 20.8086520466 0 0 0 362,450 Z'
cres='M 362,426 A 17 17 0 0 1 396,426 A 20.8086520466 20.8086520466 0 0 0 362,426 Z'
R['r1_iris_orig']=svg(f'<path d="{iris}" fill="#000"/>')
R['r1_iris_split']=svg(f'<path d="{lens}" fill="#000"/><path d="{cres}" fill="#000"/>')
R['r1_iris_lens']=svg(f'<path d="{lens}" fill="#000"/>')
R['r1_iris_cres']=svg(f'<path d="{cres}" fill="#000"/>')
# lens reversed winding (traced the other way) alone: control for orientation
R['r1_iris_lensrev']=svg('<path d="M 362,450 A 20.8086520466 20.8086520466 0 0 1 362,426 Z" fill="#000"/>')
ear='M 252,465 C 218,465 218,535 252,535 C 278,535 285,500 272,478 C 260,460 242,465 252,465 Z'
R['r2_ear']=svg(f'<path d="{ear}" fill="#000"/>')
R['r2_ear_nocusp']=svg(f'<path d="{ear.replace("C 260,460 242,465 252,465","C 264,466 258,465 252,465")}" fill="#000"/>')
lash='M 324,419 Q 330,408 336,419 M 342,414 Q 348,402 354,414 M 364,410 Q 370,398 376,410 M 386,409 Q 392,397 398,409 M 408,412 Q 414,402 420,412 M 426,418 Q 432,408 438,418'
R['r3_lash']=svg(f'<path d="{lash}" stroke="#1a0f0a" stroke-width="2.5" stroke-linecap="round" fill="none"/>', bg='#d6a487')
R['r3_lash_butt']=svg(f'<path d="{lash}" stroke="#1a0f0a" stroke-width="2.5" stroke-linecap="butt" fill="none"/>', bg='#d6a487')
# straight segments with round caps at 8 sub-pixel phases and 4 directions: the cap alone, no curvature
segs=[]
for i in range(8):
    x=320+i*14.13; y=400+i*0.137
    segs.append(f'M {x:.3f},{y:.3f} L {x:.3f},{y+8:.3f}')            # vertical
    segs.append(f'M {x:.3f},{y+20:.3f} L {x+7:.3f},{y+20:.3f}')       # horizontal
    segs.append(f'M {x:.3f},{y+34:.3f} L {x+6:.3f},{y+40:.3f}')       # diagonal
R['r3_caps']=svg(f'<path d="{" ".join(segs)}" stroke="#1a0f0a" stroke-width="2.5" stroke-linecap="round" fill="none"/>', bg='#d6a487')
R['r3_caps_butt']=svg(f'<path d="{" ".join(segs)}" stroke="#1a0f0a" stroke-width="2.5" stroke-linecap="butt" fill="none"/>', bg='#d6a487')
fs=json.load(open(f'{S}/files.json'))
have={f['key'] for f in fs}
for k,t in R.items():
    p=f'{S}/svg/{k}.svg'; open(p,'w').write(t)
    if f't__{k}' not in have: fs.append({'path':p,'key':f't__{k}','group':'t'})
json.dump(fs,open(f'{S}/files.json','w'),indent=0)
print(len(fs))
