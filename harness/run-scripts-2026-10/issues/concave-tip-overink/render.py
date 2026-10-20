#!/usr/bin/env python3
"""Render SVGs with the harness binary of femtovg master 06243b80 (_logos_full_mst4) in the corpus framings.

  render.py VARIANT FRAMING OUTDIR SVG...

VARIANT: master   the harness defaults (rule 4a shadow merge, #408 thin-fill masks on)
         off      master with NO_THIN_FILL_MASKS=1 (every fill through its fringe)
         masks    master with every fill drawn as its bounds under the path as a clip, which the library takes as an
                  exact-area coverage mask (harness FILL_MASKS=1000 FILL_MASKS_MAX=1e9, clip-mask budget lifted)
Frames land as OUTDIR/<variant>_<stem>_<framing>.png. The frame env is corpus_run/common.py's (FRAMINGS, SWEEP_ENV)."""
import os, subprocess, sys
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import FRAMINGS, SWEEP_ENV  # noqa: E402
from PIL import Image  # noqa: E402

BIN = os.path.expanduser('~/src/femtovg-wt/bin/_logos_full_mst4')
VARIANTS = {
    'master': {},
    'off': {'NO_THIN_FILL_MASKS': '1'},
    'masks': {'FILL_MASKS': '1000', 'FILL_MASKS_MAX': '1e9', 'CLIP_MASK_BUDGET_MB': '512'},
}


def render(variant, framing, out_dir, svg):
    fr, z = FRAMINGS[framing]
    stem = os.path.splitext(os.path.basename(svg))[0]
    png = f'{out_dir}/{variant}_{stem}_{framing}.png'
    ppm = png[:-4] + '.ppm'
    env = {**os.environ, **fr, **SWEEP_ENV, **VARIANTS[variant]}
    r = subprocess.run([BIN, f'{z:g}', ppm, svg], env=env, capture_output=True, text=True, timeout=600)
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
