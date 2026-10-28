#!/usr/bin/env python3
"""The numbers of the issue, from a run directory ($CORPUS_RUN_OUT) holding the femtovg frames (png/BUILD_KEY_FR.png,
from corpus_run/accuracy.py png=...) and the references (refs/{chr,ff,wk,id}_KEY_FR.png, from refs.py chromium,
refs.py firefox, refs_webkit.py and refs_ideal.py).

  measure.py [BUILD]        (default mst4: the harness built from femtovg master 06243b80)

Ink is summed luminance, (R+G+B)/3/255 per pixel. "Red" is a pixel more than 20/255 off in some channel.

Portrait (gemini-3-7-flash), per framing: two boxes, one per iris, each the rings' extent plus 2 px. The rings' ink
is the luminance change they make over the same renderer's frame of p01_nodash, summed as absolute values over both
boxes; the browsers' and the area reference's are those of the original file (the target every variant is held to).
Red counts compare each femtovg variant with the browsers' frames of the original.

gemini-3-8-flash: the same for its two rings. claude-opus-5-5: pixels off all three browsers within 6 px of each
corner of its two dashed polylines. corner.svg and repro.svg: see the functions below.

Lines (z1, one user unit per pixel): white 1 px strokes on black, so the ink of a row is its summed luminance, and
the exact ink is the length drawn (times the 1 px width). Ratios are to that analytic ink; the area reference's own
ratio is printed beside it as a check."""
import json, math, os, sys
import numpy as np
from PIL import Image

OUT = os.environ['CORPUS_RUN_OUT']
BUILD = sys.argv[1] if len(sys.argv) > 1 else 'mst4'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lines import ROWS, LEN, PIECES, END_CHORDS  # noqa: E402

BROWSERS = ('chr', 'ff', 'wk')


def lum(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float64)


def frame(key, fr, build=None):
    return lum(f'{OUT}/png/{build or BUILD}_{key}_{fr}.png')


def ref(b, key, fr):
    return lum(f'{OUT}/refs/{b}_{key}_{fr}.png')


def off(a, b):
    return np.abs(a - b).max(axis=2) > 20


# --- portrait -------------------------------------------------------------------------------------------------
def mapping(fr):
    # user unit -> frame pixel for a 1024-unit viewBox (corpus_run/common.py FRAMINGS, make_ref.py)
    if fr == 'hd':
        s = 1080 / 1024
        return (lambda u, v: (420 + u * s, v * s)), s
    z = {'z1': 1.0, 'z2': 2.0}[fr]
    s1 = 200 / 1024
    return (lambda u, v: (230 + (130 + u * s1 - 230) * z, 130 + (30 + v * s1 - 130) * z)), s1 * z


def boxes(fr, shape, centres, extent):
    # one square per centre, half side the extent in user units plus 2 px
    to, s = mapping(fr)
    m = np.zeros(shape[:2], bool)
    half = math.ceil(extent * s + 2)
    for cx, cy in centres:
        x, y = to(cx, cy)
        m[int(round(y)) - half:int(round(y)) + half + 1, int(round(x)) - half:int(round(x)) + half + 1] = True
    return m, half


def iris_mask(fr, shape):
    return boxes(fr, shape, [(408, 458), (616, 458)], 21.75)


PORTRAIT = [('p00_orig', 'femtovg master'),
            ('p05_emul_joined', 'femtovg, the same pieces joined into one polyline per dash'),
            ('p02_dash_arcs', 'femtovg, one arc subpath per dash'),
            ('p04_emul_split', 'femtovg, its own pieces written out as M a L b subpaths'),
            ('p06_arcs_floor_z2', 'femtovg, one arc per dash, dashes under a pixel lengthened to one at reduced opacity (z2)')]


