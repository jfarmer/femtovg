import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
H = os.path.expanduser('~')
c = json.load(open(f'{H}/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))['clip-edges']
FR = {'z1': 1, 'z125': 1.25, 'z15': 1.5, 'z175': 1.75, 'z2': 2, 'z3': 3, 'z4': 4, 'z075': 0.75, 'z05': 0.5, 'z033': 0.33, 'z025': 0.25}
out = f'{H}/src/femtovg-wt/runs/zoom/triage/clip-edges/area'
jobs = [(f, fr) for f in c for fr in FR]
def run(j):
    f, fr = j
    p = f'{out}/id_{f["key"]}_{fr}.png'
    if os.path.exists(p): return 'kept'
    r = subprocess.run([sys.executable, 'area.py', f'{H}/{f["path"]}', str(FR[fr]), p, 'gpu', '8'], capture_output=True, text=True)
    return 'made' if os.path.exists(p) else 'fail ' + r.stderr[-200:]
with ThreadPoolExecutor(3) as ex:
    res = list(ex.map(run, jobs))
from collections import Counter; print(Counter(res))
