# run_build.py BIN TAG: render every cluster file at every zoom into ../png/TAG/KEY_FR.png
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
H = os.path.expanduser('~')
c = json.load(open(f'{H}/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))['clip-edges']
FR = {'z1': 1, 'z125': 1.25, 'z15': 1.5, 'z175': 1.75, 'z2': 2, 'z3': 3, 'z4': 4, 'z075': 0.75, 'z05': 0.5, 'z033': 0.33, 'z025': 0.25}
binp, tag = sys.argv[1], sys.argv[2]
out = f'{H}/src/femtovg-wt/runs/zoom/triage/clip-edges/png/{tag}'; os.makedirs(out, exist_ok=True)
def run(j):
    f, fr = j
    p = f'{out}/{f["key"]}_{fr}.png'
    if not os.path.exists(p):
        subprocess.run(['./fem.sh', binp, str(FR[fr]), p, f'{H}/{f["path"]}'])
    return os.path.exists(p)
with ThreadPoolExecutor(4) as ex: print(sum(ex.map(run, [(f, fr) for f in c for fr in FR])))
