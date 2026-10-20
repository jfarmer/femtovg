import sys, numpy as np
from PIL import Image
def load(p):
    im = Image.open(p).convert('RGBA') if not p.endswith('.ppm') else Image.open(p).convert('RGB')
    a = np.asarray(im).astype(int)
    if a.shape[2] == 4:
        # composite on white
        al = a[..., 3:4] / 255.0
        a = (a[..., :3] * al + 255 * (1 - al)).round().astype(int)
    return a
def diff(a, b):
    d = np.abs(load(a) - load(b)).max(axis=2)
    return dict(any=int((d > 0).sum()), n8=int((d > 8).sum()), n20=int((d > 20).sum()), max=int(d.max()))
if __name__ == '__main__':
    base = sys.argv[1]
    for o in sys.argv[2:]:
        print(f"{o:60s}", diff(base, o))
