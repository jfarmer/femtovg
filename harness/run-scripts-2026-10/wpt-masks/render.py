#!/usr/bin/env python3
"""Render the selected files with one harness binary into png/TAG_KEY_FRAMING.png (resumable).

  render.py TAG BINARY [match=SUBSTR]... [group=NAME]... [framings=z1,z2,z4,hd] [force=1] [ENV=VALUE]...

The corpus-run sweep environment (SKIP_UNSUPPORTED_FILTERS VIEWPORT_CLIP LAYER_STATS TRANSIENT_BUDGET_MB=1024)
and SINGLE_SHADOW_LAYER=1 are always applied; ENV=VALUE pairs add to them."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import FRAMINGS, SWEEP_ENV  # noqa: E402

tag, binary = sys.argv[1:3]
matches, groups, framings, force, extra = [], set(), ['z1', 'z2', 'z4', 'hd'], False, {}
for a in sys.argv[3:]:
    k, v = a.split('=', 1)
    if k == 'match':
        matches.append(v)
    elif k == 'group':
        groups.add(v)
    elif k == 'framings':
        framings = v.split(',')
    elif k == 'force':
        force = v == '1'
    else:
        extra[k] = v
fs = json.load(open(f'{HERE}/files.json'))
fs = [f for f in fs if (not groups or f['group'] in groups) and (not matches or any(m in f['key'] for m in matches))]
os.makedirs(f'{HERE}/png', exist_ok=True)
os.makedirs(f'{HERE}/tmp', exist_ok=True)


def one(job):
    f, framing = job
    png = f'{HERE}/png/{tag}_{f["key"]}_{framing}.png'
    if os.path.exists(png) and not force:
        return 'kept'
    fr, z = FRAMINGS[framing]
    ppm = f'{HERE}/tmp/{tag}_{f["key"]}_{framing}.ppm'
    env = {**os.environ, **fr, **SWEEP_ENV, 'SINGLE_SHADOW_LAYER': '1', **extra}
    r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not os.path.exists(ppm):
        sys.stderr.write(f'FAIL {f["key"]} {framing}: {r.stderr[-300:]}\n')
        return 'failed'
    Image.open(ppm).convert('RGB').save(png)
    os.remove(ppm)
    return 'made'


counts = {}
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(one, [(f, fr) for f in fs for fr in framings]):
        counts[r] = counts.get(r, 0) + 1
print(tag, counts)
