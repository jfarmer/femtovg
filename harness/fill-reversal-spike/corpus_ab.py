#!/usr/bin/env python3
"""Which frames a variant moves, and whether toward or away from the browsers, over three frame sets.

  corpus_ab.py OUT.jsonl VARIANT [VARIANT...] [jobs=N] [sets=busey,wasmx,wpt22]

Sets (each run's files.json and refs/; the master hash of every frame from that run's accuracy.jsonl):
  busey  ~/src/femtovg-wt/runs/busey: the 36 BuseyBench portraits at z1, z2, hd (build mst4)
  wasmx  ~/src/femtovg-wt/runs/wasmx: the corpus and WPT-derived reftest groups at z1, z2, hd (build mst4n, a link
         to mst4) - the 1,243 files of that run's master pass
  wpt22  ~/src/femtovg-wt/runs/wpt22: the 780 wpt22 reftest files at z1, z2, z4, hd (build mst4)
Each frame is rendered with the variant (render.py VARIANTS) and hashed as accuracy.py hashes (sha1 of the PPM). A
frame whose hash differs from the stored master hash is rendered with master again (a master that does not
reproduce its own stored hash is flagged) and both are compared with the references: pixels more than 20/255 off
Chromium (chr), and where references exist Firefox (ff), WebKit (wk), the 8x area reference (id), and off all three
browsers (off3). One row per frame and variant; the master frame and the variant frame of every moved frame are kept
under OUT's directory in png/<variant>/ and png/master/."""
import hashlib, json, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus_run'))
from common import FRAMINGS, SWEEP_ENV  # noqa: E402
sys.path.insert(0, HERE)
from render import VARIANTS  # noqa: E402

RUNS = os.path.expanduser('~/src/femtovg-wt/runs')
SETS = {'busey': ('busey', 'mst4'), 'wasmx': ('wasmx', 'mst4n'), 'wpt22': ('wpt22', 'mst4')}


def jobs_for(name):
    run, build = SETS[name]
    paths = {f['key']: f['path'] for f in json.load(open(f'{RUNS}/{run}/files.json'))}
    seen = {}
    for line in open(f'{RUNS}/{run}/accuracy.jsonl'):
        r = json.loads(line)
        if r['build'] == build and r.get('hash'):
            seen[(r['key'], r['framing'])] = r['hash']
    return [(name, k, fr, paths[k], h) for (k, fr), h in sorted(seen.items())]


def render(variant, svg, framing, tag, tmp):
    binary, extra = VARIANTS[variant]
    fr, z = FRAMINGS[framing]
    ppm = f'{tmp}/{tag}_{os.getpid()}.ppm'
    env = {**os.environ, **fr, **SWEEP_ENV, **extra}
    r = subprocess.run([binary, f'{z:g}', ppm, svg], env=env, capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not os.path.exists(ppm):
        return None, None
    data = open(ppm, 'rb').read()
    im = np.asarray(Image.open(ppm).convert('RGB'), dtype=np.int16)
    os.remove(ppm)
    return hashlib.sha1(data).hexdigest(), im


def counts(im, run, key, framing):
    out, masks = {}, {}
    for b in ('chr', 'ff', 'wk', 'id'):
        p = f'{RUNS}/{run}/refs/{b}_{key}_{framing}.png'
        if os.path.exists(p):
            ref = np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
            h, w = min(ref.shape[0], im.shape[0]), min(ref.shape[1], im.shape[1])
            m = np.abs(im[:h, :w] - ref[:h, :w]).max(axis=2) > 20
            masks[b] = m
            out[b] = int(m.sum())
    if all(b in masks for b in ('chr', 'ff', 'wk')):
        out['off3'] = int((masks['chr'] & masks['ff'] & masks['wk']).sum())
    return out


def one(job):
    (name, key, framing, svg, master_hash), variant, base = job
    tmp, png = f'{base}/tmp', f'{base}/png'
    run = SETS[name][0]
    row = {'set': name, 'key': key, 'framing': framing, 'variant': variant, 'master_hash': master_hash}
    h, im = render(variant, svg, framing, variant, tmp)
    row['hash'] = h
    if h is None:
        row['error'] = True
        return row
    row['moved'] = h != master_hash
    if row['moved']:
        mh, mim = render('master', svg, framing, 'master', tmp)
        row['master_reproduced'] = mh == master_hash
        row['moved_vs_fresh_master'] = h != mh
        row['before'] = counts(mim, run, key, framing)
        row['after'] = counts(im, run, key, framing)
        for tag, a in (('master', mim), (variant, im)):
            d = f'{png}/{tag}'
            os.makedirs(d, exist_ok=True)
            Image.fromarray(a.astype(np.uint8)).save(f'{d}/{key}_{framing}.png')
    return row


if __name__ == '__main__':
    args = sys.argv[1:]
    out = args.pop(0)
    n = int(next((a.split('=')[1] for a in args if a.startswith('jobs=')), '6'))
    sets = next((a.split('=')[1].split(',') for a in args if a.startswith('sets=')), list(SETS))
    variants = [a for a in args if '=' not in a]
    base = os.path.dirname(os.path.abspath(out))
    os.makedirs(f'{base}/tmp', exist_ok=True)
    done = set()
    if os.path.exists(out):
        for line in open(out):
            r = json.loads(line)
            done.add((r['set'], r['key'], r['framing'], r['variant']))
    todo = [(j, v, base) for v in variants for s in sets for j in jobs_for(s) if (s, j[1], j[2], v) not in done]
    print(f'{len(todo)} renders', flush=True)
    with open(out, 'a') as f, Pool(n) as pool:
        for i, row in enumerate(pool.imap_unordered(one, todo, chunksize=4)):
            f.write(json.dumps(row) + '\n')
            f.flush()
            if i % 500 == 0:
                print(i, flush=True)
