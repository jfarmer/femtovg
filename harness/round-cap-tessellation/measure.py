#!/usr/bin/env python3
"""measure.py [TAG ...]: cap and join windows of the reductions against their exact coverage.

Every stroke's shape is known (shapes.json), so each window pixel's exact coverage is its share of 16 x 16 samples
inside the shape: for a round cap the points within half the width of the segment, for a butt cap the rectangle,
for the joins the two legs' rectangles and the disc at the corner. A cap window is the pixels whose centres lie
from 1 px inside the end to r + 1.5 px past it, and within r + 1.5 px of the axis (r = half the device width); a
join window the pixels within r + 1.5 px of the corner. Prints, per width (caps) or width and turn (joins) and
framing: the windows' ink relative to the exact ink, and the pixels more than 20/255 off the exact coverage, for
each TAG (femtovg builds, default mstc caps) and Chromium (chr), Firefox (ff), WebKit (wk) and the 8x area
reference (id). Writes numbers.json."""
import json, math, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ['CORPUS_RUN_OUT']
TAGS = sys.argv[1:] or ['mstc', 'caps']  # when run as a script
REFS = ['chr', 'ff', 'wk', 'id']
SS = 16
MAP = {'z1': (1.0, (130, 30)), 'z2': (2.0, (30, -70)), 'hd': (5.4, (420, 0))}  # device = scale * unit + offset
shapes = json.load(open(f'{HERE}/shapes.json'))


def dev(p, fr):
    s, (ox, oy) = MAP[fr]
    return np.array([p[0] * s + ox, p[1] * s + oy])


def seg_dist(X, Y, a, b):
    d = b - a; L2 = d @ d
    t = np.clip(((X - a[0]) * d[0] + (Y - a[1]) * d[1]) / L2, 0, 1)
    return np.hypot(X - a[0] - t * d[0], Y - a[1] - t * d[1])


def in_rect(X, Y, a, b, r):
    d = b - a; L = math.hypot(*d); d = d / L; n = np.array([-d[1], d[0]])
    t = (X - a[0]) * d[0] + (Y - a[1]) * d[1]; u = (X - a[0]) * n[0] + (Y - a[1]) * n[1]
    return (t >= 0) & (t <= L) & (np.abs(u) <= r)


def coverage(x0, y0, x1, y1, inside):
    o = (np.arange(SS) + 0.5) / SS
    ys = (np.arange(y0, y1)[:, None] + o[None, :]).ravel(); xs = (np.arange(x0, x1)[:, None] + o[None, :]).ravel()
    X, Y = np.meshgrid(xs, ys)
    m = inside(X, Y).astype(float)
    return m.reshape(y1 - y0, SS, x1 - x0, SS).mean(axis=(1, 3))


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), float)[..., 0] / 255


def frame(tag, key, fr):
    p = f'{OUT}/png/{tag}_{key}_{fr}.png' if tag not in REFS else f'{OUT}/refs/{tag}_{key}_{fr}.png'
    return load(p) if os.path.exists(p) else None


def caps_windows(cap, fr):
    """(width, x0, y0, x1, y1, exact, mask) per cap end."""
    s = MAP[fr][0]; res = []
    for ln in shapes['caps']:
        a, b = dev(ln['a'], fr), dev(ln['b'], fr); r = ln['w'] * s / 2
        d = (b - a) / np.linalg.norm(b - a); n = np.array([-d[1], d[0]])
        inside = (lambda X, Y, a=a, b=b, r=r: seg_dist(X, Y, a, b) <= r) if cap == 'round' else \
                 (lambda X, Y, a=a, b=b, r=r: in_rect(X, Y, a, b, r))
        for end, sgn in ((a, -1), (b, 1)):
            x0, y0 = np.floor(end - (r + 3)).astype(int); x1, y1 = np.ceil(end + (r + 3)).astype(int)
            Yc, Xc = np.mgrid[y0:y1, x0:x1] + 0.5
            t = ((Xc - end[0]) * d[0] + (Yc - end[1]) * d[1]) * sgn; u = (Xc - end[0]) * n[0] + (Yc - end[1]) * n[1]
            mask = (t > -1.0) & (t <= r + 1.5) & (np.abs(u) < r + 1.5)
            res.append((ln['w'], x0, y0, x1, y1, coverage(x0, y0, x1, y1, inside), mask))
    return res


def joins_windows(fr):
    s = MAP[fr][0]; res = []
    for p in shapes['joins']:
        P = [dev(q, fr) for q in p['pts']]; r = p['w'] * s / 2; c = P[1]
        inside = lambda X, Y, P=P, r=r: in_rect(X, Y, P[0], P[1], r) | in_rect(X, Y, P[1], P[2], r) | (np.hypot(X - P[1][0], Y - P[1][1]) <= r)
        x0, y0 = np.floor(c - (r + 3)).astype(int); x1, y1 = np.ceil(c + (r + 3)).astype(int)
        Yc, Xc = np.mgrid[y0:y1, x0:x1] + 0.5
        mask = np.hypot(Xc - c[0], Yc - c[1]) <= r + 1.5
        res.append(((p['w'], p['turn']), x0, y0, x1, y1, coverage(x0, y0, x1, y1, inside), mask))
    return res


def tally(key, wins, frs_img):
    rows = {}
    for k, x0, y0, x1, y1, ex, m in wins:
        row = rows.setdefault(k, {'exact': 0.0, **{t: [0.0, 0] for t in frs_img}})
        row['exact'] += float(ex[m].sum())
        for t, im in frs_img.items():
            if im is None: continue
            v = im[y0:y1, x0:x1]
            row[t][0] += float(v[m].sum()); row[t][1] += int((np.abs(v - ex)[m] > 20 / 255).sum())
    return rows


def main():
    out = {}
    for name, cap in (('caps', 'round'), ('caps-butt', 'butt'), ('joins', None)):
        key = f'red__{name}'
        for fr in ('z1', 'z2', 'hd'):
            imgs = {t: frame(t, key, fr) for t in TAGS + REFS}
            wins = caps_windows(cap, fr) if cap else joins_windows(fr)
            rows = tally(key, wins, imgs)
            print(f'\n{name} {fr}: ink / exact, px > 20/255 off exact   ' + '  '.join(f'{t:>12}' for t in TAGS + REFS))
            tot = {t: [0.0, 0] for t in TAGS + REFS}; tex = 0.0
            for k, row in rows.items():
                print(f'  {str(k):>10}  ' + '  '.join(f'{row[t][0] / row["exact"]:6.3f} {row[t][1]:4d}' if imgs[t] is not None else f'{"-":>11}' for t in TAGS + REFS))
                tex += row['exact']
                for t in TAGS + REFS:
                    tot[t][0] += row[t][0]; tot[t][1] += row[t][1]
                out.setdefault(name, {}).setdefault(fr, {})[str(k)] = {t: [round(row[t][0] / row['exact'], 4), row[t][1]] for t in TAGS + REFS}
            print(f'  {"all":>10}  ' + '  '.join(f'{tot[t][0] / tex:6.3f} {tot[t][1]:4d}' for t in TAGS + REFS))
            out[name][fr]['all'] = {t: [round(tot[t][0] / tex, 4), tot[t][1]] for t in TAGS + REFS}
    json.dump(out, open(f'{HERE}/numbers.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
