#!/usr/bin/env python3
"""scenes_area.py SCENES OUT_DIR : each scene drawn on a Chromium 131 canvas eight times larger (ctx.scale(8, 8)) and
averaged over each 8 x 8 block: the share of each pixel the shapes cover, over white - the exact-area reference."""
import json, os, subprocess, sys
import numpy as np
from PIL import Image

CHR = os.path.expanduser('~/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/'
                         'chrome-headless-shell-mac-arm64/chrome-headless-shell')
spec = json.load(open(sys.argv[1]))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
S = 8
w, h = spec['width'], spec['height']
for i, scene in enumerate(spec['scenes']):
    html = f'''<!doctype html><html><body style="margin:0;background:#fff">
<canvas id="c" width="{w * S}" height="{h * S}" style="display:block"></canvas>
<script>
const ops = {json.dumps(scene['ops'])};
const ctx = document.getElementById('c').getContext('2d');
ctx.scale({S}, {S});
const poly = (p) => {{ ctx.beginPath(); ctx.moveTo(p[0][0], p[0][1]); for (const q of p.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath(); }};
for (const op of ops) {{
  if (op[0] === 'save') ctx.save();
  else if (op[0] === 'restore') ctx.restore();
  else if (op[0] === 'clip') {{ poly(op[1]); ctx.clip(); }}
  else if (op[0] === 'clippath') {{ ctx.beginPath(); for (const p of op[1]) {{ ctx.moveTo(p[0][0], p[0][1]); for (const q of p.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath(); }} ctx.clip(op[2] || 'nonzero'); }}
  else if (op[0] === 'composite') ctx.globalCompositeOperation = op[1];
  else if (op[0] === 'fill') {{ ctx.fillStyle = op[1]; poly(op[2]); ctx.fill(); }}
  else if (op[0] === 'fillpath') {{ ctx.fillStyle = op[1]; ctx.beginPath(); for (const p of op[2]) {{ ctx.moveTo(p[0][0], p[0][1]); for (const q of p.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath(); }} ctx.fill(op[3] || 'nonzero'); }}
}}
</script></body></html>'''
    page = f'{out}/{i}.html'
    open(page, 'w').write(html)
    big = f'{out}/{i}_big.png'
    subprocess.run([CHR, '--headless', '--hide-scrollbars', '--force-device-scale-factor=1', f'--window-size={w * S},{h * S}',
                    f'--screenshot={big}', f'file://{page}'], capture_output=True, timeout=120)
    a = np.asarray(Image.open(big).convert('RGB').crop((0, 0, w * S, h * S)), dtype=np.float64)
    a = a.reshape(h, S, w, S, 3).mean(axis=(1, 3))
    Image.fromarray((a + 0.5).astype(np.uint8)).save(f'{out}/{i}.png')
    os.remove(page)
    os.remove(big)
print('drew', len(spec['scenes']), 'scenes at 8x and averaged')
