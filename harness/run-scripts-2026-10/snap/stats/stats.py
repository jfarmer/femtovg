#!/usr/bin/env python3
"""stats.py BUILD KEY FRAMING [frames=60]: the experiment's per-frame atlas line (FEMTOVG_MASK_STATS) in motion."""
import os, subprocess, sys
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
os.environ.setdefault('CORPUS_RUN_OUT', os.path.expanduser('~/src/femtovg-wt/runs/thin'))
from common import *  # noqa
build, key, framing = sys.argv[1:4]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 60
fs = {f['key']: f for f in files()}
key = next(k for k in fs if k.endswith(key))
binary, extra = BUILDS[build]
fr, z = FRAMINGS[framing]
env = {**os.environ, **fr, **SWEEP_ENV, **extra, 'FRAMES': str(n), 'FRAME_DRIFT': '0.37', 'MEM_PEAKS': '1', 'FEMTOVG_MASK_STATS': '1'}
r = subprocess.run([binary, f'{z:g}', '/tmp/claude-501/e2e.ppm', fs[key]['path']], env=env, capture_output=True, text=True)
for line in r.stderr.splitlines():
    if line.startswith('fill masks') or 'peak' in line:
        print(line)
