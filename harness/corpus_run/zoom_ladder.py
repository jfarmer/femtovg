#!/usr/bin/env python3
"""A zoom gesture in and out on one canvas, as an application zooms (#312, #311).

  zoom_ladder.py run BUILD [mode=svg|glyphs|shape] [keys=FILE] [workers=6] [near=24]
  zoom_ladder.py compare BUILD [mode=...] refs=DIR

run: for every file of files.json (with mode=glyphs or shape, every file with text, drawn through femtovg's text
engine: the harness's FEMTOVG_TEXT), the harness draws the default framing at each zoom of LADDER in turn in one
process (ZOOM_LADDER), and a fresh process draws each zoom of it once. A row per file goes to
zoom_<build>_<mode>.jsonl:
  - steps: per step, the zoom, the frame's hash and its difference from the fresh frame of that zoom (pixels that
    differ at all, beyond 8/255, the largest difference): what a step inherits from the zooms drawn before it;
  - z1: the first frame against each browser's frame of the default framing (pixels beyond 8/255 and 20/255, the
    largest difference), where REFS has it;
  - near: the first frame is within 8/255 of a browser but for at most NEAR pixels (24, 0.02 % of the frame).
The step PNGs of a near file, or of a file with a step that differs from its fresh frame, are kept under
png/zl_<build>_<mode>/<key>/ (NN.png per step, fresh_<framing>.png per zoom).

compare: each kept near file's steps against the browsers' frames of each zoom in refs=DIR (made with refs.py
chromium|firefox framings=<every ladder framing> in a run whose files.json holds the near files), into
zoomcmp_<build>_<mode>.jsonl."""
import hashlib, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
from common import *

LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FRAMING_OF = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
              0.33: 'z033', 0.25: 'z025'}
MODES = {'svg': {}, 'glyphs': {'FEMTOVG_TEXT': 'glyphs'}, 'shape': {'FEMTOVG_TEXT': 'shape'}}
BROWSERS = ['chr', 'ff', 'wk']
TMP = f'{OUT}/tmp'
os.makedirs(TMP, exist_ok=True)


def load(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.int16)


def diff(a, b):
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    d = np.abs(a[:h, :w] - b[:h, :w]).max(axis=2)
    return {'any': int((d > 0).sum()), 'n8': int((d > 8).sum()), 'n20': int((d > 20).sum()), 'max': int(d.max())}


def harness(build, mode, path, zoom, ppm, ladder=None):
    binary, extra = BUILDS[build]
    env = {**os.environ, **FRAMINGS['z1'][0], **SWEEP_ENV, **extra, **MODES[mode]}
    if ladder:
        env['ZOOM_LADDER'] = ','.join(f'{z:g}' for z in ladder)
    r = subprocess.run([binary, f'{zoom:g}', ppm, path], env=env, capture_output=True, text=True, timeout=600)
    return r


def run_file(build, mode, f, near):
    tag = f'{os.getpid()}_{abs(hash(f["key"]))}'
    base = f'{TMP}/zl_{tag}.ppm'
    row = {'key': f['key'], 'group': f['group'], 'build': build, 'mode': mode}
    r = harness(build, mode, f['path'], 1, base, LADDER)
    m = re.search(r'text by femtovg: (\d+) unmapped: (\d+) draw errors: (\d+)', r.stderr)
    if m:
        row['text'] = {'femtovg': int(m[1]), 'unmapped': int(m[2]), 'errors': int(m[3])}
    steps = [f'{base}.{i:02}.ppm' for i in range(len(LADDER))]
    if r.returncode != 0 or not all(os.path.exists(s) for s in steps):
        row['error'] = r.stderr.strip()[-400:]
        for s in steps:
            if os.path.exists(s):
                os.remove(s)
        return row
    frames = [load(s) for s in steps]
    fresh = {1: frames[0]}
    fresh_err = {}
    for zoom in sorted(set(LADDER) - {1}):
        ppm = f'{TMP}/zf_{tag}_{FRAMING_OF[zoom]}.ppm'
        rz = harness(build, mode, f['path'], zoom, ppm)
        if rz.returncode == 0 and os.path.exists(ppm):
            fresh[zoom] = load(ppm)
            os.remove(ppm)
        else:
            fresh_err[zoom] = rz.stderr.strip()[-200:]
    if fresh_err:
        row['fresh_errors'] = {f'{z:g}': e for z, e in fresh_err.items()}
    row['steps'] = []
    for i, (zoom, a) in enumerate(zip(LADDER, frames)):
        step = {'zoom': zoom, 'hash': hashlib.sha1(a.tobytes()).hexdigest()[:16]}
        if zoom in fresh:
            step['vs_fresh'] = diff(a, fresh[zoom])
        row['steps'].append(step)
    row['z1'] = {}
    for b in BROWSERS:
        ref = ref_png(b, f['key'], 'z1')
        if os.path.exists(ref):
            row['z1'][b] = diff(frames[0], load(ref))
    best = min((v['n8'] for v in row['z1'].values()), default=None)
    row['near'] = best is not None and best <= near
    row['leaks'] = sum(1 for s in row['steps'] if s.get('vs_fresh', {}).get('any', 0) > 0)
    if row['near'] or row['leaks']:
        d = f'{OUT}/png/zl_{build}_{mode}/{f["key"]}'
        os.makedirs(d, exist_ok=True)
        for i, a in enumerate(frames):
            Image.fromarray(a.astype(np.uint8)).save(f'{d}/{i:02}.png')
        for zoom, a in fresh.items():
            if zoom != 1:
                Image.fromarray(a.astype(np.uint8)).save(f'{d}/fresh_{FRAMING_OF[zoom]}.png')
    for s in steps:
        os.remove(s)
    return row


