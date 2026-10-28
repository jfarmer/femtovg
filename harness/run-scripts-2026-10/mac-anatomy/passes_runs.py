#!/usr/bin/env python3
"""Per-pass instructions and cycles per frame (bin/_logos_full_anat2: master + thread_selfcounts spans, FEMTOVG_PASSES=1)
on the E-cores, frames 1..N-1 (frame 0 warms up), tolerances 0.25 / 0.125 / 0.0625, REPEATS alternating.
Writes passes.jsonl."""
import json, os, re, subprocess, sys
OUT = os.path.expanduser('~/src/femtovg-wt/runs/mac-anatomy')
BIN = os.path.expanduser('~/src/femtovg-wt/bin/_logos_full_anat2')
HD = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0'}
Z1 = {'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
BASE = {'SINGLE_SHADOW_LAYER': '1', 'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024',
        'FEMTOVG_PASSES': '1', 'FEMTOVG_PROBE': '1'}
FILES = [('tiger', '/Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg', 41),
         ('puzzle-fox', '/Users/matt/src/femtovg-wt/da/corpus/firefox/puzzle-fox.svg', 101),
         ('mr-settodefault', '/Users/matt/src/femtovg-wt/da/mr-settodefault.svg', 101),
         ('svgenius-icon32', f'{OUT}/files/svgenius_icon32.svg', 201),
         ('svgenius-icon5', f'{OUT}/files/svgenius_icon5_line.svg', 201)]
reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
which = sys.argv[2].split(',') if len(sys.argv) > 2 else None
with open(f'{OUT}/passes.jsonl', 'a') as out:
    for rep in range(reps):
        for key, path, frames in FILES:
            if which and key not in which:
                continue
            for framing, fenv in (('hd', HD), ('z1', Z1)):
                tols = ['0.25', '0.125', '0.0625']
                for tol in (tols if rep % 2 == 0 else tols[::-1]):
                    env = {**os.environ, **BASE, **fenv, 'FEMTOVG_TESS_TOL': tol, 'FRAMES': str(frames)}
                    r = subprocess.run(['/usr/sbin/taskpolicy', '-c', 'background', BIN, '1', f'{OUT}/tmp/anat2.ppm', path],
                                       env=env, capture_output=True, text=True, timeout=900)
                    m = re.search(r'^PASSES (.*)$', r.stderr, re.M)
                    rec = {'file': key, 'framing': framing, 'tol': tol, 'rep': rep, 'frames': frames - 1}
                    if m:
                        for kv in m.group(1).split():
                            k, v = kv.split('=')
                            if '/' in v:
                                c, i, cy = (int(x) for x in v.split('/'))
                                rec[k] = [c, i, cy]
                            else:
                                rec[k] = int(v)
                    out.write(json.dumps(rec) + '\n'); out.flush()
