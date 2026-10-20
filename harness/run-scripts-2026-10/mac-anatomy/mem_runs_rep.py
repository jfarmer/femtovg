#!/usr/bin/env python3
"""MEM_PEAKS=1 FRAMES=3 for m7, m7f, fb, fc on every BuseyBench file and the curve-heavy files, at hd and z1.
One process per (file, framing, variant); variants interleaved per file. Appends JSON lines to mem.jsonl."""
import json, os, re, subprocess, sys
BIN = os.path.expanduser('~/src/femtovg-wt/bin')
OUT = os.path.expanduser('~/src/femtovg-wt/runs/mac-anatomy')
VARIANTS = ['m7#2', 'm7f#2', 'm7#3', 'm7f#3']
HD = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0'}
Z1 = {'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
BASE = {'SINGLE_SHADOW_LAYER': '1', 'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024',
        'MEM_PEAKS': '1', 'FRAMES': '3'}
files = [x for x in json.load(open(os.path.expanduser('~/src/femtovg-wt/runs/pr/files.json'))) if x['group'] == 'buseybench']
CURVY = [('tiger', '/Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg'),
         ('puzzle-fox', '/Users/matt/src/femtovg-wt/da/corpus/firefox/puzzle-fox.svg'),
         ('mr-settodefault', '/Users/matt/src/femtovg-wt/da/mr-settodefault.svg'),
         ('svgenius-icon32', f'{OUT}/files/svgenius_icon32.svg'),
         ('svgenius-icon5', f'{OUT}/files/svgenius_icon5_line.svg')]
jobs = [(x['key'].split('__')[-1], x['path'], 'buseybench') for x in files] + [(k, p, 'curvy') for k, p in CURVY]
done = set()
if os.path.exists(f'{OUT}/mem.jsonl'):
    for l in open(f'{OUT}/mem.jsonl'):
        r = json.loads(l); done.add((r['file'], r['framing'], r['variant']))
with open(f'{OUT}/mem.jsonl', 'a') as out:
    for key, path, group in jobs:
        for framing, fenv in (('hd', HD), ('z1', Z1)):
            for v in VARIANTS:
                if (key, framing, v) in done:
                    continue
                env = {**os.environ, **BASE, **fenv}
                r = subprocess.run([f'{BIN}/_logos_full_{v.split("#")[0]}', '1', f'{OUT}/tmp/mem_r.ppm', path], env=env,
                                   capture_output=True, text=True, timeout=600)
                m = re.search(r'^MEM (.*)$', r.stderr, re.M)
                rec = {'file': key, 'group': group, 'framing': framing, 'variant': v, 'rc': r.returncode}
                if m:
                    for kv in m.group(1).split():
                        k, val = kv.split('=')
                        rec[k] = float(val) if '.' in val else int(val)
                out.write(json.dumps(rec) + '\n'); out.flush()
