#!/usr/bin/env python3
"""clearstats.py BUILD FRAMING... : renders every corpus file (CORPUS_RUN_OUT/files.json) at each framing with
the instrumented build (CLEARSTAT lines on stderr) and writes clearstats_FRAMING.jsonl: per frame, the clears
folded into a load op and those drawn as a quad (and why), with each target's size."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import *  # noqa: F401,F403

build, framings = sys.argv[1], sys.argv[2:]
binary, extra = BUILDS[build]
TMP = f'{OUT}/tmp'
os.makedirs(TMP, exist_ok=True)


def one(args):
    f, framing = args
    fr, z = FRAMINGS[framing]
    ppm = f'{TMP}/cs_{os.getpid()}_{abs(hash((f["key"], framing)))}.ppm'
    r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra},
                       capture_output=True, timeout=600, text=True, errors='replace')
    if os.path.exists(ppm):
        os.remove(ppm)
    folds, quads = [], []
    for line in r.stderr.splitlines():
        if not line.startswith('CLEARSTAT '):
            continue
        p = line.split()
        if p[1] == 'fold':
            folds.append((p[2], p[3]))
        else:
            quads.append((p[2], p[3], p[4], p[6] if len(p) > 6 else ''))
    return {'key': f['key'], 'framing': framing, 'rc': r.returncode, 'folds': folds, 'quads': quads}


for framing in framings:
    jobs = [(f, framing) for f in files()]
    with ThreadPoolExecutor(6) as ex, open(f'{OUT}/clearstats_{framing}.jsonl', 'w') as out:
        for row in ex.map(one, jobs):
            out.write(json.dumps(row) + '\n')
    print(framing, len(jobs), 'frames')
