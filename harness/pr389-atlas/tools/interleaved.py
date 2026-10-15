#!/usr/bin/env python3
"""interleaved.py OUT.json REPEATS BUILD_A BUILD_B -- KEY:FRAMING ...   (KEY is a corpus key or a path to an SVG)

Instructions retired per frame once warm, taken as instr_framing.py takes them ((run of 1200 frames - run of 200
frames) / 1000, the same environment), with one difference: instr_framing.py measures all the repeats of one build and
then all of the next, and this alternates the two builds inside each repeat (the build that goes first alternates
between repeats) and reports the difference B - A of each repeat. A change of the machine's state during the run then
falls on both builds.

BUILD_A may equal BUILD_B: the paired differences of one build against itself are what this measurement shows when
nothing differs."""
import json, os, re, subprocess, sys

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'corpus_run'))
from common import BUILDS, FRAMINGS, SWEEP_ENV, files

HERE = os.path.dirname(os.path.abspath(__file__))
BY_KEY = {f['key']: f['path'] for f in files()}
out, repeats, a, b, sep, *jobs = sys.argv[1:]
assert sep == '--'
repeats = int(repeats)
med = lambda v: sorted(v)[len(v) // 2]


def run(build, key, framing, frames):
    binary, extra = BUILDS[build]
    fr, z = FRAMINGS[framing]
    ppm = f'{os.environ["CORPUS_RUN_OUT"]}/tmp/instr_{os.getpid()}.ppm'
    r = subprocess.run(['/usr/bin/time', '-l', binary, f'{z:g}', ppm, BY_KEY.get(key, key)], capture_output=True, text=True,
                       env={**os.environ, **fr, **SWEEP_ENV, **extra, 'FRAMES': str(frames)})
    if os.path.exists(ppm):
        os.remove(ppm)
    return int(re.search(r'(\d+)\s+instructions retired', r.stderr).group(1))


def steady(build, key, framing):
    i200, i1200 = run(build, key, framing, 200), run(build, key, framing, 1200)
    return (i1200 - i200) / 1000, i200


rows = []
for job in jobs:
    key, framing = job.rsplit(':', 1)
    va, vb, s200 = [], [], []
    for rep in range(repeats):
        if rep % 2 == 0:
            (x, xa), (y, yb) = steady(a, key, framing), steady(b, key, framing)
        else:
            (y, yb), (x, xa) = steady(b, key, framing), steady(a, key, framing)
        va.append(x); vb.append(y); s200.append((xa, yb))
    d = [100 * (y - x) / x for x, y in zip(va, vb)]
    row = {'key': key, 'framing': framing, 'a': a, 'b': b, 'a_steady': va, 'b_steady': vb, 'runs_of_200': s200,
           'paired_diff_pct': d, 'median_diff_pct': med(d), 'positive': sum(x > 0 for x in d), 'repeats': repeats}
    rows.append(row)
    print(f"{os.path.basename(key).replace('corpus__', ''):30s} {framing:3s} {a} {med(va) / 1e6:.3f} M ({min(va) / 1e6:.3f}..{max(va) / 1e6:.3f})  "
          f"{b} {med(vb) / 1e6:.3f} M ({min(vb) / 1e6:.3f}..{max(vb) / 1e6:.3f})  paired {b} - {a}: median {med(d):+.2f} % "
          f"({min(d):+.2f}..{max(d):+.2f}), {row['positive']} of {repeats} positive", flush=True)
    print('    per repeat, %:', ' '.join(f'{x:+.2f}' for x in d), flush=True)
    json.dump(rows, open(out, 'w'), indent=1)
