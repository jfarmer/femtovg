#!/usr/bin/env python3
"""Render SVGs with the harness in the corpus framings, for one build variant.

  render.py VARIANT FRAMING OUTDIR SVG...

VARIANT: master   femtovg master 06243b80 (_logos_full_mst4)
         after    the prototype in fill-extrusion-bound.patch on 06243b80 (_logos_full_spike)
         spx0     the exploratory build with its switch at 0, which must render as master
         anyof    06243b80 with expand_fill's bevel test made any-of, as nanovg's and expand_stroke's (FV_SPIKE=1 on the
                  exploratory build _logos_full_spx)
         bound    the prototype through the exploratory build (FV_SPIKE=2; renders as `after`)
         boundall every point's fill extrusion bounded to the miter limit, beveled corners included (FV_SPIKE=3)
         masks, after_masks  master and the prototype with every fill through an exact-area coverage mask (harness
                  FILL_MASKS=1000 FILL_MASKS_MAX=1e9, clip-mask budget lifted)
Frames land as OUTDIR/<variant>_<stem>_<framing>.png. The frame env is corpus_run/common.py's (FRAMINGS, SWEEP_ENV):
the harness defaults, no SINGLE_SHADOW_LAYER."""
import os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus_run'))
from common import FRAMINGS, SWEEP_ENV  # noqa: E402
from PIL import Image  # noqa: E402

BIN = os.path.expanduser('~/src/femtovg-wt/bin/_logos_full_mst4')
SPIKE = os.path.expanduser(os.environ.get('SPIKE_BIN', '~/src/femtovg-wt/bin-spike/_logos_full_spike'))
SPX = os.path.expanduser(os.environ.get('SPX_BIN', '~/src/femtovg-wt/bin-spike/_logos_full_spx'))
VARIANTS = {
    'master': (BIN, {}),
    'after': (SPIKE, {}),
    'spx0': (SPX, {'FV_SPIKE': '0'}),
    'anyof': (SPX, {'FV_SPIKE': '1'}),
    'bound': (SPX, {'FV_SPIKE': '2'}),
    'boundall': (SPX, {'FV_SPIKE': '3'}),
    # every fill drawn as its bounds under the path as a clip, which the library takes as an exact-area coverage mask
    'masks': (BIN, {'FILL_MASKS': '1000', 'FILL_MASKS_MAX': '1e9', 'CLIP_MASK_BUDGET_MB': '512'}),
    'after_masks': (SPIKE, {'FILL_MASKS': '1000', 'FILL_MASKS_MAX': '1e9', 'CLIP_MASK_BUDGET_MB': '512'}),
}


def render(variant, framing, out_dir, svg, keep=True):
    binary, extra = VARIANTS[variant]
    fr, z = FRAMINGS[framing]
    stem = os.path.splitext(os.path.basename(svg))[0]
    png = f'{out_dir}/{variant}_{stem}_{framing}.png'
    ppm = png[:-4] + f'.{os.getpid()}.ppm'
    env = {**os.environ, **fr, **SWEEP_ENV, **extra}
    r = subprocess.run([binary, f'{z:g}', ppm, svg], env=env, capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not os.path.exists(ppm):
        sys.exit(f'{svg}: rc {r.returncode}\n{r.stderr[-600:]}')
    Image.open(ppm).save(png)
    os.remove(ppm)
    return png


if __name__ == '__main__':
    variant, framing, out_dir = sys.argv[1:4]
    os.makedirs(out_dir, exist_ok=True)
    for svg in sys.argv[4:]:
        print(render(variant, framing, out_dir, svg))
