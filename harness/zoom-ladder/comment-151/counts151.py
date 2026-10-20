#!/usr/bin/env python3
"""Every number in the #151 comment, recomputed from the frames (python3 counts151.py > counts151.txt).

femtovg frames: master 06243b80 and two env-gated variants of it, one binary built with fold-test.patch and
aa-pass-writes-stencil.patch (FV_INNER=fold, FV_AA_ONCE=1; without either it is bit-identical to the ladder's
frames). Harness framing: FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1
VIEWPORT_CLIP=1. Browser frames: the zoom ladder's Chromium 131 / Firefox / WebKit (macOS 27.2) references; the area
reference is Chromium 131 at device scale 8, box-averaged 8x8. Counts are pixels more than 8/255 off in any channel;
"over" = the frame is darker (more ink) than the reference there, "under" = lighter."""
import os, re
import numpy as np
from PIL import Image

H = os.path.expanduser('~')
RUNS = f'{H}/src/femtovg-wt/runs/zoom'
WORK = f'{RUNS}/drafts/C1-comment-151/work'
REFS = f'{RUNS}/fresh/refs'
LAD = f'{RUNS}/png/zl_zm_svg'
FA = f'{RUNS}/triage/firefox-artwork'
FAV = f'{RUNS}/triage/firefox-artwork-v'
REPRO = f'{RUNS}/triage/mask-thin-stroke-3x/repro'


