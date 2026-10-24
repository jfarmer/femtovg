#!/usr/bin/env python3
"""Renders every SVG in svg/ as a standalone document with each renderer, onto white, at its natural size:
out/<renderer>/<name>.png. Resumable (existing PNGs are kept).

  render.py [renderer ...] [only=SUBSTRING]
"""
import os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.expanduser('~/src/femtovg-wt/bin')
CANARY = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
FIREFOX = '/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox'
STP = '/Applications/Safari Technology Preview.app/Contents/Frameworks'
RENDERERS = ['r48', 'r49', 'rfx', 'chrome', 'firefox', 'webkit', 'stp']


def natural_size(svg):
    png = f'{HERE}/out/r49/{os.path.basename(svg)[:-4]}.png'
    if os.path.exists(png):
        return Image.open(png).size
    head = open(svg, errors='replace').read(4000)
    m = re.search(r'<svg[^>]*>', head, re.S)
    w = re.search(r'\bwidth="([\d.]+)', m.group(0)) if m else None
    h = re.search(r'\bheight="([\d.]+)', m.group(0)) if m else None
    return (int(float(w.group(1))) if w else 300, int(float(h.group(1))) if h else 150)


def on_white(png, size):
    im = Image.open(png).convert('RGBA')
    bg = Image.new('RGBA', im.size, 'white')
    bg.alpha_composite(im)
    out = Image.new('RGB', size, 'white')
    out.paste(bg.convert('RGB').crop((0, 0, min(size[0], im.size[0]), min(size[1], im.size[1]))), (0, 0))
    out.save(png)


def render(job):
    renderer, svg = job
    name = os.path.basename(svg)[:-4]
    out = f'{HERE}/out/{renderer}/{name}.png'
    if os.path.exists(out):
        return 'kept'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    url = f'file://{svg}'
    try:
        if renderer in ('r48', 'r49', 'rfx'):
            exe = {'r48': f'{BIN}/resvg-0.48.1', 'r49': f'{BIN}/resvg-0.49.0', 'rfx': os.environ.get('RFX', f'{BIN}/resvg-fix')}[renderer]
            subprocess.run([exe, '--resources-dir', os.path.dirname(svg), svg, out], capture_output=True, timeout=300)
            if not os.path.exists(out):
                return 'failed'
            on_white(out, Image.open(out).size)
            return 'made'
        w, h = natural_size(svg)
        if renderer == 'chrome':
            # New headless mode clamps a small window (200x200 gives a 500x113 viewport), so the document goes in an
            # iframe of its natural size - still a standalone SVG document - inside a window that is not clamped.
            prof = tempfile.mkdtemp(prefix='canary')
            page = f'{prof}/page.html'
            open(page, 'w').write(f'<html><body style="margin:0"><iframe src="{url}" width="{w}" height="{h}" '
                                  f'style="border:0;display:block" scrolling="no"></iframe></body></html>')
            try:
                subprocess.run([CANARY, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                                '--no-first-run', '--disable-extensions', '--allow-file-access-from-files',
                                f'--user-data-dir={prof}/data', f'--window-size={max(w, 800)},{h + 400}',
                                '--default-background-color=FFFFFFFF', f'--screenshot={out}', f'file://{page}'],
                               capture_output=True, timeout=180)
            finally:
                shutil.rmtree(prof, ignore_errors=True)
        elif renderer == 'firefox':
            prof = tempfile.mkdtemp(prefix='ffprof')
            try:
                subprocess.run([FIREFOX, '--headless', '--no-remote', '--profile', prof, f'--window-size={w},{h}',
                                '--screenshot', out, url], capture_output=True, timeout=180)
            finally:
                shutil.rmtree(prof, ignore_errors=True)
        elif renderer in ('webkit', 'stp'):
            env = dict(os.environ)
            if renderer == 'stp':
                env.update(DYLD_FRAMEWORK_PATH=STP, __XPC_DYLD_FRAMEWORK_PATH=STP)
            subprocess.run([f'{BIN}/wk_shot', svg, out, str(w), str(h)], capture_output=True, timeout=120, env=env)
    except subprocess.TimeoutExpired:
        return 'timeout'
    if not os.path.exists(out):
        return 'failed'
    on_white(out, (w, h))
    return 'made'


if __name__ == '__main__':
    names = [a for a in sys.argv[1:] if a in RENDERERS] or RENDERERS
    only = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('only=')), '')
    svgs = sorted(f'{HERE}/svg/{f}' for f in os.listdir(f'{HERE}/svg') if f.endswith('.svg') and only in f)
    # resvg first: its output size frames the browsers' windows.
    for group in ([n for n in names if n.startswith('r')], [n for n in names if not n.startswith('r')]):
        jobs = [(r, s) for r in group for s in svgs]
        counts = {}
        with ThreadPoolExecutor(4) as ex:
            for (r, s), res in zip(jobs, ex.map(render, jobs)):
                counts[(r, res)] = counts.get((r, res), 0) + 1
                if res not in ('made', 'kept'):
                    print(r, os.path.basename(s), res, flush=True)
        print(sorted(counts.items()), flush=True)