def portrait(fr):
    k = lambda n: f'portrait__{n}'
    orig = {b: ref(b, k('p00_orig'), fr) for b in (*BROWSERS, 'id')}
    base = {b: ref(b, k('p01_nodash'), fr) for b in (*BROWSERS, 'id')}
    fv0 = frame(k('p01_nodash'), fr)
    mask, half = iris_mask(fr, fv0.shape)
    ink = lambda a, b0: float((np.abs(a - b0).mean(axis=2) / 255)[mask].sum())
    area = ink(orig['id'], base['id'])
    out = {'framing': fr, 'box_half_px': half, 'rows': []}
    for n, label in PORTRAIT:
        fv = frame(k(n), fr)
        all3 = off(fv, orig['chr']) & off(fv, orig['ff']) & off(fv, orig['wk'])
        i = ink(fv, fv0)
        vs_chr = off(fv, orig['chr']) & mask
        out['rows'].append({'variant': n, 'label': label, 'ink': round(i, 2), 'ink_vs_area': round(i / area, 3),
                            **{f'ink_vs_{b}': round(i / ink(orig[b], base[b]), 3) for b in BROWSERS},
                            'red_all3_iris': int(all3[mask].sum()), 'red_all3_frame': int(all3.sum()),
                            'red_vs_area_iris': int(off(fv, orig['id'])[mask].sum()),
                            # of the pixels off all three browsers, those also off the area reference
                            'red_all3_iris_also_off_area': int((all3 & mask & off(fv, orig['id'])).sum()),
                            # against Chromium alone, and where Chromium is itself off the area reference there
                            'red_vs_chr_iris': int(vs_chr.sum()),
                            'red_vs_chr_iris_chr_off_area': int((vs_chr & off(orig['chr'], orig['id'])).sum())})
    for b in BROWSERS:
        others = [o for o in BROWSERS if o != b]
        i = ink(orig[b], base[b])
        out['rows'].append({'variant': b, 'label': b, 'ink': round(i, 2), 'ink_vs_area': round(i / area, 3),
                            'red_vs_other_two_iris': int((off(orig[b], orig[others[0]]) & off(orig[b], orig[others[1]]))[mask].sum()),
                            'red_vs_area_iris': int(off(orig[b], orig['id'])[mask].sum())})
    out['rows'].append({'variant': 'id', 'label': 'area reference', 'ink': round(area, 2), 'ink_vs_area': 1.0})
    # without the rings, femtovg and the browsers agree in these boxes
    nd = frame(k('p01_nodash'), fr)
    out['nodash_red_all3_iris'] = int((off(nd, base['chr']) & off(nd, base['ff']) & off(nd, base['wk']))[mask].sum())
    out['nodash_vs_area_iris'] = {'femtovg': int(off(nd, base['id'])[mask].sum()),
                                  **{b: int(off(base[b], base['id'])[mask].sum()) for b in BROWSERS}}
    # the emulated pieces against the real dasher's output
    out['p04_identical_to_p00'] = bool((frame(k('p04_emul_split'), fr) == frame(k('p00_orig'), fr)).all())
    return out


# --- the other BuseyBench files ----------------------------------------------------------------------------------
def g38(fr):
    """gemini-3-8-flash.svg: its two dashed iris rings (r=15 and r=14.5, dash 2,3), boxes as for the portrait."""
    k = lambda n: f'portrait__g38_{n}'
    orig = {b: ref(b, k('orig'), fr) for b in (*BROWSERS, 'id')}
    base = {b: ref(b, k('nodash'), fr) for b in (*BROWSERS, 'id')}
    fv0 = frame(k('nodash'), fr)
    mask, half = boxes(fr, fv0.shape, [(423, 452), (600, 448)], 15.75)
    ink = lambda a, b0: float((np.abs(a - b0).mean(axis=2) / 255)[mask].sum())
    area = ink(orig['id'], base['id'])
    out = {'framing': fr, 'box_half_px': half, 'rows': []}
    for n in ('orig', 'arcs'):
        fv = frame(k(n), fr)
        all3 = off(fv, orig['chr']) & off(fv, orig['ff']) & off(fv, orig['wk'])
        i = ink(fv, fv0)
        out['rows'].append({'variant': f'g38_{n}', 'ink': round(i, 2), 'ink_vs_area': round(i / area, 3),
                            **{f'ink_vs_{b}': round(i / ink(orig[b], base[b]), 3) for b in BROWSERS},
                            'red_all3_iris': int(all3[mask].sum()), 'red_vs_area_iris': int(off(fv, orig['id'])[mask].sum())})
    for b in BROWSERS:
        i = ink(orig[b], base[b])
        out['rows'].append({'variant': b, 'ink': round(i, 2), 'ink_vs_area': round(i / area, 3)})
    out['rows'].append({'variant': 'id', 'ink': round(area, 2), 'ink_vs_area': 1.0})
    out['nodash_red_all3_iris'] = int((off(fv0, base['chr']) & off(fv0, base['ff']) & off(fv0, base['wk']))[mask].sum())
    return out


