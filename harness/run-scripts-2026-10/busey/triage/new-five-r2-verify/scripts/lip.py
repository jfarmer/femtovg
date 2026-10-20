import re, sys, json, numpy as np, math
from PIL import Image
from geom import *
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
geo = json.load(open(f'{D}/svg/geo.json'))
def flatten(d):
    toks = re.findall(r'[MCLZ]|-?[\d.]+', d); i = 0; pts = []; cur = None; cmd = None
    while i < len(toks):
        t = toks[i]
        if t in 'MCLZ': cmd = t; i += 1
        if cmd == 'M': cur = np.array([float(toks[i]), float(toks[i + 1])]); pts.append(cur); i += 2; cmd = 'L'
        elif cmd == 'L': cur = np.array([float(toks[i]), float(toks[i + 1])]); pts.append(cur); i += 2
        elif cmd == 'C':
            c = [np.array([float(toks[i + 2 * k]), float(toks[i + 2 * k + 1])]) for k in range(3)]; i += 6
            pts.extend(cubic(cur, c[0], c[1], c[2], 256)[1:]); cur = c[2]
        elif cmd == 'Z': pass
    return np.array(pts)
if __name__ == '__main__':
  for key, tips in (('v_lip', [(413, 672), (611, 672)]), ('v_cres', [(300, 300), (460, 340)])):
      P = flatten(geo[key]['d'])
      for fr in ('z2', 'hd'):
          ox, oy, s = FS[fr]; Q = np.column_stack([ox + P[:, 0] * s, oy + P[:, 1] * s])
          area = abs(0.5 * np.sum(Q[:, 0] * np.roll(Q[:, 1], -1) - np.roll(Q[:, 0], -1) * Q[:, 1])); per = np.sum(np.hypot(*(np.roll(Q, -1, 0) - Q).T))
          ims = {'fv': f'{D}/png/mst4_t__{key}_{fr}.png', 'fm': f'{D}/png/fm_t__{key}_{fr}.png'}
          ims.update({b: f'{D}/refs/{b}_t__{key}_{fr}.png' for b in ('chr', 'ff', 'wk', 'id')})
          ims = {b: np.asarray(Image.open(p).convert('L'), float) / 255 for b, p in ims.items()}
          out = []
          for (u, v) in tips:
              x, y = dev(fr, u, v); x0, y0 = int(x) - 4, int(y) - 4
              cov = coverage(x0, y0, x0 + 8, y0 + 8, lambda X, Y: inside_polys(X, Y, [Q]), ss=32)
              Yc, Xc = np.mgrid[y0:y0 + 8, x0:x0 + 8] + 0.5; m = np.hypot(Xc - x, Yc - y) <= 4
              out.append(' '.join(f'{b} {im[y0:y0 + 8, x0:x0 + 8][m].sum() / cov[m].sum():.2f}' for b, im in ims.items()))
          full = coverage(int(Q[:, 0].min()) - 2, int(Q[:, 1].min()) - 2, int(Q[:, 0].max()) + 3, int(Q[:, 1].max()) + 3, lambda X, Y: inside_polys(X, Y, [Q]), ss=16)
          x0, y0 = int(Q[:, 0].min()) - 2, int(Q[:, 1].min()) - 2
          offa = {b: int((np.abs(im[y0:y0 + full.shape[0], x0:x0 + full.shape[1]] - full) > 20 / 255).sum()) for b, im in ims.items()}
          print(f'{key} {fr}: mean width 2A/P = {2 * area / per:.2f} px; tip-window (r=4px) ink/analytic: ' + ' || '.join(out) + f'\n     px >20/255 off analytic: {offa}')
