#!/usr/bin/env python3
"""stats.py BUILD [framings=z1,hd] [workers=3] : render every corpus file with BUILD (the stencil-stats harness)
and STENCIL_STATS=1, and collect per frame what its flushes printed: passes on drawable targets, filter passes,
passes that attach a stencil, of those how many load and store it, distinct targets and distinct stencils.
Writes stats_BUILD.jsonl beside this script."""
import json, os, re, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import *  # noqa: E402,F403

build = sys.argv[1]
opts = dict(x.split('=', 1) for x in sys.argv[2:])
framings = opts.get('framings', 'z1,hd').split(',')
workers = int(opts.get('workers', 3))
HERE = os.path.dirname(os.path.abspath(__file__))
LINE = re.compile(r'STENCIL passes=(\d+) filter=(\d+) attached=(\d+) loads=(\d+) stores=(\d+) targets=(\d+) stencils=(\d+)')


def run(job):
    f, framing = job
    binary, extra = BUILDS[build]
    fr, z = FRAMINGS[framing]
    ppm = f'{HERE}/tmp/stats_{os.getpid()}_{threading.get_ident()}.ppm'
    env = {**os.environ, **fr, **SWEEP_ENV, **extra, 'STENCIL_STATS': '1'}
    r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env=env, capture_output=True, text=True, timeout=600)
    if os.path.exists(ppm):
        os.remove(ppm)
    flushes = [tuple(map(int, m.groups())) for m in LINE.finditer(r.stderr)]
    total = [sum(col) for col in zip(*flushes)] if flushes else [0] * 7
    return {'key': f['key'], 'framing': framing, 'flushes': len(flushes), 'rc': r.returncode,
            'passes': total[0], 'filter': total[1], 'attached': total[2], 'loads': total[3], 'stores': total[4],
            'targets_max': max((fl[5] for fl in flushes), default=0),
            'stencils_max': max((fl[6] for fl in flushes), default=0)}


jobs = [(f, framing) for f in files() for framing in framings]
with open(f'{HERE}/stats_{build}.jsonl', 'w') as out, ThreadPoolExecutor(workers) as pool:
    for i, row in enumerate(pool.map(run, jobs)):
        out.write(json.dumps(row) + '\n')
        if i % 200 == 0:
            print(i, 'of', len(jobs), flush=True)
print('done', len(jobs))
