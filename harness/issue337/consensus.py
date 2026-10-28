#!/usr/bin/env python3
"""consensus.py BUILD [framing]: per BuseyBench file, the pixels BUILD draws more than 20/255 off all three browsers
(Chromium, Firefox, WebKit) - femtovg's own errors where the browsers agree - as a share of the frame and as
structural share (after a 2 px erosion), and the pixels the browsers themselves disagree on. Writes consensus_BUILD_FR.json."""
import json, os, sys
import numpy as np
from PIL import Image
b = sys.argv[1]; fr = sys.argv[2] if len(sys.argv) > 2 else 'z2'
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def erode(m, it=2):
    for _ in range(it):
        m = m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
    return m
out = {}
for f in json.load(open('files.json')):
    k = f['key']
    ours = L(f'png/{b}_{k}_{fr}.png')
    refs = [L(f'refs/{x}_{k}_{fr}.png') for x in ('chr', 'ff', 'wk')]
    h = min([ours.shape[0]] + [r.shape[0] for r in refs]); w = min([ours.shape[1]] + [r.shape[1] for r in refs])
    ours = ours[:h, :w]; refs = [r[:h, :w] for r in refs]
    off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
    all3 = off[0] & off[1] & off[2]
    spread = np.zeros((h, w), bool)
    for i in range(3):
        for j in range(i + 1, 3):
            spread |= np.abs(refs[i] - refs[j]).max(axis=2) > 20
    out[k] = {'all3': round(100 * float(all3.mean()), 4), 'all3_struct': round(100 * float(erode(all3).mean()), 4),
              'all3_agreed': round(100 * float((all3 & ~spread).mean()), 4), 'browsers_spread': round(100 * float(spread.mean()), 4)}
json.dump(out, open(f'consensus_{b}_{fr}.json', 'w'), indent=1)
print(f'{fr}: pixels > 20 off all three browsers (share of frame), of those where the browsers agree, structural; browsers own spread')
for k, v in sorted(out.items(), key=lambda kv: -kv[1]['all3_agreed'])[:14]:
    print(f"  {k.split('__')[-1]:38s} all3 {v['all3']:6.3f} agreed {v['all3_agreed']:6.3f} struct {v['all3_struct']:6.3f}   spread {v['browsers_spread']:6.3f}")
