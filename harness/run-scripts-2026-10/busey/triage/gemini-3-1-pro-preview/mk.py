import re
S='/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview'
src=open(f'{S}/svg/orig.svg').read()
def w(name, t):
    assert t!=src, name
    open(f'{S}/svg/{name}.svg','w').write(t)
w('nofilters', re.sub(r' filter="url\(#[^)]*\)"','',src))
w('nodropshadow', src.replace(' filter="url(#drop-shadow)"',''))
w('nods_hairfront', src.replace('<g id="hair-front" filter="url(#drop-shadow)">','<g id="hair-front">'))
w('nods_hairback', src.replace('<g id="hair-back" filter="url(#drop-shadow)">','<g id="hair-back">'))
w('nods_head', src.replace('<g id="head-base" filter="url(#drop-shadow)">','<g id="head-base">'))
w('nods_brows', src.replace('<g id="eyebrows" filter="url(#drop-shadow)">','<g id="eyebrows">'))
w('noblurxs', src.replace(' filter="url(#blur-xs)"',''))
w('noblurs', re.sub(r' filter="url\(#blur-[a-z]+\)"','',src))
w('noclip', re.sub(r' clip-path="url\(#[^)]*\)"','',src))
