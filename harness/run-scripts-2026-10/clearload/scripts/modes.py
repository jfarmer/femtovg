#!/usr/bin/env python3
"""modes.py DEV : the clear-mode decomposition (run_micro.sh with DIAG=1, tags d-N-MODE) on the empty and
eight-layer frames. Per frame file and phase, each mode's median steady frame: GPU time, reads, writes.
  quad      #368: load the target, draw the clear's quad
  load      load the target, no quad (wrong pixels: the load alone)
  fold      this change: clear on load
  clearquad clear on load and the quad as well (the quad alone, on top of the fold)
so load - fold is what loading the target costs, clearquad - fold what the quad costs."""
import glob, json, os, statistics as st, sys
from collections import defaultdict

dev = sys.argv[1]
d = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/{dev}'
vals = defaultdict(lambda: defaultdict(list))  # (phase, file) -> mode:metric -> values
for path in sorted(glob.glob(f'{d}/frames-d-*.jsonl')):
    mode = path.rsplit('-', 1)[1].split('.')[0]
    for line in open(path):
        r = json.loads(line)
        if r['rep'] < 1 or r.get('gpu_ms') is None:
            continue
        for m in ('gpu_ms', 'read_mb', 'write_mb'):
            if r.get(m) is not None:
                vals[(r['phase'], r['file'])][f'{mode}:{m}'].append(r[m])
for (phase, name), per in sorted(vals.items()):
    print(f'== {dev} {phase} {name}')
    for m in ('gpu_ms', 'read_mb', 'write_mb'):
        med = {mode: st.median(per[f'{mode}:{m}']) for mode in ('quad', 'load', 'fold', 'clearquad')
               if per.get(f'{mode}:{m}')}
        if not med:
            continue
        cells = '  '.join(f'{mode} {v:8.3f}' for mode, v in med.items())
        extra = ''
        if {'load', 'fold', 'clearquad', 'quad'} <= med.keys():
            extra = (f'   load-fold {med["load"] - med["fold"]:+.3f}  clearquad-fold {med["clearquad"] - med["fold"]:+.3f}'
                     f'  quad-fold {med["quad"] - med["fold"]:+.3f}')
        print(f'  {m:8s} {cells}{extra}')
