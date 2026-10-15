#!/usr/bin/env python3
"""classify.py LOG A B [workers=4] : re-render every frame the identity LOG reports as differing with builds A and B,
and record how far apart they are: pixels changed, the largest change, pixels changed by more than 2 and by more
than 20 (8-bit levels), and the box they lie in. Writes classify_A_B.jsonl beside this script."""
import json, os, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus_run'))
from common import *  # noqa: E402,F403

log, A, B = sys.argv[1], sys.argv[2], sys.argv[3]
opts = dict(x.split('=', 1) for x in sys.argv[4:])
HERE = os.environ.get('CORPUS_RUN_OUT', os.getcwd())
by_key = {f['key']: f for f in files()}
frames = sorted({tuple(line.split()[1:3]) for line in open(log) if line.startswith('DIFFERS')})


def render(build, f, framing):
    binary, extra = BUILDS[build]
    fr, z = FRAMINGS[framing]
    ppm = f'{HERE}/tmp/cls_{build}_{os.getpid()}_{threading.get_ident()}.ppm'
    env = {**os.environ, **fr, **SWEEP_ENV, **extra}
    subprocess.run([binary, f'{z:g}', ppm, f['path']], env=env, capture_output=True, timeout=600)
    img = np.asarray(Image.open(ppm).convert('RGB')).astype(int)
    os.remove(ppm)
    return img


def job(frame):
    key, framing = frame
    a, b = render(A, by_key[key], framing), render(B, by_key[key], framing)
    d = np.abs(a - b).max(axis=2)
    ys, xs = np.nonzero(d)
    return {'key': key, 'framing': framing, 'px': int(len(ys)), 'max': int(d.max()),
            'px_over2': int((d > 2).sum()), 'px_over20': int((d > 20).sum()),
            'box': [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(ys) else None}


with open(f'{HERE}/classify_{A}_{B}.jsonl', 'w') as out, ThreadPoolExecutor(int(opts.get('workers', 4))) as pool:
    for row in pool.map(job, frames):
        out.write(json.dumps(row) + '\n')
print('classified', len(frames), 'frames')
