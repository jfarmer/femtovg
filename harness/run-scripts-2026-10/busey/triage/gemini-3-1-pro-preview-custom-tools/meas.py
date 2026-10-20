import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emap import L, masks
SC = os.path.dirname(os.path.abspath(__file__))
# regions in z2 px (x0,y0,x1,y1)
import numpy as _np
_Y, _X = _np.mgrid[0:260, 0:460]
R = {'hair': _Y < 105, 'eyes': (_Y >= 105) & (_Y < 125) & (_X >= 155) & (_X <= 300),
     'ears': (_Y >= 105) & (_Y < 195) & ((_X < 155) | (_X > 300)), 'mouth': _Y >= 195}
R['mid'] = ~(R['hair'] | R['eyes'] | R['ears'] | R['mouth'])
def meas(name, png=None, refdir=None):
    k = name if '__' in name else f't__{name}'
    ours = L(png or f'{SC}/png/mst2_{k}_z2.png')
    refs = [L(f'{refdir or SC+"/refs"}/{x}_{k}_z2.png') for x in ('chr','ff','wk')]
    a, ag, sp = masks(ours, refs)
    out = {'all3': int(a.sum()), 'agreed': int(ag.sum())}
    for r,m in R.items(): out[r] = int((a & m).sum()); out[r+'_ag'] = int((ag & m).sum())
    return out
if __name__ == '__main__':
    names = sys.argv[1:] or sorted(f[5:-7] for f in os.listdir(f'{SC}/png') if f.startswith('mst2_t'))
    print(f'{"variant":16s}', ' '.join(f'{c:>7s}' for c in ['all3','agreed',*[r+x for r in R for x in ('','_ag')]]))
    for n in names:
        o = meas(n); print(f'{n:16s}', ' '.join(f'{v:7d}' for v in o.values()))