def opus(fr):
    """claude-opus-5-5.svg: the two dashed polylines' corners (358,924) and (666,924), where a dash crosses each corner
    1.39 units into it. Boxes of 6 px about each corner."""
    k = lambda n: f'portrait__opus_{n}'
    orig = {b: ref(b, k('orig'), fr) for b in (*BROWSERS, 'id')}
    to, _ = mapping(fr)
    out = {'framing': fr, 'corners': []}
    shape = orig['chr'].shape
    for c in ((358, 924), (666, 924)):
        x, y = (int(round(v)) for v in to(*c))
        m = np.zeros(shape[:2], bool)
        m[max(y - 6, 0):y + 7, max(x - 6, 0):x + 7] = True
        row = {'corner': c, 'frame_px': (x, y)}
        for n in ('orig', 'joined'):
            fv = frame(k(n), fr)
            all3 = off(fv, orig['chr']) & off(fv, orig['ff']) & off(fv, orig['wk']) & m
            d_area = np.abs(fv - orig['id']).max(axis=2)
            row[n] = {'red_all3': int(all3.sum()), 'red_vs_area': int((off(fv, orig['id']) & m).sum()),
                      'all3_px_vs_area': [int(v) for v in d_area[all3]]}
        out['corners'].append(row)
    a, b = frame(k('orig'), fr), frame(k('joined'), fr)
    out['orig_vs_joined_px_differ'] = int((np.abs(a - b).max(axis=2) > 0).sum())
    return out


def corner(fr='z1'):
    """corner.svg: the outer corner square of the dash that crosses the corner (user x 120-128, y 52-60, at z1 frame
    x 250-258, y 82-90): its mean value per renderer; px off all three browsers' frames of corner.svg."""
    key, sq = 'repro__corner', (slice(82, 90), slice(250, 258))
    r = {b: ref(b, key, fr) for b in (*BROWSERS, 'id')}
    out = {'square_mean': {b: round(float(r[b][sq].mean()), 1) for b in (*BROWSERS, 'id')}}
    for n in ('corner', 'corner-joined', 'corner-split'):
        fv = frame(f'repro__{n}', fr)
        all3 = off(fv, r['chr']) & off(fv, r['ff']) & off(fv, r['wk'])
        out[n] = {'square_mean': round(float(fv[sq].mean()), 1), 'red_all3': int(all3.sum()),
                  'red_vs_area': int(off(fv, r['id']).sum())}
    out['split_identical_to_corner'] = bool((frame('repro__corner-split', fr) == frame('repro__corner', fr)).all())
    return out


def repro(fr='z1'):
    """repro.svg (the issue's repro): ink of each line over the exact 80 px (40 dashes of 2 x 1 px)."""
    key = 'repro__repro'
    ims = {'femtovg': frame(key, fr), **{b: ref(b, key, fr) for b in (*BROWSERS, 'id')}}
    out = {}
    for name, y in (('plain', 28), ('points', 36)):
        band = (slice(30 + y - 4, 30 + y + 5), slice(130 + 20 - 3, 130 + 180 + 4))
        out[name] = {w: round(float((im.mean(axis=2) / 255)[band].sum() / 80.0), 3) for w, im in ims.items()}
    return out


# --- lines ----------------------------------------------------------------------------------------------------
def row_inks(im, fr='z1'):
    g = im.mean(axis=2) / 255
    res = []
    for x0, y in ROWS:
        ya, yb = int(math.floor(30 + y - 3.5)), int(math.ceil(30 + y + 3.5))
        xa, xb = int(130 + x0 - 3), int(math.ceil(130 + x0 + LEN + 3))
        res.append(float(g[ya:yb, xa:xb].sum()))
    return np.array(res)


def drawn_length(name):
    # the length the file asks to be drawn, per row
    if name.startswith('line'):
        n_dash = len([a for a in np.arange(0, LEN, 4.0)])  # dash 2 gap 2 over 160 units
        return np.full(len(ROWS), 2.0 * n_dash)
    if name.startswith('endchord'):
        return np.full(len(ROWS), 16 * 2.0)
    return np.array([16 * L for L in PIECES])


LINES = ['line-plain', 'line-points', 'line-points-1px', 'line-split', 'line-joined', 'line-segments',
         'line-points-03', 'line-joined-03', 'line-segments@line-points-03',
         'pieces', 'pieces-scaled', 'endchord-plain', 'endchord-short']


# A file written out as a fix direction would draw it is held to the browsers' frames of the file it stands for.
# NAME@TARGET holds NAME to TARGET's references (line-segments stands for both lines' one-segment-per-dash).
TARGET = {'line-split': 'line-points', 'line-joined': 'line-points', 'line-segments': 'line-points',
          'line-joined-03': 'line-points-03', 'line-segments@line-points-03': 'line-points-03', 'pieces-scaled': 'pieces'}


