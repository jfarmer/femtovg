#!/usr/bin/env python3
"""The changed resvg references at the suite's 300 px: Chrome Canary, Firefox and STP through an iframe of 300 x 300,
then old and new reference against each (share beyond 20/255 and beyond 8/255)."""
import os, shutil, subprocess, tempfile
import numpy as np
from PIL import Image
from render import CANARY, FIREFOX, STP, BIN
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 't15')
def page(svg, prof, w=300, h=300):
    p = f'{prof}/page.html'
    open(p, 'w').write(f'<html><body style="margin:0"><iframe src="file://{svg}" width="{w}" height="{h}" style="border:0;display:block" scrolling="no"></iframe></body></html>')
    return p
def shoot(r, svg, out, w, h):
    prof = tempfile.mkdtemp(prefix='t15'); p = page(svg, prof, w, h)
    try:
        if r == 'chrome':
            subprocess.run([CANARY, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1', '--no-first-run',
                            '--allow-file-access-from-files', f'--user-data-dir={prof}/d', '--window-size=800,700',
                            '--default-background-color=FFFFFFFF', f'--screenshot={out}', f'file://{p}'], capture_output=True, timeout=120)
        elif r == 'firefox':
            subprocess.run([FIREFOX, '--headless', '--no-remote', '--profile', prof, '--window-size=800,700', '--screenshot', out, f'file://{p}'],
                           capture_output=True, timeout=120)
        else:
            env = dict(os.environ, DYLD_FRAMEWORK_PATH=STP, __XPC_DYLD_FRAMEWORK_PATH=STP)
            subprocess.run([f'{BIN}/wk_shot', p, out, '800', '700'], capture_output=True, timeout=120, env=env)
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    Image.open(out).convert('RGB').crop((0, 0, w, h)).save(out)
def load(p):
    im = Image.open(p).convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im)
    return np.asarray(bg.convert('RGB'), np.int16)
for svg in sorted(f for f in os.listdir(D) if f.endswith('.svg')):
    n = svg[:-4]
    if n.startswith('extra_'):
        print(f'{n:52} render_node output (the node layer only): not comparable with a page')
        continue
    w, h = Image.open(f'{D}/{n}__old.png').size
    for r in ('chrome', 'firefox', 'stp'):
        out = f'{D}/{n}__{r}.png'
        if not os.path.exists(out): shoot(r, f'{D}/{svg}', out, w, h)
    old, new = load(f'{D}/{n}__old.png'), load(f'{D}/{n}__new.png')
    cells = []
    for r in ('chrome', 'firefox', 'stp'):
        b = load(f'{D}/{n}__{r}.png')
        f = lambda a, t: (np.abs(a - b).max(2) > t).mean() * 100
        cells.append(f'{r}: {f(old,20):5.2f} -> {f(new,20):5.2f} ({f(old,8):5.2f} -> {f(new,8):5.2f})')
    print(f'{n:52}', ' | '.join(cells))
