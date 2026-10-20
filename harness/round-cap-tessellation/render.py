#!/usr/bin/env python3
"""render.py TAG [ENV=VAL ...] [keys=a,b] [group=G] [frs=z1,z2,hd] [jobs=4]: renders files.json of $CORPUS_RUN_OUT with
the harness binary of TAG into $CORPUS_RUN_OUT/png/TAG_KEY_FR.png, with the corpus sweep's environment (SWEEP_ENV).
TAG: mstc = master 06243b80 (bin-caps/_logos_full_mstc), caps = the prototype (bin-caps/_logos_full_caps); a tag
of the form capx<m> runs bin-caps/_logos_full_capx with FEMTOVG_CAP_MODE=<m> (0 master, 1 chords from the rim
radius, 2 chords from the half width; both of the last with one more point than chords)."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
OUT = os.environ['CORPUS_RUN_OUT']
BIN = os.environ.get('HARNESS_BIN', os.path.expanduser('~/src/femtovg-wt/bin-caps'))
DEFAULT = {'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
HD = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0'}
FR = {'z1': (DEFAULT, 1.0), 'z2': (DEFAULT, 2.0), 'hd': (HD, 1.0)}
SWEEP = {'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'LAYER_STATS': '1', 'TRANSIENT_BUDGET_MB': '1024'}
tag = sys.argv[1]
extra, opts = {}, {'frs': 'z1,z2,hd', 'jobs': '4'}
for a in sys.argv[2:]:
    k, v = a.split('=', 1)
    (opts if k in ('keys', 'group', 'frs', 'jobs') else extra).__setitem__(k, v)
if tag.startswith('capx'):
    binary = f'{BIN}/_logos_full_capx'; extra['FEMTOVG_CAP_MODE'] = tag[4:]
else:
    binary = f'{BIN}/_logos_full_{tag}'
fs = json.load(open(f'{OUT}/files.json'))
if 'keys' in opts: fs = [f for f in fs if f['key'] in opts['keys'].split(',')]
if 'group' in opts: fs = [f for f in fs if f['group'] in opts['group'].split(',')]
os.makedirs(f'{OUT}/png', exist_ok=True)


def job(a):
    f, fr = a
    png = f'{OUT}/png/{tag}_{f["key"]}_{fr}.png'
    if os.path.exists(png): return 'kept'
    env, z = FR[fr]
    ppm = png[:-4] + '.ppm'
    r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env={**os.environ, **env, **SWEEP, **extra}, capture_output=True, text=True, timeout=900)
    if not os.path.exists(ppm): return f'failed {f["key"]} {fr} rc={r.returncode} {r.stderr[-300:]}'
    Image.open(ppm).save(png); os.remove(ppm)
    return 'made'


with ThreadPoolExecutor(int(opts['jobs'])) as ex:
    res = list(ex.map(job, [(f, fr) for f in fs for fr in opts['frs'].split(',')]))
import collections
print(tag, collections.Counter(r if not r.startswith('failed') else 'failed' for r in res))
for r in res:
    if r.startswith('failed'): print(r)
