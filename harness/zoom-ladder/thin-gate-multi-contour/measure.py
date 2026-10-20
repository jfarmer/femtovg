#!/usr/bin/env python3
"""Every number in the issue, from the frames (output: numbers.txt).

master = the zm build's ladder frames (harness at femtovg 06243b80); gate fix = the proof build (06243b80 with
proof_toggles.patch) run with FV_GATE_FIX=1, whose frames without it equal the zm ladder's bit for bit at all 21
steps. Pixels "beyond 8/255" compare the largest channel difference. Ink is the summed darkness over white."""
import math, os, re
import numpy as np
from PIL import Image

H = os.path.expanduser('~/src/femtovg-wt/runs/zoom')
T = f'{H}/triage/svgenius-033'          # frames of the proof build (proof_toggles.patch), refs, area references
V = f'{T}-v'                            # frames of a second proof build (half_fringe_toggles.patch)
N9 = f'{H}/drafts/N9-thin-gate-multi-contour/work'
KEY = 'svgenius__page_275_化妆品装饰_25821_icon_24'


def load(p):
    a = np.asarray(Image.open(p).convert('RGBA')).astype(float)
    return a[..., :3] * a[..., 3:4] / 255 + 255 * (1 - a[..., 3:4] / 255)


def n8(a, b):
    return int((np.abs(a - b).max(axis=2) > 8).sum())


def ink(a):
    return (255 - (a.mean(axis=2) if a.ndim == 3 else a)).sum() / 255


def ring_walls(d):
    """The four walls (left, top, right, bottom) between a ring's outer contour and its hole, in viewBox units, from
    the contours' end points: these rings are rounded rectangles, whose extremes lie on their straight edges."""
    count = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'A': 7, 'Q': 4, 'C': 6}
    toks = re.findall(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)', d)
    contours, cur, x, y, i, cmd = [], [], 0.0, 0.0, 0, None
    while i < len(toks):
        if toks[i].isalpha():
            cmd, i = toks[i], i + 1
        if cmd in 'Zz':
            contours, cur, cmd = contours + [cur], [], None
            continue
        a = [float(v) for v in toks[i:i + count[cmd.upper()]]]
        i += count[cmd.upper()]
        rel = cmd.islower()
        if cmd.upper() == 'H':
            x = x + a[0] if rel else a[0]
        elif cmd.upper() == 'V':
            y = y + a[0] if rel else a[0]
        else:
            x, y = (x + a[-2], y + a[-1]) if rel else (a[-2], a[-1])
        cur.append((x, y))
    outer, hole = [(min(p[0] for p in c), min(p[1] for p in c), max(p[0] for p in c), max(p[1] for p in c))
                   for c in contours if len(c) > 2]
    return [hole[0] - outer[0], hole[1] - outer[1], outer[2] - hole[2], outer[3] - hole[3]]


SVG = os.path.expanduser('~/src/femtovg-wt/da/corpus/svgenius/medium/page_275_化妆品装饰_25821_icon_24.svg')
paths = re.findall(r'<path d="([^"]+)"', open(SVG).read())
walls = {i: ring_walls(paths[i]) for i in (0, 1, 3, 4, 6)}
lo, hi = min(min(w) for w in walls.values()), max(max(w) for w in walls.values())
print('ring walls (paths 0, 1, 3, 4, 6), units of the 1024-unit viewBox drawn at 200 px:',
      '; '.join(f'path {i} ' + '/'.join(f'{v:.2f}' for v in w) for i, w in walls.items()))
print('  all rings:', ', '.join(f'{z:g} -> {lo * 200 / 1024 * z:.2f}-{hi * 200 / 1024 * z:.2f} px'
                                for z in (0.25, 0.33, 0.5, 1)))

print('\n1. makeup icon, px beyond 8/255, master -> gate fix (ladder steps, 0-based)')
for step, z, fr in [(14, 0.5, 'z05'), (15, 0.33, 'z033'), (16, 0.25, 'z025')]:
    m, g = load(f'{H}/png/zl_zm_svg/{KEY}/{step:02}.png'), load(f'{N9}/lad_gate_png/{step:02}.png')
    refs = {b: load(f'{H}/fresh/refs/{b}_{KEY}_{fr}.png') for b in ('chr', 'ff', 'wk')
            if os.path.exists(f'{H}/fresh/refs/{b}_{KEY}_{fr}.png')}
    print(f'  zoom {z:g}:', ', '.join(f'{b} {n8(m, r)} -> {n8(g, r)}' for b, r in refs.items()))
    if fr == 'z033':
        print('    browsers among themselves:', f"chr-ff {n8(refs['chr'], refs['ff'])}, chr-wk {n8(refs['chr'], refs['wk'])},"
              f" ff-wk {n8(refs['ff'], refs['wk'])}")

