import os, subprocess, sys
import numpy as np
from PIL import Image
from common import *
for rule in ('nonzero', 'evenodd'):
    for fr in ('z1', 'z2', 'z4', 'hd', 'z05', 'z025', 'z01'):
        f, z = FRAMINGS[fr]
        img = {}
        for build in ('m8', 'rv'):
            for name in (f'hole-{rule}', f'hole-strip-{rule}'):
                ppm = f'{OUT}/tmp/ctl_{build}_{name}_{fr}.ppm'
                subprocess.run([BUILDS[build][0], f'{z:g}', ppm, f'{DA}/corpus/pressure/{name}.svg'],
                               env={**os.environ, **f, **SWEEP_ENV, **BUILDS[build][1]}, capture_output=True)
                img[(build, name)] = np.asarray(Image.open(ppm).convert('RGB'), dtype=np.int16)
                os.remove(ppm)
        def d(x, y):
            m = np.abs(x - y).max(axis=2)
            return f'{int((m > 0).sum())} px differ (max {int(m.max())})'
        print(f'{rule:8s} {fr:5s} strip vs control: m8 {d(img["m8", f"hole-strip-{rule}"], img["m8", f"hole-{rule}"])}; '
              f'rv {d(img["rv", f"hole-strip-{rule}"], img["rv", f"hole-{rule}"])}; control m8 vs rv {d(img["m8", f"hole-{rule}"], img["rv", f"hole-{rule}"])}')
