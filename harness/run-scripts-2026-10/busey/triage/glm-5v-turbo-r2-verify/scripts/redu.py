import sys, numpy as np
sys.path.insert(0,'scripts')
from red import L, masks, S
def ink(im, bg, box, fr):
    ox,oy,s=S[fr]; x0,y0,x1,y1=box
    X0=int(np.floor(ox+x0*s)); X1=int(np.ceil(ox+x1*s)); Y0=int(np.floor(oy+y0*s)); Y1=int(np.ceil(oy+y1*s))
    sub=im[Y0:Y1,X0:X1].astype(float)
    # ink = coverage-equivalent: fraction of the way from bg to fg, summed, per channel max-diff channel
    return sub, (X0,Y0)
def run(key, fr, box, fg, bg, build='mst4'):
    o=L(f'png/{build}_{key}_{fr}.png'); rf=[L(f'refs/{x}_{key}_{fr}.png') for x in ('chr','ff','wk','id')]
    a,g,sp,offid=masks(o,rf)
    fg=np.array(fg,float); bg=np.array(bg,float); c=np.argmax(np.abs(fg-bg))
    def cov(im):
        sub,_=ink(im,bg,box,fr); return ((sub[...,c]-bg[c])/(fg[c]-bg[c])).sum()
    ox,oy,s=S[fr]; x0,y0,x1,y1=box
    ys,xs=np.nonzero(a); u=(xs+0.5-ox)/s; v=(ys+0.5-oy)/s; inb=(u>=x0)&(u<x1)&(v>=y0)&(v<y1)
    ci=cov(rf[3])
    return dict(red=int(inb.sum()), red_offid=int((offid[ys,xs]&inb).sum()), ink_vs_area={n:round(cov(im)/ci,3) for n,im in zip(['fem','chr','ff','wk'],[o]+rf[:3])}, area_ink=round(ci,2))
if __name__=='__main__':
    import json
    fr=sys.argv[1]; box=tuple(map(float,sys.argv[2].split(','))); fg=tuple(map(int,sys.argv[3].split(','))); bg=tuple(map(int,sys.argv[4].split(',')))
    for k in sys.argv[5:]:
        for b in ['mst4','fm']:
            try: print(f'{b:4s} {k:24s}', json.dumps(run(k,fr,box,fg,bg,b)))
            except FileNotFoundError: pass
