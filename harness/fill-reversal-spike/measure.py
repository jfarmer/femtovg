#!/usr/bin/env python3
"""Numbers for the hairpin spike: pixels more than 20/255 off the browsers and the 8x area reference, and ink against
the area reference in a window on each turn, for the reductions and glm-5v-turbo's ears.

  measure.py RUN [BUSEY_REFS]

RUN holds the frames render.py wrote (png/red/<variant>_<name>_<framing>.png, png/port/<variant>_glm-5v-turbo_<framing>.png)
and the reductions' references (refs/{chr,ff,wk,id}_frs__<name>_<framing>.png from corpus_run/refs.py, refs_webkit.py
and refs_ideal.py). BUSEY_REFS holds the portrait's (refs/{chr,ff,wk,id}_corpus__buseybench__glm-5v-turbo_<framing>.png).
Writes RUN/measure.json and prints a table.

Ink is the darkness of a black fill on white summed over a window, (255 - grey) / 255, in pixels. On the portrait the
ear is light on a dark background, so there it is the summed |frame - area reference| / 255 instead (excess off the
area). Windows are 30 x 16 px at z2 and hd and 16 x 10 at z1, on the turn: the frame transform of a 1024-unit viewBox
is x = 30 + 0.390625 u, y = -70 + 0.390625 v at z2, 130 + 0.1953125 u, 30 + 0.1953125 v at z1, and 420 + 1.0546875 u,
1.0546875 v at hd."""
import json, os, sys
import numpy as np
from PIL import Image

RUN = sys.argv[1]
BUSEY = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/src/femtovg-wt/runs/busey/refs')
VARIANTS = ('master', 'after', 'anyof')
FRAME = {'z1': (130, 30, 0.1953125), 'z2': (30, -70, 0.390625), 'hd': (420, 0, 1.0546875)}
HALF = {'z1': (8, 5), 'z2': (15, 8), 'hd': (15, 8)}
# The turn in user units: the ear's leftmost hook point (the turnaround at u 248.9, v 465), the right ear's mirror,
# and the cusp's point (512, 415).
TURNS = {'ear': [(250.0, 465.0)], 'ear-no-reversal': [(250.0, 465.0)], 'cusp': [(512.0, 415.0)],
         'glm-5v-turbo': [(250.0, 465.0), (774.0, 465.0)]}


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def windows(name, fr):
    x0, y0, s = FRAME[fr]
    hw, hh = HALF[fr]
    out = []
    for u, v in TURNS[name]:
        cx, cy = int(round(x0 + s * u)), int(round(y0 + s * v))
        out.append((slice(cy - hh, cy + hh), slice(cx - hw, cx + hw)))
    return out


def off(a, b):
    return np.abs(a - b).max(axis=2) > 20


def ink(im):
    return (255.0 - im.mean(axis=2)) / 255.0


def stats(frame, refs, wins, light):
    m3 = off(frame, refs['chr']) & off(frame, refs['ff']) & off(frame, refs['wk'])
    mid = off(frame, refs['id'])
    win = np.zeros(m3.shape, bool)
    for w in wins:
        win[w] = True
    if light:
        excess = np.abs(frame - refs['id']).mean(axis=2) / 255.0
        win_ink = float(excess[win].sum())
    else:
        win_ink = float(ink(frame)[win].sum())
    return {'off_chr': int(off(frame, refs['chr']).sum()), 'off3': int(m3.sum()), 'off_id': int(mid.sum()),
            'off3_win': int((m3 & win).sum()), 'off_id_win': int((mid & win).sum()), 'win_ink': round(win_ink, 2)}


def main():
    out = {'reductions': {}, 'portrait': {}}
    for name in ('ear', 'ear-no-reversal', 'cusp'):
        for fr in ('z1', 'z2', 'hd'):
            refs = {b: load(f'{RUN}/refs/{b}_frs__{name}_{fr}.png') for b in ('chr', 'ff', 'wk', 'id')}
            wins = windows(name, fr)
            row = {v: stats(load(f'{RUN}/png/red/{v}_{name}_{fr}.png'), refs, wins, False) for v in VARIANTS}
            area = float(sum(ink(refs['id'])[w].sum() for w in wins))
            row['area_win_ink'] = round(area, 2)
            for b in ('chr', 'ff', 'wk'):
                row[f'{b}_win_ink'] = round(float(sum(ink(refs[b])[w].sum() for w in wins)), 2)
            out['reductions'][f'{name}_{fr}'] = row
    for fr in ('z1', 'z2', 'hd'):
        k = f'corpus__buseybench__glm-5v-turbo_{fr}'
        refs = {b: load(f'{BUSEY}/{b}_{k}.png') for b in ('chr', 'ff', 'wk', 'id')}
        wins = windows('glm-5v-turbo', fr)
        row = {v: stats(load(f'{RUN}/png/port/{v}_glm-5v-turbo_{fr}.png'), refs, wins, True) for v in VARIANTS}
        for b in ('chr', 'ff', 'wk'):
            row[f'{b}_win_excess'] = round(float(sum((np.abs(refs[b] - refs['id']).mean(axis=2) / 255.0)[w].sum()
                                                     for w in wins)), 2)
        out['portrait'][f'glm-5v-turbo_{fr}'] = row
    json.dump(out, open(f'{RUN}/measure.json', 'w'), indent=1)
    for k, row in {**out['reductions'], **out['portrait']}.items():
        cells = ' | '.join(f"{v}: off3 {row[v]['off3']} (win {row[v]['off3_win']}), off area {row[v]['off_id']} "
                           f"(win {row[v]['off_id_win']}), win {row[v]['win_ink']}" for v in VARIANTS)
        extra = ', '.join(f'{b} {row[b]}' for b in row if b not in VARIANTS)
        print(f'{k:22s} {cells} || {extra}')


main()
