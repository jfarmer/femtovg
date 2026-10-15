#!/usr/bin/env python3
"""short_runs.py OUT.json REPEATS NAME:FRAMING ...

The checker's own invocation for the first frames and for memory, not the first agent's frames.py or memory.py.

1. Instructions retired (`/usr/bin/time -l`, no MEM_PEAKS) by runs of 0, 1, 2 and 3 frames on mbase and poc. The two
   builds alternate within each repeat and the build that goes first alternates between repeats, so a drift of the
   machine's state does not fall on one build. Frame n costs run(n) - run(n-1).
2. One run of 1 frame and one of 200 frames per build with MEM_PEAKS=1: the harness's MEM line (graphics memory after
   the last frame, passes=, command_buffers=).

NAME is a corpus key or a path to an SVG."""
import json, os, re, subprocess, sys

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'corpus_run'))
from common import BUILDS, FRAMINGS, SWEEP_ENV, files

HERE = os.path.dirname(os.path.abspath(__file__))
BY_KEY = {f['key']: f['path'] for f in files()}
BUILD_NAMES = tuple(os.environ['POC_BUILDS'].split(','))
COUNTS = (0, 1, 2, 3)


def run(build, name, framing, frames, more=None):
    binary, extra = BUILDS[build]
    fr, z = FRAMINGS[framing]
    ppm = f'{os.environ["CORPUS_RUN_OUT"]}/tmp/cold_{os.getpid()}.ppm'
    env = {**os.environ, **fr, **SWEEP_ENV, **extra, **(more or {}), 'FRAMES': str(frames)}
    r = subprocess.run(['/usr/bin/time', '-l', binary, f'{z:g}', ppm, BY_KEY.get(name, name)], env=env,
                       capture_output=True, text=True)
    if os.path.exists(ppm):
        os.remove(ppm)
    return int(re.search(r'(\d+)\s+instructions retired', r.stderr).group(1)), r.stderr


out, repeats, jobs = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
rows = []
for job in jobs:
    name, framing = job.rsplit(':', 1)
    raw = {b: {n: [] for n in COUNTS} for b in BUILD_NAMES}
    for rep in range(repeats):
        order = BUILD_NAMES if rep % 2 == 0 else BUILD_NAMES[::-1]
        for n in COUNTS:
            for b in order:
                raw[b][n].append(run(b, name, framing, n)[0])
    mem = {}
    for b in BUILD_NAMES:
        for n in (1, 200):
            line = next(l for l in run(b, name, framing, n, {'MEM_PEAKS': '1', 'MEM_SETTLE_MS': '0'})[1].splitlines()
                        if l.startswith('MEM baseline'))
            mem[f'{b}_{n}'] = {k: float(v) for k, v in re.findall(r'(\w+)=([\d.]+)', line)}
    rows.append({'name': os.path.basename(name), 'framing': framing, 'raw': raw, 'mem': mem})
    med = lambda v: sorted(v)[len(v) // 2]
    label = f"{os.path.basename(name).replace('corpus__', ''):40s} {framing:4s}"
    for b in BUILD_NAMES:
        print(label, f'{b:6s}', ' '.join(f'run({n}) {med(raw[b][n]) / 1e6:8.2f} M ({min(raw[b][n]) / 1e6:.2f}..{max(raw[b][n]) / 1e6:.2f})'
                                         for n in COUNTS), flush=True)
    for b in BUILD_NAMES:
        for n in (1, 200):
            m = mem[f'{b}_{n}']
            print(label, f'{b:6s}', f"frames {n:3d} graphics after {m['after_graphics'] / 2**20:7.2f} MiB, peak {m['peak_graphics'] / 2**20:7.2f} MiB, "
                  f"passes={m['passes']:.0f} command_buffers={m['command_buffers']:.0f}", flush=True)
    json.dump(rows, open(out, 'w'), indent=1)
