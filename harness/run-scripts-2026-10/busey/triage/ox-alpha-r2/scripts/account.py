"""account.py: per-cause accounting of the off-all-three pixels of ox-alpha and muse-spark-1-3-contributor (mst4, z2 + hd),
from the edit runs' masks (png/*_all3.npy, written by off3.py)."""
import numpy as np
ld = lambda n: np.load(f'png/{n}_all3.npy')
tot = {}
def add(k, n): tot[k] = tot.get(k, 0) + int(n)
for fr in ('z2', 'hd'):
    R, N, F = ld(f'ox_orig_{fr}'), ld(f'ox_nodisp_{fr}'), ld(f'ox_nodisp_fm_{fr}')
    assert not (N & ~R).any()
    add('ox feDisplacementMap drawn raw', (R & ~N).sum()); add('ox fringe tips', (R & N & ~F).sum()); add('ox other', (R & N & F).sum())
    print('ox', fr, R.sum(), 'disp', (R & ~N).sum(), 'fringe (cleared by exact fills)', (R & N & ~F).sum(), 'left', (R & N & F).sum())
    R, S, F = ld(f'mu_orig_{fr}'), ld(f'mu_split_{fr}'), ld(f'mu_orig_fm_{fr}')
    print('mu', fr, R.sum(), '#410 lobes (cleared by the split)', (R & ~S).sum(), 'cleared by exact fills', (R & S & ~F).sum(), 'left', (R & S & F).sum())
print(tot)