def ld(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def cnt(b, r):
    d = b - r
    bad = np.abs(d).max(axis=2) > 8
    s = d.mean(axis=2)
    return f'{int(bad.sum())} (over {int((bad & (s < 0)).sum())}, under {int((bad & (s > 0)).sum())}, ' \
           f'>20: {int((np.abs(d).max(axis=2) > 20).sum())}, max {int(np.abs(d).max())})'


print('== pen path with #151\'s paint (pen.svg), zoom 1')
a8, c1 = ld(f'{FAV}/area/m151_bevel_s8.png'), ld(f'{FAV}/area/m151_bevel_s1.png')
print('Chromium 1x vs area:', cnt(c1, a8))
for v in ('none', 'fold', 'once'):
    print(f'{v:5} vs area:', cnt(ld(f'{WORK}/pen_{v}.ppm'), a8), '| vs Chromium 1x:', cnt(ld(f'{WORK}/pen_{v}.ppm'), c1))

# Which joins nanovg's inner-bevel test flags, and which of them the fold test still flags (W = 6 + 0.5).
d = re.search(r'<path d="([^"]+)"', open(f'{FAV}/min/m151_bevel.svg').read()).group(1)
pts = np.array([[float(x), float(y)] for x, y in re.findall(r'([\d.]+) ([\d.]+)', d)]) + [130, 30]
seg = np.diff(pts, axis=0)
ln = np.hypot(*seg.T)
W = 6.5
inner, still, feet = [], [], []
for i in range(1, len(pts) - 1):
    th = np.arccos(np.clip((seg[i - 1] / ln[i - 1]) @ (seg[i] / ln[i]), -1, 1))
    lim = max(1.01, min(ln[i - 1], ln[i]) / W)
    if np.cos(th / 2) ** 2 * lim * lim < 1:
        inner.append(pts[i])
        if W * np.tan(th / 2) > 0.5 * min(ln[i - 1], ln[i]):
            still.append(pts[i])
            feet.append((np.degrees(th), W * np.tan(th / 2)))
print(f'chords {ln.min():.2f}-{ln.max():.2f} px; {len(pts) - 2} joins, {len(inner)} inner bevels on master, '
      f'{len(still)} still beveled by the fold test (turns up to {max(f[0] for f in feet):.1f} deg, '
      f'W tan(theta/2) up to {max(f[1] for f in feet):.2f} px)')
for v, P in (('none', np.array(inner)), ('fold', np.array(still))):
    b = ld(f'{WORK}/pen_{v}.ppm') - a8
    ys, xs = np.nonzero((np.abs(b).max(axis=2) > 8) & (b.mean(axis=2) < 0))
    dist = [np.min(np.hypot(P[:, 0] - (x + .5), P[:, 1] - (y + .5))) for x, y in zip(xs, ys)]
    print(f'{v:5}: {len(xs)} over-inked px, all within {max(dist):.2f} px of a',
          'join with an inner bevel' if v == 'none' else 'join the fold test still bevels')

print('\n== loop.svg (#151\'s paint, 16 points on a radius-10 circle, 3.47 px chords turning 20 deg), zoom 1')
a8, c1 = ld(f'{WORK}/loop_s8.png'), ld(f'{WORK}/loop_s1.png')
print('Chromium 1x vs area:', cnt(c1, a8))
for v in ('none', 'fold', 'once'):
    print(f'{v:5} vs area:', cnt(ld(f'{WORK}/loop_{v}.ppm'), a8))

print('\n== lists-empty-state-light, whole frame')
K = 'corpus__firefox__lists-empty-state-light'
for fr in ('z025', 'z033', 'z05', 'z075', 'z1', 'z125', 'z15', 'z175', 'z2', 'z3', 'z4'):
    a, wk, ch = ld(f'{FA}/area/id8_{K}_{fr}.png'), ld(f'{REFS}/wk_{K}_{fr}.png'), ld(f'{REFS}/chr_{K}_{fr}.png')
    row = [f'{v} {cnt(ld(f"{FA}/var/le_{v}_{fr}.ppm"), a)}' for v in ('master', 'fold', 'once', 'p421fold')]
    print(fr, 'vs area:', ' | '.join(row))
    print('     WebKit vs area', cnt(wk, a).split(' ')[0], '| Chromium vs area', cnt(ch, a).split(' ')[0])

print('\n== strip window (32 x 24 px following frame point (240.86, 111.14)) vs WebKit; residuals vs area')
fx, fy, w, h = 240.86, 111.14, 32, 24
for z, fr in ((0.25, 'z025'), (0.33, 'z033'), (0.5, 'z05'), (0.75, 'z075'), (1, 'z1'), (1.25, 'z125'), (1.5, 'z15'),
              (1.75, 'z175'), (2, 'z2'), (3, 'z3'), (4, 'z4')):
    x = max(0, min(460 - w, int(round(230 + (fx - 230) * z - w / 2))))
    y = max(0, min(260 - h, int(round(130 + (fy - 130) * z - h / 2))))
    sl = (slice(y, y + h), slice(x, x + w))
    m, f = ld(f'{FA}/var/le_master_{fr}.ppm')[sl], ld(f'{FA}/var/le_fold_{fr}.ppm')[sl]
    wk, a = ld(f'{REFS}/wk_{K}_{fr}.png')[sl], ld(f'{FA}/area/id8_{K}_{fr}.png')[sl]
    left = np.abs(f - wk).max(axis=2) > 8
    print(f'{z:<5} master {int((np.abs(m - wk).max(axis=2) > 8).sum())}, fold {int(left.sum())}',
          f'(fold within {int(np.abs(f - a).max(axis=2)[left].max())}/255 of the area on them, WebKit '
          f'{int(np.abs(wk - a).max(axis=2)[left].max())}/255)' if left.any() else '')

print('\n== coincident butt ends: mask-on-thin-stroked-path-userspaceonuse')
MK = 'corpus__wpt__tests__mask-on-thin-stroked-path-userspaceonuse'
for z, fr, st in (('1.25', 'z125', 1), ('1.75', 'z175', 3)):
    m = ld(f'{LAD}/{MK}/{st:02}.png')
    for br in ('chr', 'ff', 'wk'):
        r = ld(f'{REFS}/{br}_{MK}_{fr}.png')
        print(z, br, 'master', cnt(m, r).split(' ')[0], 'fold', cnt(ld(f'{WORK}/mask_fold_{z}.ppm'), r).split(' ')[0],
              'once', cnt(ld(f'{WORK}/mask_once_{z}.ppm'), r).split(' ')[0])
o, r = ld(f'{WORK}/mask_once_1.25.ppm'), ld(f'{REFS}/chr_{MK}_z125.png')
for y, x in zip(*np.nonzero(np.abs(o - r).max(axis=2) > 8)):
    print(f'1.25 once leftover ({x}, {y}): coverage {1 - o[y, x, 0] / 255:.3f}, Chromium {1 - r[y, x, 0] / 255:.3f}')

print('\n== zero-gap dashes: resvg-dasharray-n-0-solid, zoom 0.33')
DK = 'wpt22__21-degenerate-paths-dashes-and-joins__resvg-dasharray-n-0-solid'
for br in ('chr', 'ff', 'wk'):
    r = ld(f'{REFS}/{br}_{DK}_z033.png')
    print(br, ' '.join(f'{v} {cnt(ld(f"{WORK}/dash_{v}_0.33.ppm"), r).split(" ")[0]}' for v in ('none', 'fold', 'once')))

print('\n== abutting subpaths (abutting.svg), zoom 1: coverage of green at the seam column x=230')
c = ld(f'{REPRO}/chr_fringe-abutting.png')
for v in ('none', 'once'):
    b = ld(f'{WORK}/abut_{v}.ppm')
    print(f'{v:5} vs Chromium', cnt(b, c).split(' ')[0], 'px; seam', f'{1 - b[80, 230, 0] / 255:.2f}',
          'Chromium', f'{1 - c[80, 230, 0] / 255:.2f}')

print('\n== geometry')
import math
print(f'nanovg inner-bevel test fires above a turn of 2 acos(1/1.01) = {2 * math.degrees(math.acos(1 / 1.01)):.1f} deg')
print(f'chords of one line width (12) with W = 6.5 bevel only past 2 acos(6.5/12) = {2 * math.degrees(math.acos(6.5 / 12)):.1f} deg')
print(f'pill end at 1.75: W = 3.68, 22.5 deg turn: miter foot W tan(11.25 deg) = {3.68 * math.tan(math.radians(11.25)):.2f} px')
print(f'loop.svg: chord {20 * math.sin(math.radians(10)):.2f} px, W tan(10 deg) = {6.5 * math.tan(math.radians(10)):.2f} px')

print('\n== fold-test sweep (firefox-artwork/sweep.py): key, zoom, px changed, WebKit master/fold, Chromium master/fold')
import json
print(len(json.load(open(f'{FA}/sweep_files.json'))), 'stroke files x zooms 1 and 1.75; frames that moved:')
print(open(f'{FA}/sweep_result.txt').read().rstrip())
