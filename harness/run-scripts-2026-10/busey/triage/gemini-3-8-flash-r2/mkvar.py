# mkvar.py NAME drop=L1,L2 [repl=L:file]... : edit svg/g00_orig.svg by 1-based line numbers
import sys, json, os
S=os.path.dirname(os.path.abspath(__file__))
lines=open(f'{S}/svg/g00_orig.svg').read().split('\n')
name=sys.argv[1]; drop=set(); repl={}
for a in sys.argv[2:]:
    k,v=a.split('=',1)
    if k=='drop': drop|={int(x) for x in v.split(',')}
    elif k=='repl':
        l,f=v.split(':',1); repl[int(l)]=open(f).read().rstrip('\n')
out=[]
for i,l in enumerate(lines,1):
    if i in repl: out.append(repl[i])
    elif i in drop: out.append('')
    else: out.append(l)
open(f'{S}/svg/{name}.svg','w').write('\n'.join(out))
fs=json.load(open(f'{S}/files.json')) if os.path.exists(f'{S}/files.json') else []
k=f't__{name}'
if not any(f['key']==k for f in fs): fs.append({'path':f'{S}/svg/{name}.svg','key':k,'group':'t'})
json.dump(fs,open(f'{S}/files.json','w'))
print(k)
