# A fill's fringe draws a spike where its curve turns back on itself

femtovg master 06243b80, WGPU, through the demo-assets harness (`_logos_full`, built with `harness/build.sh`: all
cfgs). When a fill's flattened outline turns back on itself at a point that is not a corner (a hairpin inside one
cubic, or a cusp), `expand_fill` offsets that point along its full miter vector, 1/|dm| long, because
`calculate_joins` bevels only corners past the miter limit (for the `LineJoin::Miter` that fills pass). The fringe
strip then reaches several pixels past the turn and draws a thin spike; on the ear drawn alone the same point's fan
and inner fringe vertices also leave a detached dash beyond the ear's far side. BuseyBench's glm-5v-turbo shows the
spike at the top of each ear. The sheet is `../../issue-fill-reversal-spike.png`.

## Files

| file | what |
|---|---|
| `ear.svg` | glm-5v-turbo's left ear (line 123) alone, black on white: the last cubic runs left past the path's start point (252, 465) to u 249.1 and turns back to it, a hook 0.6 units thick and 3 units long |
| `ear-no-reversal.svg` | the same ear with the last cubic ending `C 264,466 258,465 252,465`: no turn back |
| `cusp.svg` | one cubic with a cusp at its middle (512, 415), closed by a line |
| `ear-stroke.svg`, `cusp-stroke.svg` | the same outlines stroked, `stroke-width="4"` |
| `fill-extrusion-bound.patch` | the prototype on 06243b80: in `expand_fill`, the offset of a point without `BEVEL` is bounded to the miter limit (2.4 for fills), plus a unit test that fails on master (a fringe vertex 12.9 px off the outline) and passes with it |
| `exploratory-switch.patch` | the build the variants came from: `FV_SPIKE=0` master, `1` the any-of bevel test in `expand_fill` (as nanovg and `expand_stroke` have it), `2` the prototype, `3` every point's offset bounded, beveled corners too; and a test that prints the ear's points |
| `render.py` | renders SVGs in the corpus framings with `master`, `after` (the prototype), `anyof`, `bound`, `boundall`, and `masks` / `after_masks` (every fill through an exact-area coverage mask) |
| `strokes.py` | the stroked outlines on master: pixels with ink where Chromium has none, and their extent |
| `measure.py` | pixels more than 20/255 off the browsers and the area reference, and ink in a window on each turn, for the reductions and the portrait |
| `corpus_ab.py` | renders every frame of three runs with a variant, hashes it as `accuracy.py` does and, for each frame that moved, counts pixels off each reference for master and the variant |
| `recount.py`, `ab_summary.py` | recount the moved frames with references made afterwards; toward / away / same per variant |
| `make_sheet.py` | the five-column sheet |
| `numbers_measure.json`, `numbers_corpus_ab.json`, `moved_frames.jsonl` | the numbers below; every moved frame with its counts |

## Reproduce

```sh
cd harness/fill-reversal-spike
F=~/src/femtovg-wt/spike                         # a femtovg checkout at 06243b80
RUN=~/src/femtovg-wt/runs/issues/fill-reversal-spike; export CORPUS_RUN_OUT=$RUN
# builds: master (byte-identical to a fresh build of 06243b80 with this harness), the prototype, the switch build
../build.sh mst4:$F
git -C $F apply $PWD/fill-extrusion-bound.patch && ../build.sh spike:$F && git -C $F checkout src
git -C $F apply $PWD/exploratory-switch.patch && ../build.sh spx:$F && git -C $F checkout src
# references for the reductions (group frs, keys frs__<name>)
python3 -c "import json,os,sys; d=os.getcwd(); json.dump([{'path': f'{d}/{n}.svg', 'key': f'frs__{n}',
  'group': 'frs-stroke' if 'stroke' in n else 'frs'} for n in ('ear', 'ear-no-reversal', 'cusp', 'ear-stroke',
  'cusp-stroke')], open(sys.argv[1] + '/files.json', 'w'))" $RUN
(cd ../corpus_run && python3 refs.py chromium framings=z1,z2,hd group=frs && python3 refs.py firefox framings=z1,z2,hd group=frs \
  && python3 refs_webkit.py framings=z1,z2,hd group=frs && python3 refs_ideal.py framings=z1,z2,hd group=frs \
  && python3 refs.py chromium framings=z2,hd group=frs-stroke)
for v in master after anyof masks after_masks; do for f in z1 z2 hd; do
  python3 render.py $v $f $RUN/png/red ear.svg ear-no-reversal.svg cusp.svg; done; done
for v in master after anyof; do for f in z1 z2 hd; do
  python3 render.py $v $f $RUN/png/port ../../corpus/buseybench/glm-5v-turbo.svg; done; done
for f in z2 hd; do python3 render.py master $f $RUN/png/red ear-stroke.svg cusp-stroke.svg; done
python3 measure.py $RUN ~/src/femtovg-wt/runs/busey/refs
python3 strokes.py $RUN
python3 make_sheet.py $RUN ../../issue-fill-reversal-spike.png
# the corpus: BuseyBench (runs/busey), the corpus and WPT-derived reftest groups (runs/wasmx), wpt22 (runs/wpt22)
python3 corpus_ab.py $RUN/ab.jsonl spx0 anyof bound boundall after jobs=8
# references for moved frames whose run had none: files.json of those keys in $RUN/xrefs, then refs.py chromium,
# refs.py firefox, refs_webkit.py, refs_ideal.py there (framings z1,z2,hd)
python3 recount.py $RUN/ab.jsonl $RUN/ab_recount.jsonl $RUN/xrefs/refs
python3 ab_summary.py $RUN/ab_recount.jsonl anyof after boundall --list
```

