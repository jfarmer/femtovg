import sys, math; sys.path.insert(0, '.')
from lib import *
def cd(r, tol):
    da = math.acos(r / (r + tol)) * 2; return max(2, math.ceil(math.pi / da))
S = {616: ((520,190),(570,110),(650,65),(720,60),'#ffffff',2.5), 617: ((590,220),(650,130),(730,100),(790,110),'#ffffff',2),
     629: ((280,360),(230,300),(220,220),(260,160),'#fff9e6',1.5), 634: ((520,100),(560,30),(640,5),(710,25),'#fff9e6',1.5),
     636: ((670,130),(740,60),(820,60),(870,100),'#ffffff',1.5), 637: ((720,200),(800,140),(870,160),(900,210),'#fff9e6',1.5),
     638: ((750,280),(830,240),(890,280),(910,340),'#fff9e6',1.2), 639: ((730,380),(810,360),(870,410),(880,480),'#ecd599',1.5)}
bg = np.array([0x11,0x16,0x1d], float)
hx = lambda c: np.array([int(c[i:i+2], 16) for i in (1,3,5)], float)
fr = sys.argv[1] if len(sys.argv) > 1 else 'hd'
f, s = tf(fr)
o = {n: ours(n, fr).astype(float) for n in ('r20_caps_round', 'r21_caps_butt')}
R = {n: refs(n, fr) for n in ('r20_caps_round', 'r21_caps_butt')}
H, W = o['r20_caps_round'].shape[:2]; yy, xx = np.mgrid[0:H, 0:W] + 0.5
tot = {'fem': 0, 'id': 0, 'pred': 0}
for ln, (p0, c1, c2, p3, col, w) in S.items():
    fg = bg + 0.85 * (hx(col) - bg); d = fg - bg
    cov = lambda im: ((im - bg) @ d) / (d @ d)
    hw = max(w * s, 1.0) / 2; n = cd(hw, 0.125) - 1
    alpha = min(1, w * s)  # sub-fringe strokes are alpha-scaled
    for end, inward in ((p0, c1), (p3, c2)):
        ex, ey = f(*end); ix, iy = f(*inward); ux, uy = ex - ix, ey - iy; L_ = math.hypot(ux, uy); ux /= L_; uy /= L_
        # window: half-disc beyond the end point plus 1.5 px behind it, radius hw+2
        along = (xx - ex) * ux + (yy - ey) * uy; perp = np.abs(-(xx - ex) * uy + (yy - ey) * ux)
        win = (along > -1.5) & (along < hw + 2) & (perp < hw + 2)
        fr_ = {k: cov(o[k])[win].sum() for k in o}; id_ = {k: cov(R[k]['id'].astype(float))[win].sum() for k in o}
        pred = (math.pi / 2 - n / 2 * math.sin(math.pi / n)) * hw * hw * alpha
        dr = id_['r20_caps_round'] - fr_['r20_caps_round']; db = id_['r21_caps_butt'] - fr_['r21_caps_butt']
        a20, _, _ = red(o['r20_caps_round'].astype(np.int16), R['r20_caps_round'])
        print(f'{ln} end {end} hw {hw:.2f} ncap {n+1}: round deficit vs area {dr:+.2f} px2, butt deficit {db:+.2f}, round-minus-butt {dr-db:+.2f}, predicted {pred:.2f}  red in win {int((a20 & win).sum())}')
        tot['fem'] += dr - db; tot['pred'] += pred
print('sum of round-minus-butt deficits', round(tot['fem'], 2), 'predicted', round(tot['pred'], 2))