def has_text(path):
    try:
        return '<text' in open(path, errors='ignore').read()
    except OSError:
        return False


def run(build, opts):
    mode = opts.get('mode', 'svg')
    near = int(opts.get('near', 24))
    fs = files()
    if 'keys' in opts:
        keys = set(json.load(open(opts['keys'])))
        fs = [f for f in fs if f['key'] in keys]
    if mode != 'svg':
        fs = [f for f in fs if has_text(f['path'])]
    path = f'{OUT}/zoom_{build}_{mode}.jsonl'
    done = set()
    if os.path.exists(path):
        done = {json.loads(l)['key'] for l in open(path)}
    todo = [f for f in fs if f['key'] not in done]
    print(f'{build} {mode}: {len(todo)} files to run ({len(done)} done)', flush=True)
    out = open(path, 'a')
    counts = {'near': 0, 'leaks': 0, 'error': 0}
    with ThreadPoolExecutor(int(opts.get('workers', 6))) as ex:
        for i, row in enumerate(ex.map(lambda f: run_file(build, mode, f, near), todo)):
            out.write(json.dumps(row) + '\n')
            out.flush()
            counts['near'] += bool(row.get('near'))
            counts['leaks'] += bool(row.get('leaks'))
            counts['error'] += 'error' in row
            if (i + 1) % 100 == 0:
                print(f'{i + 1}/{len(todo)} {counts}', flush=True)
    print(f'done: {counts}', flush=True)


def compare(build, opts):
    mode = opts.get('mode', 'svg')
    refs = opts['refs']
    rows = [json.loads(l) for l in open(f'{OUT}/zoom_{build}_{mode}.jsonl')]
    out = open(f'{OUT}/zoomcmp_{build}_{mode}.jsonl', 'w')
    for row in rows:
        if not row.get('near'):
            continue
        d = f'{OUT}/png/zl_{build}_{mode}/{row["key"]}'
        res = {'key': row['key'], 'group': row['group'], 'steps': []}
        cache = {}
        for i, zoom in enumerate(LADDER):
            fr = FRAMING_OF[zoom]
            a = load(f'{d}/{i:02}.png')
            step = {'zoom': zoom}
            for b in BROWSERS:
                ref = f'{refs}/{b}_{row["key"]}_{fr}.png'
                if os.path.exists(ref):
                    if (b, fr) not in cache:
                        cache[(b, fr)] = load(ref)
                    step[b] = diff(a, cache[(b, fr)])
            if ('chr', fr) in cache and ('ff', fr) in cache:
                step['chr_ff'] = diff(cache[('chr', fr)], cache[('ff', fr)])
            res['steps'].append(step)
        out.write(json.dumps(res) + '\n')
    out.close()


if __name__ == '__main__':
    cmd, build = sys.argv[1:3]
    opts = dict(a.split('=', 1) for a in sys.argv[3:])
    {'run': run, 'compare': compare}[cmd](build, opts)
