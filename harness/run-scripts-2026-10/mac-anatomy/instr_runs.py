#!/usr/bin/env python3
"""Instructions and cycles per frame on the E-cores (taskpolicy -c background), as instr.py: a long run minus a short
run under /usr/bin/time -l, divided by the frame difference. Variants alternate inside each repeat. Appends instr.jsonl.
usage: instr_runs.py [repeats]"""
import json, os, re, subprocess, sys
OUT = os.path.expanduser('~/src/femtovg-wt/runs/mac-anatomy')
BIN = os.path.expanduser('~/src/femtovg-wt/bin')
ENV = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SINGLE_SHADOW_LAYER': '1',
       'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024'}
FILES = {'tiger': ('/Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg', 20, 220),
         'puzzle-fox': ('/Users/matt/src/femtovg-wt/da/corpus/firefox/puzzle-fox.svg', 50, 650),
         'mr-settodefault': ('/Users/matt/src/femtovg-wt/da/mr-settodefault.svg', 40, 440),
         'svgenius-icon32': (f'{OUT}/files/svgenius_icon32.svg', 100, 1100),
         'svgenius-icon5': (f'{OUT}/files/svgenius_icon5_line.svg', 100, 1100)}
VARS = ['m7', 'm7f', 'fb', 'fc']
def run(v, path, frames):
    env = {**os.environ, **ENV, 'FRAMES': str(frames)}
    r = subprocess.run(['/usr/bin/time', '-l', '/usr/sbin/taskpolicy', '-c', 'background', f'{BIN}/_logos_full_{v}', '1',
                        f'{OUT}/tmp/instr_{v}.ppm', path], env=env, capture_output=True, text=True)
    g = lambda name: int(re.search(r'(\d+)\s+' + name, r.stderr).group(1))
    return g('instructions retired'), g('cycles elapsed')
reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
with open(f'{OUT}/instr.jsonl', 'a') as out:
    for rep in range(reps):
        for fk, (path, lo, hi) in FILES.items():
            for v in (VARS if rep % 2 == 0 else VARS[::-1]):
                (i0, c0), (i1, c1) = run(v, path, lo), run(v, path, hi)
                rec = {'file': fk, 'variant': v, 'rep': rep, 'instr': (i1 - i0) / (hi - lo), 'cycles': (c1 - c0) / (hi - lo)}
                out.write(json.dumps(rec) + '\n'); out.flush()
