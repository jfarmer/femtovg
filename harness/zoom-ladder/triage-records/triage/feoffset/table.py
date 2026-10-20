import json, numpy as np
from cmp import *
d=json.load(open('../clusters_compact.json'))
fr={0.25:'z025',0.33:'z033',0.5:'z05',0.75:'z075',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',1:'z1'}
def n(a,b):
    if a is None or b is None: return None
    return int(bad(a,b)[0].sum())
rows_=[]
for v in d['feoffset']:
    if not v['key'].startswith('corpus__'): continue
    name=v['key'].split('__')[-1]
    for b in v['bad']:
        z=b[0]; F=frames(v['key'],fr[z]); A=load(f'area/{name}_{fr[z]}.png')
        r=dict(name=name,z=z,fv_chr=n(F['fv'],F['chr']),fv_ff=n(F['fv'],F['ff']),fv_wk=n(F['fv'],F['wk']),
               chr_ff=n(F['chr'],F['ff']),chr_wk=n(F['chr'],F['wk']),ff_wk=n(F['ff'],F['wk']),
               fv_area=n(F['fv'],A),chr_area=n(F['chr'],A),ff_area=n(F['ff'],A),wk_area=n(F['wk'],A))
        rows_.append(r)
json.dump(rows_,open('table.json','w'))
hdr=['name','z','fv_chr','fv_ff','fv_wk','chr_ff','chr_wk','ff_wk','fv_area','chr_area','ff_area','wk_area']
print(' '.join(f'{h[:9]:>9s}' if h!='name' else f'{h:44s}' for h in hdr))
for r in rows_:
    print(' '.join(f'{str(r[h]):>9s}' if h!='name' else f'{r[h][:44]:44s}' for h in hdr))
