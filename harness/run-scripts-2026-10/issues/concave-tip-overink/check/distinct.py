# Distinct strip inner vertices (u = 0) near the tips, from the Void dumps; tips' own (within 2 px of the point) apart.
import re, sys, numpy as np
src = open('/Users/matt/src/femtovg-wt/da/harness/concave-tip-overink/fringe_model.py').read()
defs = src[:src.index('# Each reduction')].replace("RUN = sys.argv[1] if len(sys.argv) > 1 else '.'", "RUN='.'")
ns = {}; exec(defs, ns)
R = '/Users/matt/src/femtovg-wt/runs/issues/concave-tip-overink-review/'
TIPS = [ns['z2'](280, 725), ns['z2'](744, 725)]
for name in ('wedge', 'wedge-split', 'lip'):
    out = open(f'{R}{name}_dump.txt').read().splitlines()
    n = int(out[0].split()[1]); V = np.array([[float(t) for t in l.split()] for l in out[1:1 + n]])
    c = [l for l in out[1 + n:] if 'ConcaveFill' in l][0]
    dr = [tuple(int(x) for x in t) for t in re.findall(r'fill_verts: Some\(\((\d+), (\d+)\)\), stroke_verts: Some\(\((\d+), (\d+)\)\)', c)]
    d = re.search(r'<path d="([^"]*)"', open(f'/Users/matt/src/femtovg-wt/da/harness/concave-tip-overink/{name}.svg').read()).group(1).replace(',', ' ')
    poly = ns['flatten'](d)
    S = V[dr[0][2]:dr[0][2] + dr[0][3]]
    inner = S[S[:, 2] == 0.0][:, :2]
    uniq = np.unique(np.round(inner, 3), axis=0)
    dist = np.min([np.hypot(*(uniq - t).T) for t in TIPS], axis=0)
    near = dist < 15; own = dist < 2
    out_ = ~ns['inside'](poly, uniq)
    print(f'{name:12s} pushed near {int((np.min([np.hypot(*(inner - t).T) for t in TIPS], axis=0) < 15).sum())}, distinct near {near.sum()} '
          f'(outside {(near & out_).sum()}); tips own {own.sum()} (outside {(own & out_).sum()}); added by pieces/flattening {(near & ~own).sum()} (outside {(near & ~own & out_).sum()})')
    print('   own-vertex distances from the point:', np.round(np.sort(dist[own]), 2))
