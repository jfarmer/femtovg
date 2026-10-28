#!/usr/bin/env python3
"""The five references (id chr chg ff wk) as corpus_run's refs*.py make them, but with this directory's make_ref.py,
into OUTDIR/PREFIX_KEY_FRAMING.png (resumable).

  refs_local.py OUTDIR [match=SUBSTR]... [who=id,chr,chg,ff,wk] [framings=z1,z2,z4,hd]"""
import json, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import FRAMINGS, CHR, FF, BIN  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
GPU = ['--enable-gpu', '--use-angle=metal', '--enable-gpu-rasterization', '--ignore-gpu-blocklist']
WK = os.environ.get('WK_SHOT', f'{BIN}/wk_shot')
out = os.path.abspath(sys.argv[1])
matches, who, framings = [], ['id', 'chr', 'chg', 'ff', 'wk'], ['z1', 'z2', 'z4', 'hd']
for a in sys.argv[2:]:
    k, v = a.split('=', 1)
    if k == 'match':
        matches.append(v)
    elif k == 'who':
        who = v.split(',')
    elif k == 'framings':
        framings = v.split(',')
os.makedirs(out, exist_ok=True)
fs = [f for f in json.load(open(f'{HERE}/files.json')) if not matches or any(m in f['key'] for m in matches)]


def page(f, framing, tag):
    fr, z = FRAMINGS[framing]
    html = f'{out}/{f["key"]}_{framing}_{tag}.html'
    r = subprocess.run([sys.executable, f'{HERE}/make_ref.py', f['path'], str(z)], capture_output=True, text=True,
                       env={**os.environ, **fr})
    if r.returncode != 0 or '<svg' not in r.stdout:
        return None
    open(html, 'w').write(r.stdout)
    return html


def crop(png, fr):
    w, h = int(fr['FRAME_W']), int(fr['FRAME_H'])
    im = Image.open(png).convert('RGB')
    if im.size != (w, h):
        im.crop((0, 0, w, h)).save(png)
    else:
        im.save(png)


def shoot(job):
    browser, f, framing = job
    png = f'{out}/{browser}_{f["key"]}_{framing}.png'
    if os.path.exists(png):
        return 'kept'
    fr, _ = FRAMINGS[framing]
    w, h = int(fr['FRAME_W']), int(fr['FRAME_H'])
    html = page(f, framing, browser)
    if html is None:
        return 'unframed'
    try:
        if browser == 'chr':
            subprocess.run([CHR, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                            f'--window-size={w},{h}', '--default-background-color=FFFFFFFF', f'--screenshot={png}',
                            f'file://{html}'], capture_output=True, timeout=180)
        elif browser == 'chg':
            subprocess.run([CHR, '--headless', *GPU, '--hide-scrollbars', '--force-device-scale-factor=1',
                            f'--window-size={w},{h}', '--default-background-color=FFFFFFFF', f'--screenshot={png}',
                            f'file://{html}'], capture_output=True, timeout=180)
        elif browser == 'id':
            scale = 4 if w > 1000 else 8
            big = png[:-4] + '_big.png'
            subprocess.run([CHR, '--headless', *GPU, '--hide-scrollbars', f'--force-device-scale-factor={scale}',
                            f'--window-size={w},{h}', '--default-background-color=FFFFFFFF', f'--screenshot={big}',
                            f'file://{html}'], capture_output=True, timeout=300)
            if not os.path.exists(big):
                return 'failed'
            im = np.asarray(Image.open(big).convert('RGB'), dtype=np.float64)
            os.remove(big)
            im = im[:h * scale, :w * scale].reshape(h, scale, w, scale, 3).mean(axis=(1, 3))
            Image.fromarray(np.rint(im).astype(np.uint8)).save(png)
            return 'made'
        elif browser == 'ff':
            prof = tempfile.mkdtemp(prefix='ffprof')
            try:
                for _ in range(2):
                    try:
                        subprocess.run([FF, '--headless', '--no-remote', '--profile', prof, f'--window-size={w},{h}',
                                        '--screenshot', png, f'file://{html}'], capture_output=True, timeout=120)
                    except subprocess.TimeoutExpired:
                        pass
                    if os.path.exists(png):
                        break
            finally:
                shutil.rmtree(prof, ignore_errors=True)
        elif browser == 'wk':
            try:
                subprocess.run([WK, html, png, str(w), str(h)], capture_output=True, timeout=60)
            except subprocess.TimeoutExpired:
                pass
    finally:
        if os.path.exists(html):
            os.remove(html)
    if not os.path.exists(png):
        return 'failed'
    crop(png, fr)
    return 'made'


workers = {'chr': 6, 'chg': 3, 'id': 3, 'ff': 3, 'wk': 4}
for b in who:
    counts = {}
    with ThreadPoolExecutor(workers[b]) as ex:
        for r in ex.map(shoot, [(b, f, fr) for f in fs for fr in framings]):
            counts[r] = counts.get(r, 0) + 1
    print(b, counts, flush=True)
