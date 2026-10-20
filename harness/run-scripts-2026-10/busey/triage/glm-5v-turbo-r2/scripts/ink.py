import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from coords import S as FRS
S='/Users/matt/src/femtovg-wt/runs/busey/triage/glm-5v-turbo-r2'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
def box(fr,u0,v0,u1,v1):
    ox,oy,s=FRS[fr]; return (int(np.floor(ox+u0*s)),int(np.floor(oy+v0*s)),int(np.ceil(ox+u1*s)),int(np.ceil(oy+v1*s)))
def ink(key, fr, ub, build='mst4', bg=None, fg=None):
    x0,y0,x1,y1=box(fr,*ub)
    ims={'fem':L(f'{S}/png/{build}_{key}_{fr}.png')}
    for b in ('chr','ff','wk','id'): ims[b]=L(f'{S}/refs/{b}_{key}_{fr}.png')
    out={}
    bgc=np.array(bg if bg is not None else [255,255,255],float); fgc=np.array(fg if fg is not None else [0,0,0],float)
    for n,im in ims.items():
        c=im[y0:y1,x0:x1]
        cov=((c-bgc)@(fgc-bgc))/((fgc-bgc)@(fgc-bgc))
        out[n]=float(cov.sum())
    o=ims['fem'][y0:y1,x0:x1]; refs=[ims[b][y0:y1,x0:x1] for b in ('chr','ff','wk')]
    off=[np.abs(o-r).max(2)>20 for r in refs]; a=off[0]&off[1]&off[2]
    offid=np.abs(o-ims['id'][y0:y1,x0:x1]).max(2)>20
    return out, int(a.sum()), int(offid.sum())
if __name__=='__main__':
    key=sys.argv[1]; fr=sys.argv[2]; ub=tuple(map(float,sys.argv[3:7])); build=sys.argv[7] if len(sys.argv)>7 else 'mst4'
    out,a,oi=ink(key,fr,ub,build)
    print(f'{key} {fr} {build} box{ub}: red(all3) {a} off_id {oi} | ink ' + ' '.join(f'{k} {v:.1f}' for k,v in out.items()) + f' | fem/id {out["fem"]/out["id"]:.3f} chr/id {out["chr"]/out["id"]:.3f} ff/id {out["ff"]/out["id"]:.3f} wk/id {out["wk"]/out["id"]:.3f}')
