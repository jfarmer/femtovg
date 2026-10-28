#!/usr/bin/env python3
"""Anatomy probe (bin/_logos_full_anat = master cc0d841 + counters + FEMTOVG_TESS_TOL) on the curve-heavy files and
BuseyBench at hd and z1, tolerances 0.25 (master; B has the same counts), 0.125 (C) and 0.0625 (A). FRAMES=3,
counts divided by 3 (geometry is rebuilt every frame by the harness). Writes probe.jsonl."""
import json, os, re, subprocess
OUT = os.path.expanduser('~/src/femtovg-wt/runs/mac-anatomy')
BIN = os.path.expanduser('~/src/femtovg-wt/bin/_logos_full_anat')
HD = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0'}
Z1 = {'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
BASE = {'SINGLE_SHADOW_LAYER': '1', 'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024',
        'FRAMES': '3', 'FEMTOVG_PROBE': '1', 'PROBE_ALLOC': '1'}
CURVY = [('tiger', '/Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg'),
         ('puzzle-fox', '/Users/matt/src/femtovg-wt/da/corpus/firefox/puzzle-fox.svg'),
         ('mr-settodefault', '/Users/matt/src/femtovg-wt/da/mr-settodefault.svg'),
         ('svgenius-icon32', f'{OUT}/files/svgenius_icon32.svg'),
         ('svgenius-icon5', f'{OUT}/files/svgenius_icon5_line.svg')]
files = [x for x in json.load(open(os.path.expanduser('~/src/femtovg-wt/runs/pr/files.json'))) if x['group'] == 'buseybench']
jobs = [(k, p, 'curvy') for k, p in CURVY] + [(x['key'].split('__')[-1], x['path'], 'buseybench') for x in files]
with open(f'{OUT}/probe.jsonl', 'w') as out:
    for key, path, group in jobs:
        for framing, fenv in (('hd', HD), ('z1', Z1)):
            for tol in ('0.25', '0.125', '0.0625'):
                env = {**os.environ, **BASE, **fenv, 'FEMTOVG_TESS_TOL': tol}
                r = subprocess.run([BIN, '1', f'{OUT}/tmp/anat.ppm', path], env=env, capture_output=True, text=True, timeout=600)
                rec = {'file': key, 'group': group, 'framing': framing, 'tol': tol}
                for tag in ('PROBE', 'ALLOC'):
                    m = re.search(rf'^{tag} (.*)$', r.stderr, re.M)
                    if m:
                        for kv in m.group(1).split():
                            k, v = kv.split('=')
                            rec[f'{tag.lower()}_{k}'] = int(v)
                out.write(json.dumps(rec) + '\n'); out.flush()
