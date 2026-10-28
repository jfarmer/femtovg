import sys; sys.path.insert(0,'.')
from model import *
H='/Users/matt/src/femtovg-wt/runs/zoom'
key='corpus__probes__bigblur'; Z=3.0; W,Hh=460,260; fit=200/1024
X=lambda u: 230+(130+fit*u-230)*Z; Y=lambda v: 130+(30+fit*v-130)*Z
groups=[(100,128,(0x28,0x80,0xc0)),(250,96,(0x50,0x80,0xc0)),(400,64,(0x78,0x80,0xc0)),(550,128,(0xa0,0x80,0xc0))]
def render(kind, roundout=False):
    img=np.full((Hh,W,3),255.0)
    for x,sd,col in groups:
        s=sd*fit*Z
        r=(X(x),Y(200),X(x+300),Y(500)); g=[X(x-150),Y(50),X(x+450),Y(650)]
        if roundout: g=[math.floor(g[0]),math.floor(g[1]),math.ceil(g[2]),math.ceil(g[3])]
        if kind=='exact':
            ax=exact1d(W,r[0],r[2],s,g[0],g[2]); ay=exact1d(Hh,r[1],r[3],s,g[1],g[3])
        else:
            P=1500
            ax,_=threebox1d(W+2*P,r[0]+P,r[2]+P,s,g[0]+P,g[2]+P); ax=ax[P:P+W]
            ay,_=threebox1d(Hh+2*P,r[1]+P,r[3]+P,s,g[1]+P,g[3]+P); ay=ay[P:P+Hh]
        a=np.outer(ay,ax)[...,None]
        img=img*(1-a)+np.array(col)[None,None,:]*a
    return img
I={'fvg':load(f'{H}/png/zl_zm_svg/{key}/05.png')}
for b in ('chr','ff','wk'): I[b]=load(f'{H}/fresh/refs/{b}_{key}_z3.png')
I['exact']=render('exact'); I['exact_ro']=render('exact',True); I['3box']=render('box'); I['3box_ro']=render('box',True)
n=list(I)
print(' '*10+''.join('%-11s'%x for x in n))
for a in n: print('%-10s'%a+''.join('%-11s'%('%d(%d)'%cmp(I[a],I[b])) for b in n))
for k in ('fvg','chr','ff'):
    for ref in ('exact_ro','3box_ro'):
        d=np.abs(I[k]-I[ref]).max(axis=2); ys,xs=np.nonzero(d>8)
        if len(xs): print(k,'vs',ref,'bad x',xs.min(),xs.max(),'y',ys.min(),ys.max(), 'rows', sorted(set(ys.tolist()))[:12])
print('Y(650)=',Y(650),'Y(50)=',Y(50), 'X groups', [(X(x-150),X(x+450)) for x,_,_ in groups])
