import os, subprocess, sys, numpy as np, re, shutil
from PIL import Image
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom/investigate/inv-masks')
SVG=os.path.expanduser('~/src/femtovg-wt/da/corpus/babylon/vertex-pulling-normals-uvs-colors-tangents__1.svg')
R=os.path.expanduser('~/src/femtovg-wt/runs/zoom/fresh/refs/')
K='corpus__babylon__vertex-pulling-normals-uvs-colors-tangents__1'
TAG={'1':'z1','1.25':'z125','1.5':'z15','1.75':'z175','2':'z2','3':'z3','4':'z4'}
ENV=dict(os.environ, FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30', SKIP_UNSUPPORTED_FILTERS='1', VIEWPORT_CLIP='1', TRANSIENT_BUDGET_MB='1024', INV_MASK_STATS='1')
L=lambda p: np.asarray(Image.open(p).convert('RGB')).astype(int)
n8=lambda a,b: int((np.abs(a-b).max(2)>8).sum())
def run(name, extra, zooms, frames, keep=False):
    out=f'{H}/var/{name}'; os.makedirs(out, exist_ok=True)
    rows=[]
    for z in zooms:
        env=dict(ENV, **extra, ZOOM_LADDER=','.join([z]*frames))
        p=subprocess.run([f'{H}/bin/_logos_full_inv', z, f'{out}/z{z}.ppm', SVG], env=env, capture_output=True, text=True)
        ms=[float(m) for m in re.findall(r'mask_ms ([0-9.]+)', p.stderr)]
        fr=[L(f'{out}/z{z}.ppm.{i:02d}.ppm') for i in range(frames)]
        last=fr[-1]
        settled=next(i for i in range(frames) if all((fr[j]==last).all() for j in range(i,frames)))
        period2 = frames>=4 and (fr[-1]==fr[-3]).all() and not (fr[-1]==fr[-2]).all()
        chr_=L(f'{R}chr_{K}_{TAG[z]}.png'); wk=L(f'{R}wk_{K}_{TAG[z]}.png')
        rows.append(dict(z=z, settled=settled, period2=bool(period2), f00_chr=n8(fr[0],chr_), f00_wk=n8(fr[0],wk), last_chr=n8(last,chr_), last_wk=n8(last,wk), f01_vs_f00=int((np.abs(fr[1]-fr[0]).max(2)>0).sum()) if frames>1 else 0, mask_ms_f0=ms[0] if ms else None, mask_ms_max=max(ms) if ms else None))
        if not keep:
            for i in range(frames):
                if i not in (0,1,frames-1): os.remove(f'{out}/z{z}.ppm.{i:02d}.ppm')
    for r in rows: print(name, r, flush=True)
if __name__=='__main__':
    zooms=['1','1.25','1.5','1.75','2']
    v=sys.argv[1]; frames=int(sys.argv[2])
    extra={'base':{}, 'nocap':{'INV_MASKS_A_FRAME':'100000000'}, 'keyfirst':{'INV_KEY_FIRST':'1'}, 'draws':{'INV_COUNT_DRAWS':'1'}, 'nomotion':{'INV_NO_MOTION_RESTART':'1'}}[v]
    run(v, extra, zooms, frames)
