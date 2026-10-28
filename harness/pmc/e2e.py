#!/usr/bin/env python3
"""e2e.py [ecore=1] [lo=50] [hi=250] [rounds=3] BUILD... -- KEY:FRAMING... : instructions and cycles a frame of the
harness in motion (FRAME_DRIFT=0.37), the difference of a long and a short run, under `taskpolicy -c background`
(the efficiency cores) unless ecore=0; builds alternate, the median of the rounds is printed. Also the peak memory
footprint and its graphics part of the long run (MEM_PEAKS)."""
import os, re, statistics as st, subprocess, sys
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
os.environ.setdefault('CORPUS_RUN_OUT', os.path.expanduser('~/src/femtovg-wt/runs/thin'))
from common import *  # noqa

args = sys.argv[1:]
opts = dict(a.split('=', 1) for a in args if '=' in a and not a.startswith('-'))
rest = [a for a in args if '=' not in a or a.startswith('-')]
i = rest.index('--')
builds, frames = rest[:i], [f.split(':') for f in rest[i + 1:]]
ecore, lo, hi, rounds = opts.get('ecore', '1') == '1', int(opts.get('lo', 50)), int(opts.get('hi', 250)), int(opts.get('rounds', 3))
fs = {f['key']: f for f in files()}


def run(build, key, framing, n):
    binary, extra = BUILDS[build]
    fr, z = FRAMINGS[framing]
    env = {**os.environ, **fr, **SWEEP_ENV, **extra, 'FRAMES': str(n), 'FRAME_DRIFT': '0.37', 'MEM_PEAKS': '1'}
    cmd = ['/usr/bin/time', '-l'] + (['/usr/sbin/taskpolicy', '-c', 'background'] if ecore else []) + \
          [binary, f'{z:g}', '/tmp/claude-501/e2e.ppm', fs[key]['path']]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    g = lambda name: int(re.search(r'(\d+)\s+' + name, r.stderr).group(1))
    peak = re.search(r'peak_footprint=(\d+)', r.stderr) or re.search(r'peak[=: ]+(\d+)', r.stderr)
    graphics = re.search(r'peak_graphics=(\d+)', r.stderr)
    return g('instructions retired'), g('cycles elapsed'), int(peak.group(1)) if peak else 0, int(graphics.group(1)) if graphics else 0


for key, framing in frames:
    key = next(k for k in fs if k.endswith(key))
    res = {b: [] for b in builds}
    for _ in range(rounds):
        for b in builds:
            i0, c0, _, _ = run(b, key, framing, lo)
            i1, c1, p1, g1 = run(b, key, framing, hi)
            res[b].append(((i1 - i0) / (hi - lo), (c1 - c0) / (hi - lo), p1, g1))
    base = None
    for b in builds:
        ins, cyc, peak, gfx = (st.median(c) for c in zip(*res[b]))
        base = base or (ins, cyc)
        print(f'{key[-28:]:28s} {framing:3s} {b:9s} {"E" if ecore else "P"}: {ins / 1e6:7.3f} M instr ({100 * (ins / base[0] - 1):+4.0f} %) '
              f'{cyc / 1e6:7.3f} M cycles ({100 * (cyc / base[1] - 1):+4.0f} %) a frame; peak {peak / 2**20:6.1f} MiB, graphics {gfx / 2**20:6.1f} MiB',
              flush=True)
