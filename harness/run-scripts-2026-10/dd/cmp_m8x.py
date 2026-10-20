import json, os, subprocess, collections
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
from common import *
by_key = {f['key']: f for f in files()}
rows = [json.loads(l) for l in open(f'{OUT}/classify.jsonl')]
def job(r):
    k, fr = r['key'], r['framing']
    f, z = FRAMINGS[fr]
    ppm = f'{OUT}/tmp/x_{abs(hash((k, fr)))}.ppm'
    subprocess.run([BUILDS['m8x'][0], f'{z:g}', ppm, by_key[k]['path']], env={**os.environ, **f, **SWEEP_ENV, **BUILDS['m8x'][1]}, capture_output=True)
    x = np.asarray(Image.open(ppm).convert('RGB'), dtype=np.int16); os.remove(ppm)
    a = np.asarray(Image.open(f'{OUT}/png_changed/rv_{k}_{fr}.png').convert('RGB'), dtype=np.int16)
    b = np.asarray(Image.open(f'{OUT}/png_changed/m8_{k}_{fr}.png').convert('RGB'), dtype=np.int16)
    d = np.abs(x - a).max(axis=2)
    db = np.abs(x - b).max(axis=2)
    kinds = set(r['merges'])
    cls = 'exact only' if kinds == {'corner ontocorner exact'} else ('no exact' if not any('exact' in s for s in kinds) else 'mixed')
    return cls, int((d > 0).sum()), int(d.max()), r['diff_px'], int((db > 0).sum()), k, fr
out = collections.defaultdict(list)
with ThreadPoolExecutor(5) as ex:
    for res in ex.map(job, rows):
        out[res[0]].append(res[1:])
for cls, v in out.items():
    same = sum(1 for x in v if x[0] == 0)
    print(f'{cls}: {len(v)} frames; m8x == fix in {same}; changed px fix vs master {sum(x[2] for x in v)}, m8x vs fix {sum(x[0] for x in v)}, m8x vs master {sum(x[3] for x in v)}')
    for x in sorted(v, reverse=True)[:6]:
        if x[0]: print(f'    m8x vs fix {x[0]} px (max {x[1]}), fix vs master {x[2]} px: {x[4][-50:]} {x[5]}')
