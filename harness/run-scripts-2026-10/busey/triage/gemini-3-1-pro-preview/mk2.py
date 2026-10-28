import re
S='/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview'
src=open(f'{S}/svg/orig.svg').read()
defs=src[:src.index('</defs>')+7]
bg='<rect width="1024" height="1024" fill="url(#bg-grad)"/>'
def grp(gid):
    i=src.index(f'<g id="{gid}"'); 
    # find matching </g>
    depth=0; j=i
    for m in re.finditer(r'<g\b|</g>', src[i:]):
        depth += 1 if m.group(0)=='<g' else -1
        if depth==0: j=i+m.end(); break
    return src[i:j]
hf=grp('hair-front')
def w(name, body):
    open(f'{S}/svg/{name}.svg','w').write(defs+'\n'+body+'\n</svg>\n')
w('hf_only', bg+hf)
w('hf_only_nods', bg+hf.replace(' filter="url(#drop-shadow)"','',1))
w('hf_only_noxs', bg+hf.replace(' filter="url(#blur-xs)"',''))
w('hf_only_noxs_nods', bg+hf.replace(' filter="url(#blur-xs)"','').replace(' filter="url(#drop-shadow)"','',1))
# shadow invisible
w('hf_only_fo0', bg+hf.replace('filter="url(#drop-shadow)"','filter="url(#ds0)"',1).replace('<g id="hair-front"','<filter id="ds0" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="10" stdDeviation="15" flood-color="#000" flood-opacity="0"/></filter><g id="hair-front"'))
# strokes only (no fills), drop shadow on
hf_strokes=re.sub(r'<path d="[^"]*" fill="[^"]*"/>','',hf)
w('hf_strokes', bg+hf_strokes)
w('hf_strokes_nods', bg+hf_strokes.replace(' filter="url(#drop-shadow)"','',1))
hf_fills=re.sub(r'<g fill="none".*?</g>','',hf,flags=re.S)
w('hf_fills', bg+hf_fills)
w('hf_fills_nods', bg+hf_fills.replace(' filter="url(#drop-shadow)"','',1))