Frames: z2 is 460 x 260 with the 1024-unit viewBox fitted to a 200 px box at 2x (x = 30 + 0.390625 u, y = -70 +
0.390625 v), z1 the box at 1x, hd 1920 x 1080 with a 1080 px box. References: Chromium 131, Firefox 159.0b3, WebKit
(macOS 27.2, `wk_shot`), and the area reference `id_` (Chromium at 8x, averaged). The harness runs with its defaults
(no `SINGLE_SHADOW_LAYER`).

## Numbers (2026-10-19)

**The turn, from the library.** `spike_probe_ear` in `exploratory-switch.patch` builds the ear with the z2 transform,
`PathCache::new(.., 0.125, 0.01)` and `expand_fill(1.0, Miter, 2.4, NonZero)`, and prints (`FV_SPIKE=0 cargo test
--release --lib spike_probe_ear -- --nocapture`; `FV_SPIKE=2` for the prototype). Point 31 of 33, at (127.348,
111.450), is flagged `LEFT | INNERBEVEL`, with no `CORNER` and so no `BEVEL`, and
|dmpos| = 14.54. It takes the plain strip pair, which for a concave contour (the ear is one: its x direction changes sign four times) runs from p - 0.5 dmpos to
p + 1.5 dmpos (`lw` = fringe_width + woff, cache.rs L989-L995; a convex contour stops at p + 0.5 dmpos). The outer
vertex p - 0.5 dmpos lands at (120.12, 110.69), 7.3 px past the turn along the ear's top edge. The inner vertex p +
1.5 dmpos lands at (149.04, 113.73), 12.9 px from any outline point, and the fan vertex at (134.58, 112.21). Both land
past the ear's far side (Chromium's ink on row 112 ends at x 132). On `ear.svg` they leave a detached dash on the
segment between them: 3 px at x 137-139, row 112 (48 38 29) at z2, 3 of master's 17, and 2 px at x 187-188, row 121
(27 22) at z1, 5-6 px right of the ear's edge. It is the dark bar at the right edge of the sheet's `ear.svg` before
panel; the prototype removes it, and the patch's unit test fails on master on exactly that inner vertex. It does not
show in the portrait, where no pixel on that side changes. The start point (128.438, 111.641) is the other end of the
hook: a corner, `CORNER | BEVEL | INNERBEVEL`, |dmpos| 6.96, so it takes `bevel_join`. With the prototype, point 31's
outer vertex lands at (126.15, 111.32), 1.2 px past the turn. The 400 x 400 repro in the issue is the z2 frame shifted
by whole pixels: the hook region is identical, and row 180 at x 93-98 (the spike) reads 58 14 30 74 118 162 on master
and white except 156 at x 98 with the prototype; row 182 at x 107-109 (the dash) reads 48 38 29 on master and white
with the prototype.

**Reductions** (`measure.py`): pixels more than 20/255 off all three browsers over the whole frame, and ink (black on
white, summed (255 - grey) / 255) in a window on the turn, 30 x 16 px at z2, 16 x 10 at z1:

| | master | prototype | any-of | area | Chromium / Firefox / WebKit |
|---|---:|---:|---:|---:|---:|
| `ear.svg` z2 | 17, 122.6 | 3, 114.0 | 7, 116.0 | 112.7 | 110.4 / 110.4 / 112.5 |
| `ear.svg` z1 | 11, 41.3 | 3, 38.3 | 6, 40.5 | 37.7 | 37.6 / 37.7 / 37.5 |
| `ear.svg` hd | 4, 172.3 | 4, 172.3 | 4, 172.1 | 169.7 | 167.8 / 169.5 / 170.1 |
| `ear-no-reversal.svg` z2 | 0, 112.9 | 0, 112.9 | 0, 112.9 | 113.3 | 111.0 / 111.0 / 113.1 |
| `cusp.svg` z2 | 12, 18.9 | 9, 16.1 | 14, 17.9 | 13.4 | 13.7 / 13.7 / 13.3 |
| `cusp.svg` z1 | 12, 7.0 | 11, 6.9 | 17, 9.4 | 5.9 | 6.1 / 6.1 / 5.9 |

