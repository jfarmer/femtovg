#!/usr/bin/env python3
"""Every corpus frame (runs/pr/files.json, z1 z2 z4 hd) with one binary, hashed as accuracy.py hashes (sha1 of the
PPM), against another build's hashes in runs/pr/accuracy.jsonl. Changed frames are kept as png_changed/TAG_KEY_FR.png
and listed in TAG_vs_BASE.json (resumable through that file).

  corpus_hash.py TAG BINARY BASE"""
import hashlib, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PR = os.path.expanduser('~/src/femtovg-wt/runs/pr')
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import FRAMINGS, SWEEP_ENV  # noqa: E402

tag, binary, base = sys.argv[1:4]
fs = json.load(open(f'{PR}/files.json'))
want = {}
for line in open(f'{PR}/accuracy.jsonl'):
    r = json.loads(line)
    if r['build'] == base and r.get('hash'):
        want[(r['key'], r['framing'])] = r['hash']
out_json = f'{HERE}/{tag}_vs_{base}.json'
done = json.load(open(out_json)) if os.path.exists(out_json) else {}
os.makedirs(f'{HERE}/png_changed', exist_ok=True)
os.makedirs(f'{HERE}/tmp', exist_ok=True)


def one(job):
    f, framing = job
    name = f'{f["key"]}|{framing}'
    if name in done:
        return name, done[name]
    fr, z = FRAMINGS[framing]
    ppm = f'{HERE}/tmp/h_{tag}_{f["key"]}_{framing}.ppm'
    env = {**os.environ, **fr, **SWEEP_ENV, 'SINGLE_SHADOW_LAYER': '1'}
    try:
        r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env=env, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return name, 'timeout'
    if r.returncode != 0 or not os.path.exists(ppm):
        return name, 'error'
    h = hashlib.sha1(open(ppm, 'rb').read()).hexdigest()
    old = want.get((f['key'], framing))
    if old is None:
        state = 'nobase'
    elif old == h:
        state = 'same'
    else:
        state = 'changed'
        Image.open(ppm).convert('RGB').save(f'{HERE}/png_changed/{tag}_{f["key"]}_{framing}.png')
    os.remove(ppm)
    return name, state


jobs = [(f, fr) for f in fs for fr in ('z1', 'z2', 'z4', 'hd')]
with ThreadPoolExecutor(4) as ex:
    for i, (name, state) in enumerate(ex.map(one, jobs)):
        done[name] = state
        if (i + 1) % 400 == 0:
            json.dump(done, open(out_json, 'w'))
            print(i + 1, flush=True)
json.dump(done, open(out_json, 'w'))
import collections
print(collections.Counter(done.values()))
