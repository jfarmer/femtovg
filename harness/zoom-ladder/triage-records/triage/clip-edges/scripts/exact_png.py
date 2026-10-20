import sys, numpy as np
from PIL import Image
from exact_circle import coverage_circle, framing, compose
cx, cy, r, z = map(float, sys.argv[1:5]); out = sys.argv[5]
X, Y, R = framing(cx, cy, r, z)
Image.fromarray(np.rint(compose(coverage_circle(X, Y, R, ss=64))).astype(np.uint8)).save(out)
