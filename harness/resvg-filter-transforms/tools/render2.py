#!/usr/bin/env python3
"""Multi-scale renders: every SVG in svg/ at device scale S, out_<S>/<renderer>/<name>.png, onto white.
Browsers load the document in an iframe of its natural CSS size (a standalone SVG document) at a device pixel
ratio of S; resvg renders with -z S. Resumable.

  render2.py SCALE [renderer ...] [only=SUBSTRING]
"""
import os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from render import CANARY, FIREFOX, STP, BIN, natural_size

HERE = os.path.dirname(os.path.abspath(__file__))
RESVG = {'r48': 'resvg-0.48.1', 'r49': 'resvg-0.49.0', 'rT': 'resvg-fix', 'rE': 'resvg-E', 'rB': 'resvg-B', 'rB2': 'resvg-B2'}
BROWSERS = ['chrome', 'firefox', 'webkit', 'stp']


def finish(png, size):
    im = Image.open(png).convert('RGBA')
    bg = Image.new('RGBA', im.size, 'white')
    bg.alpha_composite(im)
    out = Image.new('RGB', size, 'white')
    out.paste(bg.convert('RGB').crop((0, 0, min(size[0], im.size[0]), min(size[1], im.size[1]))), (0, 0))
    out.save(png)


def render(job):
    scale, renderer, svg = job
    name = os.path.basename(svg)[:-4]
    out = f'{HERE}/out_{scale}/{renderer}/{name}.png'
    if os.path.exists(out):
        return 'kept'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    w, h = natural_size(svg)
    size = (round(w * float(scale)), round(h * float(scale)))
    if renderer in RESVG:
        subprocess.run([f'{BIN}/{RESVG[renderer]}', '-z', scale, '--resources-dir', os.path.dirname(svg), svg, out],
                       capture_output=True, timeout=300)
        if not os.path.exists(out):
            return 'failed'
        finish(out, Image.open(out).size)
        return 'made'
    prof = tempfile.mkdtemp(prefix='r2')
    page = f'{prof}/page.html'
    # Firefox's --screenshot captures at one pixel per CSS pixel whatever the device pixel ratio, so it gets
    # CSS zoom on the iframe instead (ZOOM=1 does the same for every browser, to check the two agree).
    zoom = renderer == 'firefox' or os.environ.get('ZOOM') == '1'
    style = f'zoom:{scale};' if zoom else ''
    open(page, 'w').write(f'<html><body style="margin:0;background:#fff"><iframe src="file://{svg}" width="{w}" height="{h}" '
                          f'style="border:0;display:block;{style}" scrolling="no"></iframe></body></html>')
    dsf = '1' if zoom else scale
    try:
        if renderer == 'chrome':
            subprocess.run([CANARY, '--headless', '--disable-gpu', '--hide-scrollbars', f'--force-device-scale-factor={dsf}',
                            '--no-first-run', '--disable-extensions', '--allow-file-access-from-files',
                            f'--user-data-dir={prof}/data', f'--window-size={max(round(w * float(scale)), 800)},{round(h * float(scale)) + 400}',
                            '--default-background-color=FFFFFFFF', f'--screenshot={out}', f'file://{page}'],
                           capture_output=True, timeout=180)
        elif renderer == 'firefox':
            subprocess.run([FIREFOX, '--headless', '--no-remote', '--profile', prof,
                            f'--window-size={max(round(w * float(scale)), 800)},{round(h * float(scale)) + 400}', '--screenshot', out, f'file://{page}'],
                           capture_output=True, timeout=180)
        else:
            env = dict(os.environ, WK_SCALE=dsf)
            if renderer == 'stp':
                env.update(DYLD_FRAMEWORK_PATH=STP, __XPC_DYLD_FRAMEWORK_PATH=STP)
            subprocess.run([f'{BIN}/wk_shot_s', page, out, str(max(round(w * float(scale)), 800)), str(round(h * float(scale)) + 400)], capture_output=True,
                           timeout=120, env=env)
    except subprocess.TimeoutExpired:
        return 'timeout'
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    if not os.path.exists(out):
        return 'failed'
    finish(out, size)
    return 'made'


if __name__ == '__main__':
    scale = sys.argv[1]
    names = [a for a in sys.argv[2:] if a in RESVG or a in BROWSERS] or list(RESVG) + BROWSERS
    only = next((a.split('=', 1)[1] for a in sys.argv[2:] if a.startswith('only=')), '')
    svgs = sorted(f'{HERE}/svg/{f}' for f in os.listdir(f'{HERE}/svg') if f.endswith('.svg') and only in f and not f.startswith('i949'))
    jobs = [(scale, r, s) for r in names for s in svgs]
    counts = {}
    with ThreadPoolExecutor(4) as ex:
        for (_, r, s), res in zip(jobs, ex.map(render, jobs)):
            counts[(r, res)] = counts.get((r, res), 0) + 1
            if res not in ('made', 'kept'):
                print(r, os.path.basename(s), res, flush=True)
    print(scale, sorted(counts.items()), flush=True)
