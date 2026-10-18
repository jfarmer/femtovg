#!/usr/bin/env python3
"""scenes_browser.py chromium|firefox|webkit OUT_DIR : draw every scene of SCENES (default scenes.json beside this
script) on a 2D canvas in a browser and save each as OUT_DIR/<index>.png, the canvas over white. SCENES_SCALE draws
them at that many device pixels a canvas pixel, as a canvas sized for that devicePixelRatio and scaled by it.

  chromium  headless Chromium 131 (puppeteer's headless shell, as scenes_chromium.py and the corpus refs)
  firefox   Firefox headless --screenshot (FIREFOX, default Firefox Developer Edition)
  webkit    the system WebKit through wk_shot (WK_SHOT, default $HARNESS_BIN/wk_shot; ../corpus_run/wk_shot.swift)"""
import json, os, shutil, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CHR = os.environ.get('CHROMIUM', os.path.expanduser(
    '~/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
FF = os.environ.get('FIREFOX', '/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox')
WK = os.environ.get('WK_SHOT', os.path.join(os.environ.get('HARNESS_BIN', os.path.join(HERE, '../../../bin')), 'wk_shot'))


def page(ops, w, h, scale):
    cw, ch = round(w * scale), round(h * scale)
    return cw, ch, f'''<!doctype html><html><body style="margin:0;background:#fff;overflow:hidden">
<canvas id="c" width="{cw}" height="{ch}" style="display:block"></canvas>
<script>
const ops = {json.dumps(ops)};
const ctx = document.getElementById('c').getContext('2d');
ctx.scale({scale}, {scale});
const poly = (p) => {{ ctx.beginPath(); ctx.moveTo(p[0][0], p[0][1]); for (const q of p.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath(); }};
const contours = (cs) => {{ ctx.beginPath(); for (const p of cs) {{ ctx.moveTo(p[0][0], p[0][1]); for (const q of p.slice(1)) ctx.lineTo(q[0], q[1]); ctx.closePath(); }} }};
for (const op of ops) {{
  if (op[0] === 'save') ctx.save();
  else if (op[0] === 'restore') ctx.restore();
  else if (op[0] === 'clip') {{ poly(op[1]); ctx.clip(); }}
  else if (op[0] === 'clippath') {{ contours(op[1]); ctx.clip(op[2] || 'nonzero'); }}
  else if (op[0] === 'composite') ctx.globalCompositeOperation = op[1];
  else if (op[0] === 'fill') {{ ctx.fillStyle = op[1]; poly(op[2]); ctx.fill(); }}
  else if (op[0] === 'fillpath') {{ ctx.fillStyle = op[1]; contours(op[2]); ctx.fill(op[3] || 'nonzero'); }}
}}
</script></body></html>'''


def shoot(browser, html, png, w, h):
    if browser == 'chromium':
        subprocess.run([CHR, '--headless', '--hide-scrollbars', '--force-device-scale-factor=1', f'--window-size={w},{h}',
                        f'--screenshot={png}', f'file://{html}'], capture_output=True, timeout=120)
    elif browser == 'firefox':
        prof = tempfile.mkdtemp(prefix='ffprof')
        try:
            subprocess.run([FF, '--headless', '--no-remote', '--profile', prof, f'--window-size={w},{h}',
                            '--screenshot', png, f'file://{html}'], capture_output=True, timeout=120)
        finally:
            shutil.rmtree(prof, ignore_errors=True)
    elif browser == 'webkit':
        subprocess.run([WK, html, png, str(w), str(h)], capture_output=True, timeout=60)
    else:
        sys.exit(f'no browser {browser}')


browser, out = sys.argv[1], sys.argv[2]
spec = json.load(open(os.environ.get('SCENES', f'{HERE}/scenes.json')))
scale = float(os.environ.get('SCENES_SCALE', '1'))
os.makedirs(out, exist_ok=True)
for i, scene in enumerate(spec['scenes']):
    w, h, html = page(scene['ops'], spec['width'], spec['height'], scale)
    path = os.path.abspath(f'{out}/{i}.html')
    open(path, 'w').write(html)
    png = os.path.abspath(f'{out}/{i}.png')
    shoot(browser, path, png, w, h)
    os.remove(path)
    if not os.path.exists(png):
        sys.exit(f'{browser} drew no {png}')
    Image.open(png).convert('RGB').crop((0, 0, w, h)).save(png)
print(f'drew {len(spec["scenes"])} scenes with {browser} at {scale:g}x')
