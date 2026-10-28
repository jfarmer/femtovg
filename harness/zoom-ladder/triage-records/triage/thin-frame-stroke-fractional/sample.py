import sys, numpy as np
from PIL import Image
d = sys.argv[1]; tags = sys.argv[2].split(','); names = sys.argv[3].split(',')
for name in names:
    for zs in ['1', '0.75', '0.5', '0.33', '0.25']:
        z = float(zs)
        y0 = 130 - 100 * z
        rows = list(range(int(y0) - 1, int(y0) + 3))
        line = f'{name:11} z={zs:5} rows {rows}: '
        for t in tags:
            try:
                a = np.asarray(Image.open(f'{d}/{t}_{name}_z{zs}.png').convert('L'), dtype=int)
            except FileNotFoundError:
                continue
            cov = [round(1 - a[r, 230] / 255, 3) for r in rows]
            line += f'{t}={cov} '
        print(line)
