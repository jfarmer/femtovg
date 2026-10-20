#!/usr/bin/env python3
"""Clip census: what each clip_path call of a corpus file becomes, at the given framings (a build that prints
CLIPCENSUS lines). census.py z1 [z2 ...]"""
import json, os, subprocess, sys, collections
sys.path.insert(0, '/Users/matt/src/femtovg-wt/da/harness/corpus_run')
os.environ.setdefault('CORPUS_RUN_OUT', os.path.dirname(os.path.abspath(__file__)))
from common import FRAMINGS, SWEEP_ENV
B = '/Users/matt/src/femtovg-wt/bin/_logos_full_census'
files = json.load(open(os.path.join(os.environ['CORPUS_RUN_OUT'], 'files.json')))
for framing in sys.argv[1:]:
    fr, z = FRAMINGS[framing]
    total = collections.Counter(); by_group = collections.defaultdict(collections.Counter); with_clips = 0
    for f in files:
        if f['group'] == 'clip-probes' or 'clip' not in open(f['path'], errors='replace').read(): continue
        r = subprocess.run([B, f'{z:g}', '/tmp/census.ppm', f['path']], env={**os.environ, **fr, **SWEEP_ENV}, capture_output=True, text=True, timeout=300)
        kinds = [l.split()[1] for l in r.stderr.splitlines() if l.startswith('CLIPCENSUS')]
        if kinds: with_clips += 1
        total.update(kinds); by_group[f['group']].update(kinds)
    print(framing, 'files with clips', with_clips, 'clips', sum(total.values()), dict(total))
    for g, c in sorted(by_group.items(), key=lambda kv: -sum(kv[1].values())): print('   ', g, dict(c))
