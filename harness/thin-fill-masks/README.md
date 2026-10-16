# Thin fills through coverage masks

Evidence for femtovg's thin-fill masks (#327; branch `thin-fill-masks` on
`even-odd-mask-winding`, on master 9f5ad26).

The fringe that antialiases a fill's edges gives the fill about a pixel of
ink across however thin it is. A fill whose mean width - twice its area over
its perimeter, each contour's area added or, if it bounds a hole under the
fill's rule, taken off - is under a pixel, and whose bounds span at most
65,536 pixels, is rasterized on the CPU by the clip masks' exact-area coverage
into one 2048 x 2048 one-byte atlas and drawn as a quad that reads the mask as
a glyph's is read (`GlyphTexture::AlphaMask`): the paint, the scissor and the
clips apply as they do to text, and no shader changes.

- `scenes.json`: seven Canvas 2D scenes on a 120 x 96 canvas - slivers 0.12 to
  0.8 px wide, rings 0.5 px wide (non-zero, and even-odd with both circles
  wound alike), crossing 0.3 px hairlines, a crescent, slivers under a triangle
  clip, and an outline 0.4 px wide around a filled body. `fillpath` takes an
  optional fill rule, `clippath` contours and a rule.
- `scenes_area.py SCENES OUT`: the 8x area reference (Chromium 131 at 8x,
  averaged over each 8 x 8 block). `../hard-mask-scenes/scenes_chromium.py`
  draws Chromium at 1x, `../hard-mask-scenes/wgpu_scenes.rs` WGPU and
  `../clip-bench/gl_scenes.rs` OpenGL; `../hard-mask-scenes/strip.py` with
  `REF_NAME='8x area'` makes the strips.
- `scenes-vs-area.png`, `scenes-vs-chromium.png`: master against the branch,
  at 3x. OpenGL and WGPU are pixel-identical on every scene, before and after.
- `corpus-1x.png`, `corpus-small.png`: 40 x 30 crops of corpus frames at 8x,
  where the masks bring the most pixels within 20 levels of the area reference
  (`corpus-strip-rows.txt` lists them), the pixels the masks moved outlined in
  magenta.

## Scenes

Ink (summed darkness) against the exact area of each scene's shapes, and
pixels more than 20 levels off the 8x area reference:

| scene | exact | master | branch | Chromium 1x | off area: master / branch / Chromium |
|---|---|---|---|---|---|
| slivers 0.12-0.8 px | 127.6 | 237.4 | 127.1 | 116.0 | 244 / 0 / 380 |
| ring 0.5 px, non-zero | 103.9 | 318.2 | 104.1 | 101.7 | 584 / 0 / 23 |
| ring 0.5 px, even-odd wound alike | 103.9 | 318.2 | 104.1 | 101.7 | 584 / 0 / 23 |
| hairlines 0.3 px, crossing | 634.3 | 1841.4 | 625.7 | 849.1 | 2310 / 0 / 1232 |
| crescent 0.6 px | 78.7 | 192.9 | 78.7 | 79.3 | 339 / 0 / 16 |
| slivers under a triangle clip | - | 68.3 | 28.4 | 10.4 | 103 / 15 / 128 |
| outline 0.4 px around a body | 730.2 | 973.2 | 723.1 | 734.9 | 544 / 0 / 0 |

The hairlines' exact ink takes off the 154 crossings' overlap; the branch is a
level light along each hairline because the mask's outline is kept to 1/256 px,
which rounds 8.35-8.65 inward to 0.297 px. The 15 pixels left in the clipped
row are where a sliver runs along the clip's edge inside a pixel: the clip's
coverage multiplies the sliver's, as it does every draw's (master and Chromium
at 1x leak there too), where the area reference intersects the two shapes.
Chromium at 1x drops the 0.12 and 0.25 px slivers and draws its horizontal
hairlines darker than its vertical ones.

## Corpus (2026-10-15, harness of this checkout, one binary with the masks on
and off: `tfme` / `tfme_off`)

- 1,094 of 11,403 frames change (z01 364, z025 254, z05 183, z1 110, zt2 69,
  z2 68, z4 22, hd 17, zt4 7). `tfmp` (the perimeter from the points' edge
  lengths) renders all 11,403 identically to `tfme`, and the final `tfmq` (a
  frame's masks uploaded as the rectangle they span) to `tfmp`.
- The 397 changed frames with an area reference: pixels beyond 20/255 of the
  area 139,475 -> 83,122 (WebKit 83,048, GPU Chromium 104,960, software
  Chromium 95,048, Firefox 62,194 on the same frames); 359 frames nearer, 15
  further. At 1x and up: 123 frames, 86,216 -> 61,964 (-28 %), 101 nearer, 3
  further; below 1x: 274 frames, 53,259 -> 21,158 (-60 %), 258 nearer, 12
  further.
- The further frames: where an exact thin fill meets a draw beside or over it,
  each draw's coverage composites on its own (conflation) - fox-with-box z05
  697 -> 899, against software Chromium 908 and Firefox 916; most others end at
  the browsers' counts. Two frames of one icon (page_84 icon_33, z1 +6 and hd
  +4 px): its light sliver (path 1, 3.7 px of ink by its fringe, 0.1 by its
  mask) lies over the thin tip of a thick path (path 0) whose fringe over-inks
  it; the over-inked sliver had half hidden that. A gate on a whole path's
  mean width does not see a thin part of a thick path.
