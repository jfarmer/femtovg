#!/usr/bin/env python3
"""Pixels more than 8/255 off each browser's frame (Chromium/Firefox/WebKit; '-' where no frame was taken), per
ladder step, for master 06243b80 and the prototype. Frames: frames/<master|prototype>/<name>/NN.png (render_ladder.py)."""
import os, sys
import numpy as np
from PIL import Image
CORPUS_RUN = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'corpus_run')  # harness/corpus_run on demo-assets
sys.path.insert(0, CORPUS_RUN if os.path.isdir(CORPUS_RUN) else os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from zoom_ladder import LADDER, FRAMING_OF
Z = os.path.expanduser('~/src/femtovg-wt/runs/zoom')
HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = {'miter-acute': 'wpt22__21-degenerate-paths-dashes-and-joins__wpt-2d-line-miter-acute',
        'mask-thin': 'corpus__wpt__tests__mask-on-thin-stroked-path-userspaceonuse'}
for copy in ('framed_mask-on-thin-stroked-path-userspaceonuse', 'framed_mask-on-thin-stroked-path-userspaceonuse-ref',
             'refs_mask-on-thin-stroked-path-userspaceonuse-expected', 'refs_mask-on-thin-stroked-path-userspaceonuse-ref'):
    KEYS[copy] = 'corpus__wpt__' + copy.replace('_', '__', 1)


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None


def n8(a, b):
    return int((np.abs(a - b).max(axis=2) > 8).sum())


print('px more than 8/255 off Chromium 131 / Firefox 159 / WebKit (macOS 27.2) at each zoom (-: no browser frame at that zoom).')
print('master = femtovg 06243b80; prototype = 06243b80 + prototype.patch; harness default framing (460 x 260), the 21 steps drawn in one process.')
for name, key in KEYS.items():
    print(f'{name} ({key})')
    for s, z in enumerate(LADDER):
        row = []
        for build in ('master', 'prototype'):
            f = load(f'{HERE}/frames/{build}/{name}/{s:02}.png')
            row.append(build + ' ' + '/'.join(
                str(n8(f, r)) if (r := load(f'{Z}/fresh/refs/{b}_{key}_{FRAMING_OF[z]}.png')) is not None else '-'
                for b in ('chr', 'ff', 'wk')))
        print(f'  step {s + 1:2} zoom {z:<4g} ' + '   '.join(row))
chrome = load(f'{HERE}/repro_chr.png')
print('repro.svg at 1 against Chromium: ' + '   '.join(f'{b} {n8(load(f"{HERE}/frames/{b}/repro/00.png"), chrome)}'
                                                     for b in ('master', 'prototype')))