print('\n2. each path of the icon drawn alone at 0.33, ink over the 8x area reference (Chromium at 8x, averaged)')
for i in range(10):
    a = ink(load(f'{T}/pp/area_m{i}.png'))
    print(f'  path {i}: master {ink(load(f"{V}/mkb_{i}.png")) / a:.3f}  gate fix {ink(load(f"{V}/mkg_{i}.png")) / a:.3f}'
          f'  every fill masked {ink(load(f"{V}/mkf_{i}.png")) / a:.3f}  Chromium {ink(load(f"{T}/pp/chr_m{i}.png")) / a:.3f}')
print('  (rings of two convex contours: paths 0, 1, 3, 4, 6; the gate fix here is SKV_GATE of half_fringe_toggles.patch,'
      ' which counts drawn contours; on the whole icon at 0.33 its frame and FV_GATE_FIX\'s are identical)')

same = (load(f'{V}/pg_make_0.33.png') != load(f'{N9}/lad_gate_png/15.png')).any(axis=2).sum()
print('  pixels where SKV_GATE and FV_GATE_FIX differ on the icon at 0.33:', int(same))

print('\n3. repro.svg at 1x, ink over the exact area (axis-aligned edges on a 0.1 px grid, rasterized 10x)')
S = 10
g = np.zeros((260 * S, 460 * S), bool)


def rect(x0, y0, x1, y1, val=True):
    g[round((y0 + 30) * S):round((y1 + 30) * S), round((x0 + 130) * S):round((x1 + 130) * S)] = val


rect(20, 20.3, 180, 21.5)
rect(20, 40.3, 180, 41.5)
rect(20, 50.3, 180, 51.5)
rect(20.3, 70.3, 180.3, 90.3)
rect(21.5, 71.5, 179.1, 89.1, False)
exact = 255 * (1 - g.reshape(260, S, 460, S).mean(axis=(1, 3)))
frames = {'master': load(f'{N9}/repro_master.png'), 'gate fix': load(f'{N9}/repro_gate.png'),
          'Chromium': load(f'{T}/repro_chr.png'), 'WebKit': load(f'{T}/repro_wk.png')}
for row, (y0, y1) in {'A one bar': (46, 56), 'B two bars, one path': (66, 86), 'C ring': (96, 126)}.items():
    e = ink(exact[y0:y1, 140:330])
    print(f'  {row}:', ', '.join(f'{k} {ink(v[y0:y1, 140:330]) / e:.3f}' for k, v in frames.items()))
w = frames['WebKit']
print('  px beyond 8/255 off WebKit in rows A-C (frame rows 40-129):',
      ', '.join(f'{k} {n8(v[40:130], w[40:130])}' for k, v in frames.items() if k != 'WebKit'))
print('  B, column 230, rows 70-71 and 80-81:', {k: [int(round(v[y, 230, 0])) for y in (70, 71, 80, 81)]
                                              for k, v in frames.items()}, 'exact 76.5, 127.5')

print("\n4. #327's ring, R = 8, at 1x: ink over the exact area pi (R^2 - r^2)")
for f, r in [('r10', 7.0)]:
    e = math.pi * (64 - r * r)
    print(f'  wall {8 - r:.1f} px: master {ink(load(f"{V}/{f}_b.png")) / e:.3f}  gate fix {ink(load(f"{V}/{f}_g.png")) / e:.3f}'
          f'  every fill masked {ink(load(f"{V}/{f}_f.png")) / e:.3f}')

print('\n5. the alternative: every concave ramp ends 0.5 px inside its edge (SKV_HALF in half_fringe_toggles.patch, no masks), at 0.33')
wk = load(f'{H}/fresh/refs/wk_{KEY}_z033.png')
print('  icon, px beyond 8/255 off WebKit:', n8(load(f'{V}/h_make.png'), wk))
print('  rings drawn alone, ink over the 8x area reference:',
      ', '.join(f'path {i} {ink(load(f"{V}/mkh_{i}.png")) / ink(load(f"{T}/pp/area_m{i}.png")):.3f}' for i in (0, 1, 3, 4, 6)))
