#!/usr/bin/env python3
"""snap_diff.py [framings=hd,p240] [variants=snp2,snp4,snp8] [workers=6] [jsonl=PATH] [only=FRAMING:KEYS.json,...]: every corpus file at each framing drawn
exact (snp0) and with the thin-fill masks' positions snapped (the variants), and each snapped frame's pixels that
differ from the exact one by more than 8 and more than 20 levels, and by how much at most. Rows go to
CORPUS_RUN_OUT/snap_diff.jsonl (resumable); prints, per framing and variant, the frames with more than 2 pixels
beyond each threshold and the worst frames."""
import collections, json, os, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import *
opts = dict(a.split('=', 1) for a in sys.argv[1:])
framings = opts.get('framings', 'hd,p240').split(',')
variants = opts.get('variants', 'snp2,snp4,snp8').split(',')
workers = int(opts.get('workers', 6))
path = opts.get('jsonl', f'{OUT}/snap_diff.jsonl')
# only=hd:changed_hd.json,p240:changed_p240.json limits each framing to the frames listed (those whose masks snapping
# touches: a frame without masks draws the same at any step)
only = {fr: set(json.load(open(f))) for fr, f in (a.split(':') for a in opts['only'].split(','))} if 'only' in opts else None
done = {(r['key'], r['framing']) for r in map(json.loads, open(path))} if os.path.exists(path) else set()
out = open(path, 'a'); lock = threading.Lock()
os.makedirs(f'{OUT}/tmp', exist_ok=True)


def render(build, f, framing):
    binary, extra = BUILDS[build]; fr, z = FRAMINGS[framing]
    ppm = f'{OUT}/tmp/sd_{build}_{os.getpid()}_{threading.get_ident()}.ppm'
    r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra}, capture_output=True, timeout=600)
    if not os.path.exists(ppm):
        return None
    d = open(ppm, 'rb').read(); os.remove(ppm)
    p = d.split(b'\n', 3); w, h = map(int, p[1].split())
    return np.frombuffer(p[3], dtype=np.uint8).reshape(h, w, 3).astype(np.int16)


def job(args):
    f, framing = args
    base = render('snp0', f, framing)
    row = {'key': f['key'], 'framing': framing, 'group': f['group']}
    for v in variants:
        im = render(v, f, framing)
        if base is None or im is None:
            row[v] = None
            continue
        d = np.abs(im - base).max(axis=2)
        row[v] = [int((d > 8).sum()), int((d > 20).sum()), int(d.max())]
    with lock:
        out.write(json.dumps(row) + '\n'); out.flush()


jobs = [(f, fr) for fr in framings for f in files() if (f['key'], fr) not in done and (only is None or f['key'] in only[fr])]
print(f'{len(jobs)} frames to draw', flush=True)
with ThreadPoolExecutor(workers) as ex:
    for i, _ in enumerate(ex.map(job, jobs)):
        if (i + 1) % 500 == 0:
            print(f'{i + 1}/{len(jobs)}', flush=True)
rows = [json.loads(l) for l in open(path)]
for fr in framings:
    sel = [r for r in rows if r['framing'] == fr]
    print(f'\n{fr}: {len(sel)} frames')
    for v in variants:
        got = [r for r in sel if r.get(v)]
        moved8 = [r for r in got if r[v][0] > 2]; moved20 = [r for r in got if r[v][1] > 2]
        any_ = [r for r in got if r[v][0] > 0 or r[v][2] > 0]
        print(f'  {v}: frames differing at all {sum(1 for r in got if r[v][2] > 0)}; more than 2 px beyond 8/255 {len(moved8)}, '
              f'beyond 20/255 {len(moved20)}; pixels beyond 20/255 in all {sum(r[v][1] for r in got)}')
        worst = sorted(got, key=lambda r: -r[v][1])[:5]
        print('    worst:', [(r['key'].split('__')[-1][:36], r[v][1], r[v][2]) for r in worst])
