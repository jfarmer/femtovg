import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, '/Users/matt/src/femtovg-wt/runs/zoom/triage/clip-edges-v')
from cmp import load, ref, beyond
S = sys.argv[1]
D = '/Users/matt/src/femtovg-wt/runs/zoom/triage/mask-thin-stroke-3x/bin/'
env = dict(os.environ, FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30',
           SKIP_UNSUPPORTED_FILTERS='1', VIEWPORT_CLIP='1', TRANSIENT_BUDGET_MB='1024')
d = json.load(open('/Users/matt/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))
def best(im, k, z):
    return min(v for v in (beyond(im, ref(br, k, z)) for br in ('chr', 'ff', 'wk')) if v is not None)
n = 0
for cname, files in d.items():
    for f in files:
        k = f['key']; svg = os.path.expanduser('~/' + f['path'])
        for b in f['bad']:
            z = b[0]; ims = {}
            for t in ('_logos_cull', '_logos_cull_aa1'):
                p = f'{S}/b{t}.ppm'
                subprocess.run([D + t, str(z), p, svg], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                ims[t] = load(p)
            c, a = ims['_logos_cull'], ims['_logos_cull_aa1']
            if np.array_equal(c[..., :3], a[..., :3]):
                continue
            n += 1
            diff = int((np.abs(a[..., :3] - c[..., :3]).max(-1) > 8).sum())
            print(cname, k, z, 'cull', best(c, k, z), 'aa1', best(a, k, z), 'px>8 changed', diff, flush=True)
print('moved', n)
