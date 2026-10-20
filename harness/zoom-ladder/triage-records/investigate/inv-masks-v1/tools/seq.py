#!/usr/bin/env python3
"""seq.py PREFIX N: frames PREFIX.00.ppm .. PREFIX.(N-1).ppm. Prints the
identity classes of the frames (equal frames share a letter), the first frame
equal to every later one, and each frame's diff to frame 00 and to the frame
before as (px differing at all, px beyond 8/255, max channel diff)."""
import sys
import numpy as np
from PIL import Image


def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(np.int16)


def d(a, b):
    m = np.abs(a - b).max(axis=2)
    return int((m > 0).sum()), int((m > 8).sum()), int(m.max())


prefix, n = sys.argv[1], int(sys.argv[2])
fr = [load(f'{prefix}.{i:02}.ppm') for i in range(n)]
reps, labels = [], []
for i, f in enumerate(fr):
    for j, r in enumerate(reps):
        if np.array_equal(fr[r], f):
            labels.append(j)
            break
    else:
        reps.append(i)
        labels.append(len(reps) - 1)
settle = next(i for i in range(n) if all(np.array_equal(fr[i], fr[j]) for j in range(i, n)))
print('classes', ''.join(chr(ord('A') + l) for l in labels), 'settles_at', settle)
if '-v' in sys.argv:
    for i in range(1, n):
        print(f'  f{i:02} vs f00 {d(fr[i], fr[0])}  vs f{i-1:02} {d(fr[i], fr[i-1])}')
