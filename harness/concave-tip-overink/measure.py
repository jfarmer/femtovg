#!/usr/bin/env python3
"""Numbers for the concave-tip over-ink issue: ink at the tips against the 8x area reference, and pixels more than
20/255 off all three browsers, for the reductions and the BuseyBench portraits.

  measure.py RUN [BUSEY_REFS]

RUN holds the frames render.py wrote (png/red/<variant>_<name>_z2.png, png/port/<variant>_<portrait>_<framing>.png)
and the reductions' references (refs/{chr,ff,wk,id}_ct__<name>_z2.png, from corpus_run/refs.py, refs_webkit.py and
refs_ideal.py). BUSEY_REFS holds the portraits' references (refs/{chr,ff,wk,id}_corpus__buseybench__<name>_<framing>.png).

Ink is the darkness of a black fill on white summed over a window, in pixels: sum of (255 - grey) / 255. A tip
window is 28 x 28 px centred on the tip. Variants: master (06243b80 as it is), off (NO_THIN_FILL_MASKS=1), masks
(every fill as its bounds under the path as a clip: an exact-area coverage mask)."""
import json, os, sys
import numpy as np
from PIL import Image

RUN = sys.argv[1]
BUSEY = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/src/femtovg-wt/runs/busey/refs')
BROWSERS = ('chr', 'ff', 'wk')


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def window(cx, cy, r=14):
    x, y = int(np.floor(cx)), int(np.floor(cy))
    return (slice(y - r, y + r), slice(x - r, x + r))


def off_all(frame, refs):
    m = np.ones(frame.shape[:2], bool)
    for b in BROWSERS:
        m &= np.abs(frame - refs[b]).max(axis=2) > 20
    return m


def ink(im, wins):
    g = (255.0 - im.mean(axis=2)) / 255.0
    return float(sum(g[w].sum() for w in wins))


# z2: svg (u, v) -> frame (0.390625 u + 30, 0.390625 v - 70); hd: (420 + 1.0546875 u, 1.0546875 v); z1: (130 + u / 5.12,
# 30 + v / 5.12).
def z2(u, v):
    return 0.390625 * u + 30, 0.390625 * v - 70


def hd(u, v):
    return 420 + 1.0546875 * u, 1.0546875 * v


def z1(u, v):
    return 130 + 0.1953125 * u, 30 + 0.1953125 * v


# The reductions share the lip's tips, svg (280, 725) and (744, 725).
TIPS = [z2(280, 725), z2(744, 725)]
out = {'reductions': {}, 'portraits': {}}
print('Reductions at z2 (460 x 260, 1024-unit viewBox in a 200 px box at 2x), black on white, both tip windows:')
print(f'{"":12s} {"ink: master":>12s} {"masks":>7s} {"Chromium":>9s} {"Firefox":>8s} {"WebKit":>7s} {"area":>6s} | '
      f'{"off all 3: master":>17s} {"masks":>6s} | {">20 off area in tips: master":>28s} {"masks":>6s} {"chr":>4s} {"ff":>4s} {"wk":>4s}')
for name in ('wedge', 'wedge-split', 'lip'):
    refs = {b: load(f'{RUN}/refs/{b}_ct__{name}_z2.png') for b in BROWSERS + ('id',)}
    fr = {v: load(f'{RUN}/png/red/{v}_{name}_z2.png') for v in ('master', 'off', 'masks')}
    wins = [window(*t) for t in TIPS]
    area = ink(refs['id'], wins)
    row = {'ink_area_px': round(area, 2)}
    for k, im in [('master', fr['master']), ('masks', fr['masks'])] + [(b, refs[b]) for b in BROWSERS]:
        row[f'ink_{k}'] = round(ink(im, wins) / area, 3)
        over = np.abs(im - refs['id']).max(axis=2) > 20
        row[f'over_area_{k}'] = int(over.sum())
        row[f'over_area_tips_{k}'] = int(sum(over[w].sum() for w in wins))
    for k in ('master', 'masks'):
        m = off_all(fr[k], refs)
        row[f'off3_{k}'] = int(m.sum())
        row[f'off3_{k}_in_tips'] = int(sum(m[w].sum() for w in wins))
    row['off_identical_to_master'] = bool((fr['off'] == fr['master']).all())
    row['excess_px_per_tip_master'] = round((ink(fr['master'], wins) - area) / 2, 2)
    out['reductions'][name] = row
    print(f'{name:12s} {row["ink_master"]:12.2f} {row["ink_masks"]:7.2f} {row["ink_chr"]:9.2f} {row["ink_ff"]:8.2f} '
          f'{row["ink_wk"]:7.2f} {1.0:6.2f} | {row["off3_master"]:17d} {row["off3_masks"]:6d} | '
          f'{row["over_area_tips_master"]:28d} {row["over_area_tips_masks"]:6d} {row["over_area_tips_chr"]:4d} '
          f'{row["over_area_tips_ff"]:4d} {row["over_area_tips_wk"]:4d}   (area ink {area:.1f} px, master +{row["excess_px_per_tip_master"]} px a tip; '
          f'NO_THIN_FILL_MASKS identical: {row["off_identical_to_master"]})')

