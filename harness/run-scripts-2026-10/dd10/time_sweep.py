#!/usr/bin/env python3
"""time_sweep.py BUILD,BUILD,... keys=FILE [rounds=3] [frames=40] [framing=hd]  (run through tool.py)

Per file, the builds in rotating order, `rounds` times: the harness's frame_ms and encode_ms (MEM_PEAKS=1) over
`frames` frames. Appends to time_sweep.jsonl; resumable by (key, build, round)."""
import json, os, re, subprocess, sys
from common import *
builds = sys.argv[1].split(',')
opts = dict(a.split('=', 1) for a in sys.argv[2:])
keys = json.load(open(opts['keys']))
rounds, frames, framing = int(opts.get('rounds', 3)), opts.get('frames', '40'), opts.get('framing', 'hd')
by_key = {f['key']: f for f in files()}
path = f'{OUT}/time_sweep.jsonl'
done = set()
if os.path.exists(path):
    for l in open(path):
        r = json.loads(l); done.add((r['key'], r['build'], r['round'], r['framing']))
out = open(path, 'a')
fr, z = FRAMINGS[framing]
for i, key in enumerate(keys):
    for rnd in range(rounds):
        order = builds[rnd % len(builds):] + builds[:rnd % len(builds)]
        for b in order:
            if (key, b, rnd, framing) in done:
                continue
            binary, extra = BUILDS[b]
            env = {**os.environ, **fr, **SWEEP_ENV, **extra, 'MEM_PEAKS': '1', 'FRAMES': frames}
            r = subprocess.run([binary, f'{z:g}', f'{OUT}/tmp/time_{b}.ppm', by_key[key]['path']], env=env, capture_output=True, text=True, timeout=600)
            m = re.search(r'frame_ms=([\d.]+).*encode_ms=([\d.]+)', r.stderr)
            row = {'key': key, 'build': b, 'round': rnd, 'framing': framing,
                   'frame_ms': float(m.group(1)) if m else None, 'encode_ms': float(m.group(2)) if m else None}
            out.write(json.dumps(row) + '\n'); out.flush()
    if i % 20 == 0:
        print(i, len(keys), flush=True)
print('done', flush=True)
