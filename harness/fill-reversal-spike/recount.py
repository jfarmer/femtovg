#!/usr/bin/env python3
"""Recount corpus_ab.py's moved frames against the references, looking in each run's refs/ and then in extra
reference directories (references made afterwards for frames whose run had none), from the frames corpus_ab.py kept.

  recount.py AB.jsonl OUT.jsonl EXTRA_REFS_DIR..."""
import json, os, sys
import numpy as np
from PIL import Image

RUNS = os.path.expanduser('~/src/femtovg-wt/runs')
SETS = {'busey': 'busey', 'wasmx': 'wasmx', 'wpt22': 'wpt22'}
src, out, extra = sys.argv[1], sys.argv[2], sys.argv[3:]
base = os.path.dirname(os.path.abspath(src))


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def ref(b, key, framing, run):
    for d in [f'{RUNS}/{run}/refs'] + extra:
        p = f'{d}/{b}_{key}_{framing}.png'
        if os.path.exists(p):
            return load(p)
    return None


def counts(im, refs):
    o, masks = {}, {}
    for b, r in refs.items():
        h, w = min(r.shape[0], im.shape[0]), min(r.shape[1], im.shape[1])
        masks[b] = np.abs(im[:h, :w] - r[:h, :w]).max(axis=2) > 20
        o[b] = int(masks[b].sum())
    if all(b in masks for b in ('chr', 'ff', 'wk')):
        o['off3'] = int((masks['chr'] & masks['ff'] & masks['wk']).sum())
    return o


with open(out, 'w') as f:
    for line in open(src):
        r = json.loads(line)
        if r.get('moved'):
            run = SETS[r['set']]
            refs = {b: x for b in ('chr', 'ff', 'wk', 'id') if (x := ref(b, r['key'], r['framing'], run)) is not None}
            m = load(f"{base}/png/master/{r['key']}_{r['framing']}.png")
            a = load(f"{base}/png/{r['variant']}/{r['key']}_{r['framing']}.png")
            r['before'], r['after'] = counts(m, refs), counts(a, refs)
        f.write(json.dumps(r) + '\n')
