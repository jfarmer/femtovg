#!/usr/bin/env python3
"""usage: sheets.py out.png title name1 name2 ... -> rows of [resvg 0.48.1 | this PR | Chromium | Firefox] at 200 px, one row per x/<name> (names dir_test)."""
import sys, os, subprocess
from PIL import Image, ImageDraw
out, title, names = sys.argv[1], sys.argv[2], sys.argv[3:]
OLD = os.path.expanduser('~/src/femtovg-wt/tools/bin/resvg')
F = os.path.expanduser('~/src/femtovg-wt/runs/dir/resvg/crates/resvg/tests/fonts')
def load(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im); return bg.convert('RGB')
S = 200; cols = [('old', 'resvg 0.48.1'), ('rs', 'this PR'), ('chr', 'Chromium 131'), ('ff', 'Firefox')]
sheet = Image.new('RGB', (len(cols) * (S + 6) + 6, len(names) * (S + 20) + 24), 'white'); d = ImageDraw.Draw(sheet)
d.text((6, 4), title, fill='black')
for r, n in enumerate(names):
    base = f'x/{n}'
    if not os.path.exists(f'{base}.old.png'):
        subprocess.run([OLD, f'{base}.svg', f'{base}.old.png', '-w', '300', '--use-fonts-dir', F, '--skip-system-fonts', '--serif-family', 'Noto Serif', '--sans-serif-family', 'Noto Sans', '--monospace-family', 'Noto Mono'], check=True)
    y = 24 + r * (S + 20)
    d.text((6, y), n.replace('_', '/', 1), fill='black')
    for c, (k, label) in enumerate(cols):
        im = load(f'{base}.{k}.png').resize((S, S), Image.LANCZOS)
        x = 6 + c * (S + 6)
        sheet.paste(im, (x, y + 12))
        if r == 0: d.text((x + 2, 14), label, fill='black')
sheet.save(out); print(out, sheet.size)
