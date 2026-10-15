#!/usr/bin/env python3
"""judge.py A B [over=2] [workers=3] : for every frame classify_A_B.jsonl lists with a change above `over` levels,
render Chromium at 1x and at 8x (box-filtered down: the area reference) and judge, at the pixels A and B render more
than `over` apart, which build is nearer the area. Writes judge_A_B.jsonl and prints a summary."""
import json, os, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus_run'))
from common import *  # noqa: E402,F403

A, B = sys.argv[1], sys.argv[2]
opts = dict(x.split('=', 1) for x in sys.argv[3:])
over = int(opts.get('over', 2))
HERE = os.environ.get('CORPUS_RUN_OUT', os.getcwd())
by_key = {f['key']: f for f in files()}
rows = [json.loads(l) for l in open(f'{HERE}/classify_{A}_{B}.jsonl')]
rows = [r for r in rows if r['max'] > over]


def tag():
    return f'{os.getpid()}_{threading.get_ident()}'


def build_frame(build, f, framing):
    binary, extra = BUILDS[build]
    fr, z = FRAMINGS[framing]
    ppm = f'{HERE}/tmp/j_{build}_{tag()}.ppm'
    subprocess.run([binary, f'{z:g}', ppm, f['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra},
                   capture_output=True, timeout=600)
    img = np.asarray(Image.open(ppm).convert('RGB')).astype(float)
    os.remove(ppm)
    return img


def chromium(f, framing, scale):
    fr, z = FRAMINGS[framing]
    w, h = int(fr['FRAME_W']), int(fr['FRAME_H'])
    html = f'{HERE}/tmp/j_{tag()}.html'
    r = subprocess.run([sys.executable, f'{HARN}/make_ref.py', f['path'], str(z)], capture_output=True, text=True,
                       env={**os.environ, **fr})
    if r.returncode != 0 or '<svg' not in r.stdout:
        return None
    open(html, 'w').write(r.stdout)
    png = f'{HERE}/tmp/j_{tag()}_{scale}.png'
    subprocess.run([CHR, '--headless', '--hide-scrollbars', f'--force-device-scale-factor={scale}',
                    f'--window-size={w},{h}', f'--screenshot={png}', f'file://{html}'], capture_output=True, timeout=300)
    img = np.asarray(Image.open(png).convert('RGB')).astype(float)[:h * scale, :w * scale]
    os.remove(png)
    os.remove(html)
    if scale > 1:
        img = img.reshape(h, scale, w, scale, 3).mean(axis=(1, 3))
    return img


def job(r):
    f = by_key[r['key']]
    a, b = build_frame(A, f, r['framing']), build_frame(B, f, r['framing'])
    area = chromium(f, r['framing'], 8)
    if area is None:
        return {**r, 'judged': False}
    chr1 = chromium(f, r['framing'], 1)
    moved = np.abs(a - b).max(axis=2) > over
    ea = np.abs(a - area).max(axis=2)[moved]
    eb = np.abs(b - area).max(axis=2)[moved]
    ec = np.abs(chr1 - area).max(axis=2)[moved]
    return {**r, 'judged': True, 'moved': int(moved.sum()), 'nearer': int((eb < ea).sum()),
            'farther': int((eb > ea).sum()), 'err_a': float(ea.mean()), 'err_b': float(eb.mean()),
            'err_chromium': float(ec.mean())}


with open(f'{HERE}/judge_{A}_{B}.jsonl', 'w') as out, ThreadPoolExecutor(int(opts.get('workers', 3))) as pool:
    results = list(pool.map(job, rows))
    for res in results:
        out.write(json.dumps(res) + '\n')
judged = [r for r in results if r['judged']]
print(f'{len(rows)} frames changed by more than {over} levels; {len(judged)} judged against the area reference')
print('frames nearer the area with', B, ':', sum(r['err_b'] < r['err_a'] for r in judged),
      ' farther:', sum(r['err_b'] > r['err_a'] for r in judged))
print('pixels nearer:', sum(r['nearer'] for r in judged), ' farther:', sum(r['farther'] for r in judged))
for r in sorted(judged, key=lambda r: r['err_b'] - r['err_a'], reverse=True)[:12]:
    print(f"  {r['key'][8:56]:48s} {r['framing']:5s} moved={r['moved']:4d} nearer={r['nearer']:4d} farther={r['farther']:4d} "
          f"err {A}={r['err_a']:6.1f} {B}={r['err_b']:6.1f} chromium={r['err_chromium']:6.1f}")
