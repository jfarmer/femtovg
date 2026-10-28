import sys; sys.path.insert(0, '.')
from lib import *
def cov(img, bg, fg):
    bg = np.array(bg, float); fg = np.array(fg, float); d = fg - bg
    return ((img.astype(float) - bg) @ d) / (d @ d)
def hx(c): return [int(c[i:i + 2], 16) for i in (1, 3, 5)]
CASES = {
 'r10_lip_skin': ('#df9a78', '#ab4f47', [(360, 640, 420, 735), (604, 640, 664, 735)]),
 'r11_lip_dark': ('#1f0305', '#ab4f47', [(360, 640, 420, 735), (604, 640, 664, 735)]),
 'r12_nose': ('#e8a080', '#5c1f14', [(486, 586, 500, 596), (524, 586, 538, 596)]),
 'r30_dart': ('#df9a78', '#ab4f47', [(296, 494, 330, 506), (770, 594, 804, 607)]),
 'r31_dart_split10': ('#df9a78', '#ab4f47', [(296, 494, 330, 506), (770, 594, 804, 607)]),
}
for n, (bg, fg, wins) in CASES.items():
    for fr in ('z2', 'hd'):
        f, s = tf(fr); R = refs(n, fr)
        line = f'{n:18s} {fr}'
        for tag in ('', 'nt_', 'fm_'):
            o = ours(n, fr, tag); a, ag, sp = red(o, R); oi = offid(o, R)
            ink = 0; inkid = 0; inkb = {b: 0 for b in ('chr', 'ff', 'wk')}
            for (x0, y0, x1, y1) in wins:
                X0, Y0 = f(x0, y0); X1, Y1 = f(x1, y1)
                sl = np.s_[int(Y0):int(np.ceil(Y1)), int(X0):int(np.ceil(X1))]
                ink += cov(o, hx(bg), hx(fg))[sl].sum(); inkid += cov(R['id'], hx(bg), hx(fg))[sl].sum()
                for b in inkb: inkb[b] += cov(R[b], hx(bg), hx(fg))[sl].sum()
            line += f' | {tag or "mst"} red {a.sum():3d} offid {oi.sum():3d} tip {ink / inkid:.2f}'
        line += ' | browsers ' + ' '.join(f'{b} {v / inkid:.2f}' for b, v in inkb.items())
        line += f" offid {' '.join(str(int(offid(R[b], R).sum())) for b in ('chr','ff','wk'))}"
        print(line)
