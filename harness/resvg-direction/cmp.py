#!/usr/bin/env python3
"""usage: cmp.py x/name.svg [resvg-binary]  -> x/name.sheet.png: resvg | Chromium | Firefox | WebKit (300 px wide, resvg test fonts)."""
import os, subprocess, sys
from PIL import Image, ImageDraw
svg = sys.argv[1]; base = svg[:-4]
RB = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/src/femtovg-wt/runs/dir/target/release/resvg')
F = os.path.expanduser('~/src/femtovg-wt/runs/dir/resvg/crates/resvg/tests/fonts')
subprocess.run([RB, svg, f'{base}.rs.png', '-w', '300', '--use-fonts-dir', F, '--skip-system-fonts', '--serif-family', 'Noto Serif', '--sans-serif-family', 'Noto Sans', '--monospace-family', 'Noto Mono'], check=True)
subprocess.run([sys.executable, os.path.expanduser('~/src/femtovg-wt/runs/dir/br.py'), svg, base], check=True, capture_output=True)
def load(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im); return bg.convert('RGB')
ims = [(k, load(f'{base}.{k}.png')) for k in ('rs', 'chr', 'ff', 'wk') if os.path.exists(f'{base}.{k}.png')]
w, h = ims[0][1].size
sheet = Image.new('RGB', (len(ims) * (w + 4), h + 14), 'white')
d = ImageDraw.Draw(sheet)
for i, (k, im) in enumerate(ims):
    sheet.paste(im, (i * (w + 4), 14)); d.text((i * (w + 4) + 4, 1), {'rs': 'resvg', 'chr': 'Chromium 131', 'ff': 'Firefox', 'wk': 'WebKit'}[k], fill='black')
sheet.save(f'{base}.sheet.png'); print(f'{base}.sheet.png')
