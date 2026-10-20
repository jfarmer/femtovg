"""redimg.py OURS CHR FF WK OUT.png [x0 y0 x1 y1 scale]: ours with the off-all-three pixels painted red (agreed) / magenta (browsers spread)."""
import sys, numpy as np
from PIL import Image
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
ours, *refs = [L(p) for p in sys.argv[1:5]]
h = min([ours.shape[0]] + [r.shape[0] for r in refs]); w = min([ours.shape[1]] + [r.shape[1] for r in refs])
ours = ours[:h, :w]; refs = [r[:h, :w] for r in refs]
off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
all3 = off[0] & off[1] & off[2]
spread = np.zeros((h, w), bool)
for i in range(3):
    for j in range(i + 1, 3):
        spread |= np.abs(refs[i] - refs[j]).max(axis=2) > 20
img = (ours * 0.45 + 140).astype(np.uint8)
img[all3 & ~spread] = (255, 0, 0); img[all3 & spread] = (255, 0, 255)
im = Image.fromarray(img)
if len(sys.argv) > 6:
    x0, y0, x1, y1, s = map(int, sys.argv[6:11])
    im = im.crop((x0, y0, x1, y1)).resize(((x1-x0)*s, (y1-y0)*s), Image.NEAREST)
im.save(sys.argv[5])
