#!/usr/bin/env python3
"""fp.py BUILD KEY FRAMING [frames] [at_s]: runs the harness in motion and prints `footprint` by category at_s seconds in."""
import os, subprocess, sys, time
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
os.environ.setdefault('CORPUS_RUN_OUT', os.path.expanduser('~/src/femtovg-wt/runs/thin'))
from common import *  # noqa
build, key, framing = sys.argv[1:4]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
at = float(sys.argv[5]) if len(sys.argv) > 5 else 6
fs = {f['key']: f for f in files()}
key = next(k for k in fs if k.endswith(key))
binary, extra = BUILDS[build]
fr, z = FRAMINGS[framing]
env = {**os.environ, **fr, **SWEEP_ENV, **extra, 'FRAMES': str(n), **({'FRAME_DRIFT': os.environ.get('DRIFT', '0.37')} if os.environ.get('DRIFT', '0.37') != '0' else {})}
p = subprocess.Popen([binary, f'{z:g}', f'/tmp/claude-501/fp_{build}.ppm', fs[key]['path']], env=env, stdout=subprocess.DEVNULL, stderr=open('fp_err.txt', 'w'))
time.sleep(at)
r = subprocess.run(['footprint', '-p', str(p.pid)], capture_output=True, text=True); out = r.stdout + r.stderr + f' (alive: {p.poll() is None})'
p.kill()
print(out)
