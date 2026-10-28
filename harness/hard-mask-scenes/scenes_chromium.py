#!/usr/bin/env python3
"""scenes_chromium.py OUT_DIR : draw every scene of SCENES (default scenes.json beside this script) on a 2D canvas in headless Chromium 131 and save
each as OUT_DIR/<index>.png (the canvas over white)."""
import json, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CHR = os.path.expanduser('~/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/'
                         'chrome-headless-shell-mac-arm64/chrome-headless-shell')
spec = json.load(open(os.environ.get('SCENES', f'{HERE}/scenes.json')))
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
w, h = spec['width'], spec['height']
for i, scene in enumerate(spec['scenes']):
    html = f'''<!doctype html><html><body style="margin:0;background:#fff">
<canvas id="c" width="{w}" height="{h}" style="display:block"></canvas>
<script>
const ops = {json.dumps(scene['ops'])};
const ctx = document.getElementById('c').getContext('2d');
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
    png = f'{out}/{i}.png'
    subprocess.run([CHR, '--headless', '--hide-scrollbars', '--force-device-scale-factor=1', f'--window-size={w},{h}',
                    f'--screenshot={png}', f'file://{page}'], capture_output=True, timeout=120)
    Image.open(png).convert('RGB').crop((0, 0, w, h)).save(png)
    os.remove(page)
print('drew', len(spec['scenes']), 'scenes with Chromium')
