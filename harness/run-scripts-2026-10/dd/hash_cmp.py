"""hash_cmp.py REF NEW [framings=...] : render NEW for every frame REF has a row for; compare hashes."""
import hashlib, json, os, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor
from common import *
ref, new = sys.argv[1:3]
by_key = {f['key']: f for f in files()}
want = {}
for l in open(f'{OUT}/accuracy.jsonl'):
    r = json.loads(l)
    if r['build'] == ref and r.get('hash'):
        want[(r['key'], r['framing'])] = r['hash']
def job(x):
    k, fr = x
    f, z = FRAMINGS[fr]
    ppm = f'{OUT}/tmp/h_{threading.get_ident()}.ppm'
    subprocess.run([BUILDS[new][0], f'{z:g}', ppm, by_key[k]['path']], env={**os.environ, **f, **SWEEP_ENV, **BUILDS[new][1]}, capture_output=True, timeout=300)
    h = hashlib.sha1(open(ppm, 'rb').read()).hexdigest() if os.path.exists(ppm) else None
    if h: os.remove(ppm)
    return x, h
diff = []
with ThreadPoolExecutor(5) as ex:
    for x, h in ex.map(job, sorted(want)):
        if h != want[x]: diff.append(x)
print(f'{new} vs {ref}: {len(want)} frames, {len(want) - len(diff)} identical, {len(diff)} differ')
for x in diff[:20]: print('  ', x)