- An earlier build (`tfmr`) summed the contours' signed areas, so a path of
  solid shapes wound against each other cancelled toward no width at any zoom
  and went through a mask: 152 frames, which now render as master does. The
  masks were nearer the area there too (the fringe is inexact at the corners of
  features 1 to 2 px across), which is a question of accuracy against cost for
  later, not of over-inking.

## Cost

One binary with the masks on and off (`tfmq` / `tfmq_off`, the final branch),
the 365 files whose frames change, at 1x and 1080p, 20 frames, 3 alternating
repeats (`../corpus_run/pass_time.py`):

- still: -1.1 % in sum, median frame +0.1 %; encoding -1.9 % (median +0.2 %).
- every frame moved by 0.37 px (`FRAME_DRIFT`), each mask made again each
  frame, the worst case: -0.2 % in sum, median frame +0.1 %; encoding +0.8 %
  (median +0.4 %).
- 150 files whose frames do not change (`tfmp`): +0.1 % in sum, median frame
  0.0 %.
- Card pages (`../corpus_run/instr.py tfmp_off tfmp`, instructions a frame at
  1080p): `cards_none_200` +0.2 %, `cards_rounded_200` +0.2 %,
  `cards_circle_200` 0.0 %, `tabs_300` +0.1 %, within the runs' spread. The gate
  took a square root an edge for the perimeter at first (+0.2 to +1.2 %); the
  points' edge lengths, worked out when the path is flattened, cost nothing.

`pass_time.py` divides the elapsed time by the frame count, the first frame's
setup (the atlas, the mask quad's pipeline) included, so its slowest frames
were timed again at 200 frames, 5 alternating repeats, in motion: diners at
1080p +276 us a frame (+32 %), the tiger at 1x +238 us (+12 %), page_84 icon_33
at 1080p +42 us (+7.6 %; +206 us while a frame uploaded the atlas's whole rows
its masks spanned, two megabytes for one tall sliver), puzzle-fox at 1080p -14
us. Diners makes 13 masks a frame there (75,000 px, 1,807 points): the clip
masks' rasterizer spends about 8 ns an edge cell on it, mostly sorting and
gathering the cells by row (Time Profiler: `MaskKey::rasterize` 34 % of the
run, the upload 2 %).

## In motion: the rasterizer and the atlas (2026-10-16)

A scene whose thin fills move makes their masks again each frame. Measured on
the efficiency cores of the M4 Max (`taskpolicy -c background`) and of the A15
Apple TV ("team h"), with the tools in `../pmc`:

- The rasterizer, which clip masks share, resolves each row from the edges
  crossing it, a bit for each cell touched, where it collected every cell an
  edge touched and sorted them by row and by cell (b2c4f40). Over the masks of
  moving corpus frames (757 heavy and 2,540 varied, captured from the harness)
  and 480 clip masks, exact counts a pass on the M4's efficiency cores: cycles
  -54 % and -56 %, clip masks -32 %; instructions -49 %, -50 %, -25 %; sampled,
  L1D load misses about -80 % and branch mispredicts -63 % on the moving masks,
  clip masks -28 % and -37 %. 7 of 51.7 million mask bytes differ, by one
  level (the cells' sums are added in another order); 10 of 11,403 corpus
  frames move, by one level in 100 pixels.
- Mask keys and requests are hashed a word at a time (4957eea): SipHash had
  been 1.6 % of a moving frame's cycles, and the frame's instructions drop
  about 1 % (diners at 1080p in motion, exact counts). A commit that added a
  one-cell piece's two cells at once (9d86ad3) is reverted (53cdc19): its
  -7 to -8 % was the benchmark's, whose old side allocated a contour for every
  mask; with the library's path on both sides it moved cycles by -3 to +1 %.
- The atlas starts at 512 pixels a side and grows in the frame a mask finds no
  room (df28a4c): every corpus frame renders as before; on the M4 the masks of
  diners, the tiger or puzzle-fox at 1080p add half a MiB of peak footprint
  where the fixed 2048 atlas added 11, and a frame that needs the whole atlas
  (page_84 icon_33 at 1080p, one tall sliver) still adds 11. The atlas does not
  shrink.
- On the TV, the render thread's efficiency-core cycles a moving frame summed
  over the 16 frames of the `thin` and `thinhd` phases (round 5, 4957eea):
  masks off 62.7 M, the first branch head 67.4 M (+7.5 %), the
  branch 66.1 M (+5.4 %); diners at 1080p +64 % -> +35 %. Inside the mask path
  (`fill_through_mask`) -39 % cycles and -47 % mispredicts (round 4, with the
  rasterizer and the atlas: -36 % L1D load misses). Peak footprint at 460 x 260: +8 / +4 MiB (graphics) with the fixed
  atlas, +0.2 / +0.1 with the growing one. GPU (Metal GPU Counters, masks off
  / old / new): GPU time 52.7 / 52.5 / 52.4 ms, read 37.3 / 37.6 / 36.8 MB,
  write 34.7 / 35.7 / 34.5 MB, partial renders 0 in every frame.
- What the masks still cost in motion on the TV is their rasterizing and the
  upload, about 40 % of it: wgpu's `write_texture` makes a staging buffer each
  call (the `wgpu-frame-setup` branch's staging belt is the fix for every image
  upload).
