import os, json, subprocess, sys, re, numpy as np
from multiprocessing import Pool
from PIL import Image
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom/investigate/inv-masks')
FILES=json.load(open(os.path.expanduser('~/src/femtovg-wt/runs/zoom/files.json')))
ENV=dict(os.environ, FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30', SKIP_UNSUPPORTED_FILTERS='1', VIEWPORT_CLIP='1', TRANSIENT_BUDGET_MB='1024', INV_MASK_STATS='1')
ZOOMS=sys.argv[1].split(',')
L=lambda p: np.asarray(Image.open(p).convert('RGB')).astype(int)
def one(f):
    out=[]
    for z in ZOOMS:
        tmp=f'{H}/survey_tmp/{f["key"]}_{z}.ppm'
        try:
            p=subprocess.run([f'{H}/bin/_logos_full_inv', z, tmp, f['path']], env=dict(ENV, ZOOM_LADDER=f'{z},{z},{z}'), capture_output=True, text=True, timeout=300)
            st=[dict(zip(['thin','asked','key','made','refused'], map(int, re.search(r'thin (\d+) asked_hit (\d+) key_hit (\d+) made (\d+) refused_share (\d+)', l).groups()))) for l in p.stderr.splitlines() if l.startswith('INV frame')]
            fr=[L(f'{tmp}.{i:02d}.ppm') for i in range(3)]
            d=lambda a,b: (int((np.abs(a-b).max(2)>0).sum()), int((np.abs(a-b).max(2)>8).sum()), int(np.abs(a-b).max()))
            out.append(dict(key=f['key'], z=z, stats=st, f1f0=d(fr[1],fr[0]), f2f1=d(fr[2],fr[1]), f2f0=d(fr[2],fr[0])))
        except Exception as e:
            out.append(dict(key=f['key'], z=z, err=str(e)[:200]))
        finally:
            for i in range(3):
                try: os.remove(f'{tmp}.{i:02d}.ppm')
                except OSError: pass
    return out
if __name__=='__main__':
    os.makedirs(f'{H}/survey_tmp', exist_ok=True)
    with Pool(6) as pool, open(f'{H}/survey_{sys.argv[2]}.jsonl','w') as o:
        for res in pool.imap_unordered(one, FILES, chunksize=4):
            for r in res: o.write(json.dumps(r)+'\n')
            o.flush()