At hd the ear's turn is spread over three points (50-52 of 54) with |dmpos| 1.11, 1.53 and 1.02, so nothing changes.
Drawn through exact-area masks (`render.py masks` and `after_masks`), both builds are at 0 off all three browsers on
`ear.svg` and `cusp.svg` at every framing. The mask path draws no `expand_fill` fringe, so the two builds render
byte-identical frames there: that shows the pixels the prototype leaves come from the fringe, not which fringe error
they are. Where they sit is the evidence for #418's thin-tip case: (128,110), (128,111) and (129,111) on the 0.6-unit
hook (0.23 px at z2), and x 229-230, rows 92-95, at and just below the cusp's point (y 92.1), where it is under a
pixel wide.

**The any-of test** clears the spike at z2 but not at z1. `ear.svg` z2 row 110, x 123-127: 58 14 30 74 118 on master,
white with any-of (and the dash goes too). z1 row 120, x 175-177: 211 114 86 on master, 166 94 104 with any-of.
`bevel_join` still emits a vertex at the miter for a left turn without `BEVEL` (cache.rs L1410-L1411), but that
reading does not predict these frames; the reason not to take the any-of test is the corpus, below.

**glm-5v-turbo**, pixels more than 20/255 off all three browsers, whole frame / the two ear windows: z2 110 / 6 on
master, 104 / 0 with the prototype, 107 / 1 with any-of. z1: 47 / 7, 40 / 0, 53 / 6. hd: 251 / 0 for all three.
Master's window counts are totals over both ears: 3 + 3 at z2, (123-125, 110) and (334-336, 111); 3 + 4 at z1. The
spike is light there (skin colour on the dark background); on `ear.svg` it is dark.

**Corpus** (`corpus_ab.py`, `ab_summary.py`). The frame set is 6,957 frames: the 36 BuseyBench portraits at z1, z2 and
hd; the 1,243 corpus and WPT-derived reftest files of the wasmx run at z1, z2 and hd; and the 780 wpt22 files at z1,
z2, z4 and hd. The switch build at `FV_SPIKE=0` reproduced the stored master hash of every frame, and master itself,
rendered again for each moved frame, reproduced its own. The prototype build and `FV_SPIKE=2` give identical hashes on
all 6,957. A frame comes closer to (or goes further from) a reference when it has fewer (more) pixels more than 20/255
off it:

| variant | frames moved | vs Chromium: toward / away / same | net px | vs the area reference: toward / away / same |
|---|---:|---|---:|---|
| prototype | 26 | 18 / 1 / 7 | -300 | 17 / 1 / 8 |
| any-of test in `expand_fill` | 1,027 | 223 / 513 / 291 | +9,830 | 167 / 480 / 273 |
| every point bounded, beveled corners too | 719 | 127 / 384 / 208 | +17,248 | 119 / 327 / 185 |

The prototype's frames: glm-5v-turbo z1 and z2; Ghostscript Tiger at z1, z2 and hd (z2 3,208 -> 3,195 off Chromium; at
hd 26 of the 41 changed pixels are at the tip of one fur shape, x 703-709, y 328-342); seven svgenius icons; ember;
firefox pocket-swoosh and fox-with-box-on-cloud (same counts). The one frame that moves away is ember at z2: 3 px
change by at most 2/255, and one of them crosses 20/255 (615 -> 616). The any-of test sends Ghostscript Tiger (z2
3,208 -> 3,271) and fox-with-box-on-cloud away at every framing. Among the frames it brings closer,
fill-path-subpixel-sliver-control goes from 663 to 540 at hd; the prototype does not move that file.

**Strokes** share `calculate_joins`. Stroking the same outlines (`ear-stroke.svg`, `cusp-stroke.svg`) on master gives
a spike where Chromium has none (`strokes.py`): 15 px of ink over x 115-126 at z2, reaching x 115, 12 px left of the
turn (x 127.35) and about 8-11 px past Chromium's stroke edge (x 123-126 on rows 110-111); and above the cusp over 6
px (z2, y 85-90) and 16 px (hd, y 419-434). The prototype does not touch strokes.
