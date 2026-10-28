#!/usr/bin/env python3
"""snap_area.py: the frames snapping changes (changed_<framing>.json), each variant against the area reference
(refs/id_KEY_FRAMING.png): pixels beyond 20/255 and beyond 8/255, summed, with the frames nearer and further than the
exact masks."""
import json, os, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import *
HERE = os.path.dirname(os.path.abspath(__file__))
VARIANTS = ['snp_off', 'snp0', 'snp2', 'snp4', 'snp8']
fs = {f['key']: f for f in files()}


def render(build, key, framing):
    binary, extra = BUILDS[build]; fr, z = FRAMINGS[framing]
    ppm = f'{OUT}/tmp/sa_{build}_{threading.get_ident()}.ppm'
    subprocess.run([binary, f'{z:g}', ppm, fs[key]['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra}, capture_output=True)
    d = open(ppm, 'rb').read(); os.remove(ppm)
    p = d.split(b'\n', 3); w, h = map(int, p[1].split())
    return np.frombuffer(p[3], dtype=np.uint8).reshape(h, w, 3).astype(np.int16)


def one(args):
    key, framing = args
    ref = f'{OUT}/refs/id_{key}_{framing}.png'
    if not os.path.exists(ref):
        return None
    idr = np.asarray(Image.open(ref).convert('RGB'), dtype=np.int16)
    h, w = idr.shape[:2]
    row = {'key': key, 'framing': framing}
    for v in VARIANTS:
        d = np.abs(render(v, key, framing)[:h, :w] - idr).max(axis=2)
        row[v] = [int((d > 20).sum()), int((d > 8).sum())]
    return row


for framing in ('hd', 'p240'):
    keys = json.load(open(f'{HERE}/changed_{framing}.json'))
    with ThreadPoolExecutor(6) as ex:
        rows = [r for r in ex.map(one, [(k, framing) for k in keys]) if r]
    json.dump(rows, open(f'{HERE}/area_{framing}.json', 'w'))
    print(f'{framing}: {len(rows)} of {len(keys)} changed frames have an area reference')
    for v in VARIANTS:
        s20 = sum(r[v][0] for r in rows); s8 = sum(r[v][1] for r in rows)
        rel = '' if v in ('snp_off', 'snp0') else f'; vs exact: nearer {sum(r[v][0] < r["snp0"][0] for r in rows)}, further {sum(r[v][0] > r["snp0"][0] for r in rows)}'
        print(f'  {v:8s} beyond 20/255 {s20:6d} px, beyond 8/255 {s8:6d} px{rel}')
