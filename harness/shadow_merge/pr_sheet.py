#!/usr/bin/env python3
"""A PR's evidence sheet from ab.py's frames and references (SHADOW_MERGE_OUT): one row per frame with Chromium,
Firefox, BEFORE and AFTER, each build against each browser, and each build outside the range the two browsers span.
A difference panel is white where the frame is within 8/255, orange from 9 to 20 and red beyond, as
corpus_run/sheet.py draws them; outside the browsers is white wherever a build lies between them.

  pr_sheet.py OUT.png BEFORE[=label] AFTER[=label] [--panels=refs,builds,chr,ff,outside] ROW...

ROW is NAME:FRAMING followed by options, each after a colon: box=X,Y,W,H (the window in frame pixels), or size=WxH
(default 230x130) for a window placed where AFTER comes back inside the browsers' range the most; zoom=N magnifies
N times. The caption has, for the whole frame, px > 8/255 and the mean max-channel delta against each browser and
the share more than 8/255 outside both. --panels picks the groups of panels, in that order: the references, the two
builds, the builds against Chromium, against Firefox, and outside both (default: all). Environment: SHADOW_MERGE_OUT as for ab.py, CHROMIUM_LABEL and
FIREFOX_LABEL for the reference panels' names."""
import glob, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DA = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(os.path.abspath(os.environ.get('SHADOW_MERGE_OUT', 'shadow-merge-run')), 'corpus')
LABELS = {'chr': os.environ.get('CHROMIUM_LABEL', 'Chromium'), 'ff': os.environ.get('FIREFOX_LABEL', 'Firefox')}


def font(size):
    for path in ('/System/Library/Fonts/Helvetica.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def key(name):
    hits = [p for p in glob.glob(f'{DA}/corpus/**/{name}.svg', recursive=True)]
    if len(hits) != 1:
        raise SystemExit(f'{name}: {len(hits)} corpus files by that name')
    return os.path.relpath(hits[0], DA)[:-4].replace('/', '__')


def load(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.int16)


def delta(a, b):
    return np.abs(a - b).max(axis=2)


def outside(a, refs):
    low, high = np.minimum.reduce(refs), np.maximum.reduce(refs)
    return np.maximum(np.maximum(low - a, a - high), 0).max(axis=2)


def heat(d, box, zoom):
    x, y, w, h = box
    d = d[y:y + h, x:x + w]
    im = np.full(d.shape + (3,), 255, np.uint8)
    im[d > 8] = [255, 160, 0]
    im[d > 20] = [255, 0, 0]
    return Image.fromarray(im).resize((w * zoom, h * zoom), Image.NEAREST)


def picture(a, box, zoom):
    x, y, w, h = box
    return Image.fromarray(a[y:y + h, x:x + w].astype(np.uint8)).resize((w * zoom, h * zoom), Image.NEAREST)


def best_window(gain, w, h):
    """The w x h window with the largest summed gain, by an integral image."""
    H, W = gain.shape
    w, h = min(w, W), min(h, H)
    s = np.pad(gain.astype(np.float64).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    sums = s[h:, w:] - s[:-h, w:] - s[h:, :-w] + s[:-h, :-w]
    y, x = np.unravel_index(np.argmax(sums), sums.shape)
    return int(x), int(y), w, h


def main():
    args = sys.argv[1:]
    groups = next((a.split('=', 1)[1].split(',') for a in args if a.startswith('--panels=')),
                  ['refs', 'builds', 'chr', 'ff', 'outside'])
    out, before, after, *specs = [a for a in args if not a.startswith('--')]
    (before, bl), (after, al) = ((s.split('=', 1) + [s])[:2] for s in (before, after))
    rows = []
    for spec in specs:
        name, framing, *options = spec.split(':')
        opt = dict(o.split('=', 1) for o in options)
        k = key(name)
        b, a = load(f'{OUT}/{before}/{k}_{framing}.ppm'), load(f'{OUT}/{after}/{k}_{framing}.ppm')
        refs = {r: load(f'{OUT}/refs/{r}_{k}_{framing}.png') for r in ('chr', 'ff')}
        ob, oa = outside(b, list(refs.values())), outside(a, list(refs.values()))
        zoom = int(opt.get('zoom', 1))
        if 'box' in opt:
            box = tuple(int(v) for v in opt['box'].split(','))
        else:
            w, h = (int(v) for v in opt.get('size', '230x130').split('x'))
            box = best_window(np.clip(ob, 0, 40) - np.clip(oa, 0, 40), w, h)
        group = {'refs': [(LABELS['chr'], picture(refs['chr'], box, zoom)), (LABELS['ff'], picture(refs['ff'], box, zoom))],
                 'builds': [(bl, picture(b, box, zoom)), (al, picture(a, box, zoom))],
                 'outside': [(f'{bl} outside both', heat(ob, box, zoom)), (f'{al} outside both', heat(oa, box, zoom))]}
        caption = f'{name} at {framing}:'
        for r, ref in refs.items():
            db, da = delta(b, ref), delta(a, ref)
            group[r] = [(f'{bl} vs {LABELS[r]}', heat(db, box, zoom)), (f'{al} vs {LABELS[r]}', heat(da, box, zoom))]
            caption += (f' vs {LABELS[r]} px>8 {100 * (db > 8).mean():.2f} -> {100 * (da > 8).mean():.2f} %,'
                        f' mean {db.mean():.3f} -> {da.mean():.3f};')
        panels = [p for g in groups for p in group[g]]
        caption += f' outside both by >8 {100 * (ob > 8).mean():.2f} -> {100 * (oa > 8).mean():.2f} %'
        rows.append((caption, panels))
        print(caption, 'window', box)
    gap, cap = 8, 36
    column = max(p.width for _, panels in rows for _, p in panels) + gap
    width = max(len(panels) for _, panels in rows) * column + gap
    height = sum(max(p.height for _, p in panels) + cap + gap for _, panels in rows) + gap
    sheet = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(sheet)
    y = gap
    for caption, panels in rows:
        draw.text((gap, y), caption, fill=(0, 0, 0), font=font(13))
        for i, (label, p) in enumerate(panels):
            x = gap + i * column
            draw.text((x, y + 19), label, fill=(90, 90, 90), font=font(11))
            sheet.paste(p, (x, y + cap))
            draw.rectangle([x - 1, y + cap - 1, x + p.width, y + cap + p.height], outline=(200, 200, 200))
        y += max(p.height for _, p in panels) + cap + gap
    sheet.save(out)
    print(out, sheet.size)


if __name__ == '__main__':
    main()