# Portrait tip windows: svg tip points of the crescents named in the README.
PORTRAITS = {
    ('grok-4-5', 'z2'): [z2(80, 260), z2(944, 260)],              # lines 153/169, the lower hair spikes
    ('grok-4-5', 'hd'): [hd(80, 260), hd(944, 260)],
    ('grok-4-5', 'z1'): [z1(80, 260), z1(944, 260)],                # at 1x the spikes are thin enough for #408
    ('gemini-3-7-flash', 'z2'): [z2(345, 645), z2(679, 645)],    # line 562, the lip crescent
    ('gemini-3-7-flash', 'hd'): [hd(345, 645), hd(679, 645)],
    ('gemini-3-1-pro-preview', 'z2'): [z2(280, 725), z2(744, 725)],  # line 293, the lower lip (mouth corners)
    ('gemini-3-1-pro-preview', 'hd'): [hd(280, 725), hd(744, 725)],
    ('gemini-3-1-pro-preview', 'z1'): [z1(280, 725), z1(744, 725)],  # the lip is 3.8 px at 1x, over #408's gate
    # lines 279/280 (eye-top shadows, blurred) and 411/416 (lips); lines 129/130 (eyebrow spike), 177 (lower teeth) and
    # 178 (tongue), whose windows also hold the strokes drawn over them
    ('gemini-3-1-pro-preview-custom-tools', 'z2'): [z2(*t) for t in ((350, 475), (465, 480), (559, 480), (674, 475), (355, 760), (675, 730))],
    ('gemini-3-1-pro-preview-custom-tools', 'hd'): [hd(*t) for t in ((350, 475), (465, 480), (559, 480), (674, 475), (355, 760), (675, 730))],
    ('mistral-large-4', 'z2'): [z2(*t) for t in ((512, 382), (430, 742), (594, 742), (455, 770), (569, 770))],
    ('mistral-large-4', 'hd'): [hd(*t) for t in ((512, 382), (430, 742), (594, 742), (455, 770), (569, 770))],
}
print('\nPortraits: pixels more than 20/255 off all three browsers, whole frame and in the tip windows')
for (name, framing), tips in PORTRAITS.items():
    key = f'corpus__buseybench__{name}_{framing}'
    refs = {b: load(f'{BUSEY}/{b}_{key}.png') for b in BROWSERS}
    union = np.zeros(refs['chr'].shape[:2], bool)  # windows may overlap: count each pixel once
    for t in tips:
        union[window(*t)] = True
    row = {}
    for v in ('master', 'off', 'masks'):
        m = off_all(load(f'{RUN}/png/port/{v}_{name}_{framing}.png'), refs)
        row[v] = int(m.sum())
        row[f'{v}_tips'] = int((m & union).sum())
        row[f'{v}_each_tip'] = [int(m[window(*t)].sum()) for t in tips]  # per window, in PORTRAITS order
    a, b = (load(f'{RUN}/png/port/{v}_{name}_{framing}.png') for v in ('master', 'off'))
    row['off_identical_in_tips'] = bool((a[union] == b[union]).all())
    out['portraits'][f'{name}_{framing}'] = row
    print(f'{name:36s} {framing}: frame master {row["master"]:4d}  off {row["off"]:4d}  masks {row["masks"]:4d}   '
          f'tips master {row["master_tips"]:3d}  off {row["off_tips"]:3d}  masks {row["masks_tips"]:3d}   '
          f'(master and NO_THIN_FILL_MASKS identical in the tip windows: {row["off_identical_in_tips"]}; '
          f'master per window {row["master_each_tip"]})')
json.dump(out, open(f'{RUN}/measure.json', 'w'), indent=1)
