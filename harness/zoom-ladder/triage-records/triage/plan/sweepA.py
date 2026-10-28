import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, '/Users/matt/src/femtovg-wt/runs/zoom/triage/clip-edges-v')
from cmp import load, fem, ref, beyond
S = sys.argv[1]
B = '/Users/matt/src/femtovg-wt/runs/zoom/triage/clip-edges-v/bin/_logos_full_area_v'
env = dict(os.environ, FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30',
           SKIP_UNSUPPORTED_FILTERS='1', VIEWPORT_CLIP='1', TRANSIENT_BUDGET_MB='1024')
d = json.load(open('/Users/matt/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))
out = []
for cname, files in d.items():
    if cname == 'clip-edges':
        continue
    for f in files:
        k = f['key']; svg = os.path.expanduser('~/' + f['path'])
        for b in f['bad']:
            z = b[0]
            p = f'{S}/a.ppm'
            subprocess.run([B, str(z), p, svg], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            a = load(p); m = fem(k, z)
            if a is None or m is None:
                out.append((cname, k, z, 'missing')); continue
            if np.array_equal(a[..., :3], m[..., :3]):
                continue
            mb = min(v for v in (beyond(m, ref(br, k, z)) for br in ('chr', 'ff', 'wk')) if v is not None)
            ab = min(v for v in (beyond(a, ref(br, k, z)) for br in ('chr', 'ff', 'wk')) if v is not None)
            diff = int((np.abs(a[..., :3] - m[..., :3]).max(-1) > 0).sum())
            out.append((cname, k, z, mb, ab, diff))
            print(cname, k, z, mb, '->', ab, 'pxchanged', diff, flush=True)
print('moved', len(out))
