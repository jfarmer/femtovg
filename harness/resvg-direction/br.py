#!/usr/bin/env python3
"""usage: br.py file.svg outprefix [W H]  -> outprefix.{chr,ff,wk}.html pages and PNGs (Chromium 131, Firefox, WebKit).
The SVG is inlined into an HTML page with @font-face for the resvg test fonts, scaled to W x H CSS px (default 300 x 300)."""
import os, re, subprocess, sys, tempfile, shutil
svg, out = sys.argv[1], sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 300
H = int(sys.argv[4]) if len(sys.argv) > 4 else 300
F = os.path.expanduser('~/src/femtovg-wt/runs/dir/resvg/crates/resvg/tests/fonts')
CHR = os.path.expanduser(os.environ.get('CHROMIUM', '~/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
FF = '/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox'
WK = os.path.expanduser('~/src/femtovg-wt/bin/wk_shot')
fonts = {'Noto Sans': 'NotoSans-Regular.ttf', 'Amiri': 'Amiri-Regular.ttf', 'Noto Serif': 'NotoSerif-Regular.ttf', 'Noto Mono': 'NotoMono-Regular.ttf', 'Noto Sans Arabic': 'Amiri-Regular.ttf'}
css = ''.join(f'@font-face{{font-family:"{n}";src:url("file://{F}/{f}")}}' for n, f in fonts.items())
t = open(svg).read()
t = re.sub(r'<\?xml[^>]*\?>', '', t)
t = re.sub(r'<!DOCTYPE[^>]*>', '', t)
html = f'<!doctype html><meta charset="utf-8"><style>{css}html,body{{margin:0;background:#fff}}svg{{display:block;width:{W}px;height:{H}px}}</style>{t}'
page = f'{out}.html'
open(page, 'w').write(html)
subprocess.run([CHR, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1', f'--window-size={W},{H}', '--default-background-color=FFFFFFFF', f'--screenshot={out}.chr.png', f'file://{os.path.abspath(page)}'], capture_output=True, timeout=120)
prof = tempfile.mkdtemp(prefix='ffprof')
try:
    subprocess.run([FF, '--headless', '--no-remote', '--profile', prof, f'--window-size={W},{H}', '--screenshot', os.path.abspath(f'{out}.ff.png'), f'file://{os.path.abspath(page)}'], capture_output=True, timeout=120)
except subprocess.TimeoutExpired:
    pass
import time
for _ in range(40):
    if os.path.exists(f'{out}.ff.png'): time.sleep(0.5); break
    time.sleep(0.25)
shutil.rmtree(prof, ignore_errors=True)
subprocess.run([WK, os.path.abspath(page), f'{out}.wk.png', str(W), str(H)], capture_output=True, timeout=60)
from PIL import Image
for k in ('chr', 'ff', 'wk'):
    p = f'{out}.{k}.png'
    if os.path.exists(p):
        im = Image.open(p).convert('RGB'); im.crop((0, 0, W, H)).save(p)
print(' '.join(k for k in ('chr', 'ff', 'wk') if os.path.exists(f'{out}.{k}.png')))