def lines(fr='z1'):
    out = {}
    for n in LINES:
        key, tkey = f'repro__{n.split("@")[0]}', f'repro__{TARGET.get(n, n)}'
        exact = drawn_length(n.split('@')[0])
        fv = frame(key, fr)
        r = {b: ref(b, key, fr) for b in (*BROWSERS, 'id')}
        t = {b: ref(b, tkey, fr) for b in (*BROWSERS, 'id')}
        all3 = off(fv, t['chr']) & off(fv, t['ff']) & off(fv, t['wk'])
        inks = {'femtovg': row_inks(fv), **{b: row_inks(r[b]) for b in (*BROWSERS, 'id')}}
        out[n] = {'target': TARGET.get(n, n), 'ink_vs_exact': {w: round(float(v.sum() / exact.sum()), 3) for w, v in inks.items()},
                  'red_all3_frame': int(all3.sum()), 'red_vs_area_frame': int(off(fv, t['id']).sum()),
                  'red_vs_chr_frame': int(off(fv, t['chr']).sum())}
        if n == TARGET.get(n, n):
            # the browsers' own spread on this file: each against the other two, and against the area reference
            out[n]['browsers'] = {b: {'red_vs_other_two': int(np.logical_and.reduce([off(t[b], t[o]) for o in BROWSERS if o != b]).sum()),
                                      'red_vs_area': int(off(t[b], t['id']).sum())} for b in BROWSERS}
        if n in ('line-split', 'line-segments'):
            out[n]['identical_to'] = {'line-split': 'line-points', 'line-segments': 'line-plain'}[n]
            out[n]['identical'] = bool((fv == frame(f"repro__{out[n]['identical_to']}", fr)).all())
        if n == 'pieces-scaled':
            # where the stand-ins stay off all three browsers: by segment length, and the largest such difference
            ys = np.nonzero(all3)[0]
            row = [min(range(len(ROWS)), key=lambda i: abs(30 + ROWS[i][1] - y)) for y in ys]
            out[n]['red_all3_by_length'] = {str(L): sum(PIECES[r] == L for r in row) for L in sorted(set(PIECES[r] for r in row))}
            out[n]['red_all3_max_vs_area'] = int(np.abs(fv - t['id']).max(axis=2)[all3].max()) if all3.any() else 0
        if n.startswith(('pieces', 'endchord')):
            per, lengths = {}, PIECES if n.startswith('pieces') else END_CHORDS
            for L in sorted(set(lengths)):
                rows = [i for i, p in enumerate(lengths) if p == L]
                per[str(L)] = {w: round(float(v[rows].sum() / exact[rows].sum()), 3) for w, v in inks.items()}
            out[n]['per_length'] = per
    return out


def main():
    res = {'build': BUILD, 'portrait': [portrait(fr) for fr in ('z1', 'z2', 'hd')], 'lines_z1': lines('z1'),
           'g38': [g38(fr) for fr in ('z1', 'z2', 'hd')], 'opus': [opus(fr) for fr in ('z1', 'hd')],
           'corner_z1': corner('z1'), 'repro_z1': repro('z1')}
    json.dump(res, open(f'{OUT}/numbers_{BUILD}.json', 'w'), indent=1)
    for p in res['portrait']:
        print(f"\nportrait {p['framing']} (iris boxes {2 * p['box_half_px'] + 1} px square; femtovg red without the rings: {p['nodash_red_all3_iris']})")
        for r in p['rows']:
            print('  ' + ' '.join(f'{k}={v}' for k, v in r.items() if k != 'label'))
    print('\nlines at z1, ink / exact')
    for n, v in res['lines_z1'].items():
        print(f'  {n:16s} (held to {v["target"]})', v['ink_vs_exact'], 'red all3', v['red_all3_frame'], 'vs area', v['red_vs_area_frame'],
              'vs chr', v['red_vs_chr_frame'], v.get('browsers', ''))
        for L, w in v.get('per_length', {}).items():
            print(f'      {L:>5s} px', w)
    for p in res['g38']:
        print(f"\ngemini-3-8-flash {p['framing']} (boxes {2 * p['box_half_px'] + 1} px; femtovg red without the rings: {p['nodash_red_all3_iris']})")
        for r in p['rows']:
            print('  ' + ' '.join(f'{k}={v}' for k, v in r.items()))
    for p in res['opus']:
        print(f"\nclaude-opus-5-5 {p['framing']} corners (orig vs joined: {p['orig_vs_joined_px_differ']} px differ)")
        for c in p['corners']:
            print('  ', c)
    print('\ncorner.svg z1', res['corner_z1'])
    print('\nrepro.svg z1, ink / exact', res['repro_z1'])


if __name__ == '__main__':
    main()
