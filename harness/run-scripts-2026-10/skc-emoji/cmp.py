import sys, os, glob
import numpy as np
from PIL import Image
R = os.path.expanduser('~/src/femtovg-wt/runs/wpt-text/refs')
W = os.path.expanduser('~/src/femtovg-wt/runs/inv-emoji/refs')
G = '28-color-emoji-and-png-glyphs'
F = sys.argv[1]; z = sys.argv[2] if len(sys.argv)>2 else '1'
def load(p): return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def px(a,b,t=20):
    if a.shape!=b.shape: return float('nan')
    return 100*(np.abs(a-b).max(axis=2)>t).mean()
names = sorted({os.path.basename(p).rsplit('_',2)[0] for p in glob.glob(f'{F}/*_z{z}.ppm')})
print(f'{"file":44s} {"svg":>6s} {"glyphs":>6s} {"shape":>6s} | ff:svg/gl  wk8:svg/gl | chr-ff chr-wk8 chr-wkold')
for n in names:
    chr_ = load(f'{R}/chr_wpttext__{G}__{n}_z{z}.png')
    ff = f'{R}/ff_wpttext__{G}__{n}_z{z}.png'; ff = load(ff) if os.path.exists(ff) else None
    wk = f'{W}/wk8_{n}_z{z}.png'; wk = load(wk) if os.path.exists(wk) else None
    wko = f'{R}/wk_wpttext__{G}__{n}_z{z}.png'; wko = load(wko) if os.path.exists(wko) else None
    fr = {m: load(f'{F}/{n}_{m}_z{z}.ppm') for m in ('svg','glyphs','shape') if os.path.exists(f'{F}/{n}_{m}_z{z}.ppm')}
    row = f'{n:44s} ' + ' '.join(f'{px(fr[m],chr_):6.2f}' if m in fr else '     -' for m in ('svg','glyphs','shape'))
    row += ' | ' + (f'{px(fr["svg"],ff):.2f}/{px(fr["glyphs"],ff):.2f}' if ff is not None else '-')
    row += '  ' + (f'{px(fr["svg"],wk):.2f}/{px(fr["glyphs"],wk):.2f}' if wk is not None else '-')
    row += ' | ' + ' '.join(f'{px(chr_,x):.2f}' if x is not None else '-' for x in (ff,wk,wko))
    print(row)
