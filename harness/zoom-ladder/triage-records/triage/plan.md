# Zoom-ladder issue plan

**Scope.** The input stopped partway through the blur skeptic's verdict. It contained 8 of the 13 clusters in `triage/clusters_compact.json`, which is 143 of the 157 failing files. The blur skeptic's reasoning opens with "the central claim holds", but its corrections were not in the input. No skeptic refuted any of the 8 clusters.

Five clusters (14 files, 39 pairs) are not planned here because their investigations and verdicts were not in the input; see the last section.

I added two checks of my own. Scripts and results are in `~/src/femtovg-wt/runs/zoom/triage/plan/`:
- **Sweep A.** The corner-area clip build (`clip-edges-v/bin/_logos_full_area_v`) over every failing pair of the other 12 clusters.
- **Sweep B.** The stroke-fringe proof build (`mask-thin-stroke-3x/bin/_logos_cull` against `_logos_cull_aa1`) over every failing pair of all 13 clusters.

Both change where some pairs belong (issues 2 and 4).

None of the eight clusters' causes has an open issue. The plan is five new femtovg issues, one draft issue that needs your decision, and one optional comment on #13.

---

## Femtovg issues to file

### 1. NEW: "A stroke whose centreline lies off the canvas is culled even when its width, miter or cap reaches onto it"

This merges the miter-limit cluster with the zoom-3 part of mask-thin-stroke-3x. Neither has anything to do with the miter limit or masks.

**Covers 6 files, 10 pairs.**
- `wpt22…wpt-2d-line-miter-acute` at zoom 1.5 / 1.75 / 2 / 3 / 4: 39,000 / 45,500 / 52,000 / 59,800 / 59,800 px, all going to 0 px at all 11 zooms.
- The 5 `mask-on-thin-stroked-path-userspaceonuse` files (`framed`, `framed -ref`, `refs -expected`, `refs -ref`, `tests`) at zoom 3: 7,500 px each, going to 0.

**Mechanism** (master 06243b80, lines checked):
- `src/lib.rs:1607-1614` returns early when `path_cache.bounds` is off the canvas.
- Those bounds are the flattened centreline only (`src/path/cache.rs:349-363`).
- The test runs before the line width is known (`:1621`) and before `stroke.reach` (`:1640`, `src/paint.rs:457`).
- The shadow path at `:1584-1589` already widens the bounds by half the width. The cull does not.
- The cull came in with 227cb6c1 "Path culling" (2020), which added the same early-out to `contains_point` (`:1260`) and `fill_path` (`:1333`). Only the stroke one is wrong.
- nanovg's `nvgStroke` has no cull. Skia's `onDrawPath` quick-rejects on `computeFastBounds`, which uses `GetInflationRadius` (the same formula as `reach`), with a 1 px AA outset on the clip side.
- All three browsers agree pixel for pixel.

**Repro**
- SVG `triage/miter-limit/repro.svg`: `<rect 100x50 red/>` plus `<path d="M -50 120 H 150" stroke="#0f0" stroke-width="240"/>`. Master draws it all red; the browsers and the fix draw it all green.
- API: `move_to(0,120)`, `line_to(100,120)`, `line_width 60` on a 100x100 canvas. Master issues no Stroke command.
- Unit test: `a_stroke_whose_width_reaches_the_canvas_from_a_centreline_off_it_is_drawn` in `miter-limit/stroke-cull-reach.diff`. It fails on master with (0,0,0) against the expected (1,1,0).

**Fix sketch**
- Move the line-width computation (with the fringe clamp) above the early-out.
- Cull on the outer AA edge: `r = stroke.reach(line_width + fringe)`.
- The skeptic's correction: this is not "the same bounds as `draw_clip`", which uses `reach(line_width)` with no fringe.
- Three variants (`reach(max(w,f))+f`, `reach(w)+f/2`, and removing the cull entirely) give identical results.
- 282 lib tests pass.

**Evidence**
- The 557-render scan moves exactly these 10 frames.
- The skeptic removed the cull entirely and ran all 1,026 ladder files at zooms 0.5, 1, 1.5, 2, 3 and 4 (plus 1.75 on the miter file). Only these pairs move.

**Strip:** `miter-limit/strip5_sheet.png` plus `.gif`/`.webp`, in the house five columns (before, after, Chromium, before vs Chromium, after vs Chromium). The 1.25 to 1.5 pair is the clearest panel. For the mask files, `strip5_mask_sheet.png`; its 26 and 38 px at 1.25 and 1.75 are issue 2, so caption that red.

**Skeptics:** both confirmed it, each with their own patch. Corrections taken: origin commit 227cb6c1 (not 66a86c8a), the fringe wording, Skia's 1 px outset, and line 1584.

**Unresolved**
- The ablation was not run on always-passing files at 0.25 / 0.33 / 0.75 / 1.25 / 1.75.
- No timing A/B. The cost is one multiply-add per stroke, but the per-draw-work rule says to check the card pages.
- The GL backend was not run (the code is shared).
- From code only, not rendered: the stroke shadow store is bounded by half the width at `:1584`, not by reach, and `render_shadow` goes back through `stroke_path_internal`.

### 2. NEW: "Where the contours of one stroke meet, their fringes blend twice: coincident butt ends over-ink, abutting ones leave a seam"

**Covers 5 files, 10 pairs:** the same 5 mask files at 1.25 (26 px) and 1.75 (38 px). It also shows below threshold at 0.25 / 0.33 / 0.75 (6, 10 and 18 px).

**Mechanism**
- The stencil-stroke base pass discards fringe fragments below `strokeThr`, which is set at `lib.rs:1686` and tested at `shader.wgsl:157` and `main-fs.glsl:406`.
- The AA pass tests stencil Equal 0 with Keep (`wgpu.rs:1936-1958`, `opengl.rs:695-704`). So every contour's fringe lands on the same pixel and they compound as 1-(1-a)(1-b): 75 % where the browsers give the union's 50 %.
- Abutting contours leave a 75 % seam where the browsers draw 100 %.
- This is inherited from nanovg's stencil strokes (`glnvg__stroke`, EQUAL 0 / GL_KEEP).
- The browsers take the union within one draw. Across separate `<path>` elements Chromium also gives 75 %, and femtovg matches it there.

**Repro** (`mask-thin-stroke-3x/repro/`)
- `<path d="M 50.5 45 L 150.5 45 M 50.5 55 L 150.5 55" stroke="green" stroke-width="20"/>` at zoom 1.
- The abutting case: `M 50 50 L 100.5 50 M 100.5 50 L 150 50`.

**Fix sketch (not implemented, not costed)**
- No blend rule gives the union. First-wins stencil fixes coincident ends but halves abutting ones. MAX has the same split. Adding cell areas over-inks.
- Real fix: draw strokes that have two or more contours with intersecting reach bounds through the #408 coverage mask, resolving nonzero per sub-scanline as `SkScan_AntiPath` does.
- That needs issue 5's sub-scanline fold first: `coverage.rs` today sums areas before it folds.
- Low priority (26-38 px at 64/255). Cross-link #417 (its dash pieces abut) and #13.

**Proof:** `proof-aa-pass-marks-stencil.patch` takes 26 to 2, 38 to 2 and 18 to 2. The leftover is row 73 at 0.378 coverage against a predicted 0.375.

**Sweep B** (mine, the proof build against the cull build over all clusters):
- It also moves `corpus__firefox__lists-empty-state-light`: 37→33, 32→15, 26→11, 45→27, 60→35 at 0.25 / 0.75 / 1.25 / 1.5 / 1.75.
- It makes `dasharray-n-0-solid` at 0.33 worse, 60→76, which is the abutting case.
- The firefox-artwork investigator tried the same IncrementClamp (`firefox-artwork/experiment_aa_once.patch`).
- Both clusters are outside this input. Merge them here only if their own verdicts agree.

**Strip:** `mask-thin-stroke-3x/sheet_before_after.png`, five columns. Its "after" is the proof build, not a fix: say so. Caption the abutting row, where the seam stays. The ladder strip is `strip_fringe_z1-175.{gif,webp}`.

**Skeptic:** confirmed both repros. Corrections taken: the nanovg origin, cite #13 and #327, the extra small zooms, and the line references.

### 3. NEW: "Hard gradient stops are blurred over 1/256 of the gradient and moved onto a 1/256 grid"

**Covers 4 files, 22 of 25 pairs.**
- `stops-with-equal-offset-1`, `-2` and `stop-with-smaller-offset-monotonic` at 1.25 / 1.5 / 1.75 / 2 / 3 / 4: 208 / 240 / 260 / 260 / 260 / 780 px, going to 8 / 0 / 0 / 0 / 0 / 0.
- `stop-zero-offset-in-the-middle` at 1.75 / 2 / 3 / 4: 520 px each, going to 0.
- Not covered: the three 0.7 files at 0.33 (see "not femtovg's").

**Mechanism**
- Every MultiStop gradient is baked into a 256x1 Rgba8 texture (`gradient_store.rs:48`) with no NEAREST flag, so it is sampled linearly (`wgpu.rs:3193-3196`, `gl_texture.rs:112-141`).
- It is read at `shader.wgsl:465`, at `:206` (conic) and `:363` (two-point radial), and at `main-fs.glsl:177/199/284`.
- MultiStop means everything except exactly two stops at ≤0 and ≥1 (`paint.rs:237-257`).
- Two effects:
  - (a) a one-texel ramp, L/256 px wide;
  - (b) the stop is quantised to the 1/256 grid, and the `as usize` truncation at `:81-82` can add up to another half texel.
- Skia raster evaluates per pixel (`SkRasterPipeline_opts.h:3466-3476`) and skips empty intervals (`SkGradientBaseShader.cpp:440`).
- Ganesh is analytic up to 128 stops. Its own 256-texel fallback "always blurs hard-stops" (`GrGradientShader.cpp:892`).

**Repro:** `gradient-hard-stops/repro.svg`, a 640 px gradient (red, yellow at 0.7, green at 0.7). Master gives cols 446-448 = [229,240,0] [128,191,0] [26,141,0]. Chromium and the area give a single step at x = 448.

**Fix sketch**
- Evaluate stops per fragment: a threshold plus scale/bias table, skipping empty intervals, in straight colour space, with a bounded loop. Keep it inside the existing gradient shader variants.
- Storage: textureLoad from an Rgba32Float row (or a storage buffer) on wgpu; RGBA32F or packed channels on GL.
- A wider texture is a band-aid: in the 640 px repro at zoom 2, a centre-evaluated 1024-texel texture still fails 20 px. NEAREST alone still fails at zoom 4.
- This conflicts with PR #359 and touches #350's function.

**Evidence:** the 4096-texel probe over all 400 failing steps moves only this cluster, plus `wallpaper-landscape-planet` by at most 1 px.

**Strip:** `gradient-hard-stops/strips/equal-offset-1_5col.{gif,webp,_sheet.png}` and `zero-offset-middle_5col`. Captions: "after" is the 4096-texel probe, not the proposed fix; the red at zoom 1 and 1.25 is femtovg's own frame-corner pixels; the red at 0.33 is the frame stroke.

**Skeptic:** confirmed with an independent probe. Corrections taken:
- the band-aid evidence: N=1024 failed because of truncation, not ramp width;
- the quantisation wording;
- Firefox is within 1/255 of Chromium, not identical;
- MultiStop covers more than "3 or more stops";
- the model tolerance at zoom 3 is about 2.5/255;
- the Skia line ranges.

**Unresolved:** GL not run. Conic and two-point radial gradients with 3 or more stops not tested. The analytic fix is neither written nor timed; it needs a paired A/B on both backends.

### 4. NEW: "Round clip shapes take a distance ramp: up to 11/255 off each pixel's area on the diagonals"

**Covers 15 files, 78 pairs.** The fix clears 38 of them, measured with `clip-edges-v/ab.py` and Sweep A.

| file | before → after | zooms cleared |
|---|---|---|
| variation-12 | 6 → 3 | 0.33, 1.25, 3 |
| variation-16 | 7 → 4 | 0.33, 0.75, 4 |
| variation-20 | 5 → 2 | 0.33, 1.25, 2 |
| variation-24 | 6 → 4 | 3, 4 |
| variation-28 | 7 → 3 | 0.75, 1.25, 3, 4 |
| variation-32 | 7 → 4 | 0.33, 3, 4 |
| variation-36 | 6 → 4 | 0.33, 0.75 |
| variation-40 | 4 → 3 | 2 |
| variation-44 | 7 → 3 | 0.33, 1.25, 3, 4 |
| variation-48 | 8 → 3 | 0.33, 0.75, 1.25, 3, 4 |
| clip-path-rounded-rect | 4 → 2 | 1.5, 3 |
| offset-under-clip-path-ref | 4 → 3 | 1.75 |
| blend-clip-path-nested-overlay-ref | 1 → 0 | 0.75 |
| blend-clip-path-nested-overlay | 2 → 1 | 4 |
| **feblend-in-clipped-layer** (thin-frame cluster) | 4 → 1 | 0.75, 3, 4 |

The last row is new from Sweep A. Against WebKit, 43→12, 36→4 and 53→5. The thin-frame investigator had called these pairs "browser disagreement at the clip edge"; they are this mechanism. Its 0.33 pair (44 against WebKit) does not move.

**Mechanism**
- `clipMask` (`shader.wgsl:395-409`, the ramp at `:405`; `main-fs.glsl:118-130`, `:128`) takes coverage as clamp(0.5 − signed distance).
- That is exact only on axis-aligned edges. On a 45° edge it is up to 0.043 off, which is 11/255.
- The analytic fit itself is exact (`clip/shape.rs:135-150`): 16-arc input renders bit-identically.
- #380 already records 13/255. Parent #346 is closed.

**Repro:** `<clipPath><circle cx=110 cy=95 r=25/></clipPath>` over a green rect at zoom 3 or 4, compared with an exact disc. API: `clip_path(circle)` then `fill_rect`.

**Fix sketch**
- Port 48b9284 (origin/clip-corner-area). It does not apply cleanly: use `clip-edges-v/corner-area-on-06243b80.patch`. Its GLSL hunk is neither compiled nor run.
- It was parked on 2026-10-05 for cost: +5 % on wgpu and +15-18 % on Apple GL for fill-bound full-screen ellipse clips, and agreement with GPU Chromium fell from 37 to 22 reftests.
- Re-measure on 06243b80 and run `gl_clip_check` before proposing it.

**What stays after the fix (39 pairs plus feblend 0.33)**
- 35 pairs where the exact area itself fails against WebKit. That is WebKit's own error, on the same diagonals with the opposite sign.
- 4 pairs where two sub-threshold errors add up: variation-16, -32 and -36 at 1.25, and offset-under-clip-path-ref at 0.75.

**Strip:** GPU Chromium at 1x is 32-40/255 off these circles, so the issue's reference columns should be WebKit and the area; say why. The existing `clip-edges/strips/v28_vs_area.png` is not in the house format. **To make:** `sheet.py` on variation-28 at 1.5 / 3 / 4, `_logos_full_master_v` against `_logos_full_area_v`, with WebKit and area references.

**Skeptic:** confirmed. Corrections taken: the patch does not apply cleanly; 74→39, not 40; 4 sums, not 5; WebKit errs on the same diagonals (not elsewhere on the circle); rounded-rect reaches 4/255.

### 5. NEW: "A clip mask over-covers where a self-crossing contour puts windings 0, 1 and 2 in one pixel"

**Covers 1 file, 2 pairs:** `wpt22…resvg-clippath-multiple-children` at 1.25 (32 px) and 1.75 (26 px).
- Its 2 / 3 / 4x failures are WebKit's own error (42 / 122 / 182 px off the exact star).
- At 1.25 the 1 px frame's corner pixels also count: 32 = 8 vertex + 8 frame-corner + 16 other pixels. Removing either set leaves 24, a pass, so this fix alone passes it.

**Mechanism**
- `clip/coverage.rs:11-12` and `:191-205` sum signed areas per cell, then fold by the fill rule. Even-odd gives a1 + 2·min(a0, a2) where the area gives a1.
- That over-covers by 49-86/255 at zooms 1-4.
- #407 states the limitation but fixed only nested contours. #410 is the fill-side bug, a different mechanism.

**Repro:** the even-odd pentagram clip `M100 15l50 160-130-100h160l-130 100z` at zoom 1.25 or 1.75. API: `clip_path(star, FillRule::EvenOdd)`.

**Fix sketch:** in rows where two or more edges touch a cell, fold per sub-row (4-16 sub-rows) and average, or split edges at their crossings. Check nonzero overlaps (min(|sum|, 1)) too. Not implemented, cost unknown. Issue 2's fix depends on it.

**Proof:** the same region as a 10-gon plus a reversed pentagon under nonzero gives 32→24 and 26→20.

**Strip:** the existing `clip-edges/strips/star_crossing_vs_area.png` is not in the house format. **To make:** five columns with master on the original as "before", master on `exp/star_nocross.svg` as "after" (caption: equivalent geometry, not a fix), and WebKit as reference.

**Skeptic:** confirmed it pixel by pixel. Corrections taken: the fold formula, and the frame corners counting at 1.25.

### Draft 6, decision needed: "Strokes under a pixel wide on axis-aligned rectangles spread over two pixels, where Chromium and Firefox draw the exact area"

**Would cover 23 thin-frame files, 48 pairs at 0.25 / 0.33 / 0.75.** That is every file in the cluster except `empty` and `feblend-in-clipped-layer`. `subregion-1-ref`'s failing zooms (0.25 and 0.75) are frame-only.

**Mechanism (confirmed):** `lib.rs:1621-1635` widens a stroke thinner than the fringe to the fringe width and multiplies its alpha by w/f. With `stroke_mult` = 1 (`params.rs:128`) this draws a 2 px tent at peak w. Sampled at pixel centres, that is Skia's hairline profile.

**Disputed, and settled against the investigator by the skeptic's measurements**
- The browsers draw the exact area only for rectangle-shaped geometry: Chromium for `<rect>` (`DrawRect` → `AntiFrameRect`), Firefox for `<rect>` and H/V rectangle path data, WebKit only for single line segments.
- For general paths, curves and circles, all three draw the hairline profile, which master already matches.
- The investigator's general exact-area patch passes 22 of 25 files, but moves away from all three browsers on BuseyBench (for example opus-5-5: Chromium 931→1308, WebKit 941→1333) and on curve and circle probes.
- On the frame itself WebKit draws femtovg's profile. So under the rule this is a browser disagreement.

**Recommendation:** list it under "not femtovg's" for now. File the narrow rectangle-only issue only after two things:
- a rect-only prototype (closed axis-aligned four-segment subpaths, Firefox's rule);
- an A/B on general content (buseybench, nyt, svgenius, tiger).

Do not file the investigator's title "draw them at their own width, at the exact area": it claims more than the browsers support.

**Strip if filed:** `thin-frame-stroke-fractional/strips/sheet_thin_profile.png`, with "after" rebuilt from the rect-only variant.

### Optional comment on open #13 (low priority; it decides no pair on its own)

Fill fringes cover a square corner pixel by about min(cx, cy), not cx·cy. Measured examples:
- feOffset probe: 0.40 where exact is 0.16;
- offset-under-clip-path-ref at 0.33: 61/255;
- blur clip-containment: 2 px;
- the frame corners in the gradient files at 1.25: 8 px;
- layer-ctm at 0.33: 15 px;
- thin-frame residuals: 2-12 px.

It co-decides only multiple-children at 1.25, where issue 5 alone clears it. #337 already notes it with "no issue yet".

---

## Not femtovg's (no femtovg issue)

### Browser approximations or disagreement

**Blur (a), three-box against Gaussian:** 30 files (16 distinct SVGs; the wpt22 copies are byte-identical), 30 pairs.
- 29 pairs are blur-variation 4-4-* and 6-4-* and their refs, plus `2d.layer.anisotropic-blur.isotropic`, all at 0.5; the 30th is `probes/bigblur` at 3.
- femtovg is within 3/255 of the analytic Gaussian.
- Chromium and Firefox run Skia's legacy three-box (`SK_USE_LEGACY_BLUR_RASTER`). At device σ 2 the window rounds to an even 4, which is 6 % too wide, and the two axis errors add at rect corners to 9-11/255.
- Closed #325 already records this residual.
- The blur skeptic's corrections were not in the input.

**Blur (b), clip containment:** 2 files at 0.33.
- Chromium's rect clip-path is aliased and WebKit leaks on all four edges.
- femtovg's clip and blur each match their reference; the leak is conflation at a shared edge.
- femtovg's own part is 2 corner pixels (#13).

**layer-ctm-drop-shadow:** 1 file, 5 pairs (0.25 / 0.33 / 0.75 / 1.25 / 1.75).
- All three browsers rasterise the filter layer in user space and resample it under rotate(90) and the fractional origin. femtovg draws in device space and is exact.
- Against the WPT `-ref` match file femtovg is still 48-304 px off. Proven cause: the shadow's fractional offset is composited bilinearly (`shadow.rs:223`, no NEAREST), which is the same choice as Chromium (Skia kLinear).

**feOffset group A:** 52 files (26 SVGs × 2 corpora), 120 pairs.
- Each engine resamples a fractional device shift by its own rule: femtovg bilinear (deliberate since #374), Chromium nearest plus antialiased bounds, Firefox truncates, WebKit uses CoreGraphics interpolation.
- With integer shifts, every case comes within 0-5 px of the best browser.
- The skeptic's correction: femtovg does **not** fold consecutive offsets (`image.rs:841-873`).
- WebKit-only differences: linear-light blending in border-stroke-fill, and the half-covered region edge in group-opacity.
- Note for you: in `offset-with-parent-transform-scale` at 1.25, Chromium and WebKit agree with each other and are closer to exact than femtovg (188 against 279 px off the area).
- This bilinear-offset policy is one design choice shared with layer-ctm. If it is ever revisited, it is one item covering both.

**Gradient files at 0.33:** 3 pairs. They still fail after the texture fix (62 px against WebKit, 264 against Chromium and Firefox):
- WebKit puts the stop one pixel earlier than Chromium and Firefox;
- the frame's 0.33 px stroke (draft 6).

**clip-edges A residual:** the 35 pairs where the exact area itself fails against WebKit, plus the 4 sub-threshold sums (issue 4).

**clip-edges C at 2 / 3 / 4x:** 3 pairs, WebKit's own error.

**thin-frame:** the 23 frame files, 48 pairs, if draft 6 is not filed.

### Harness mapping (notes for demo-assets)

**`resvg-feblend/empty` at 0.33:** 1 pair. `_logos_full.rs:718` marks feBlend(SourceGraphic, SourceGraphic) complete with no pass. It should draw the group twice.

**feOffset group B:** 4 files, 10 pairs.
- `offset-triple-chain-rgb-shadow`: the harness maps feMerge only as [previous, SourceGraphic] (`:621`).
- `offset-sourcealpha-flood`: `shadow_chain` requires a blur (`:1114`).
- `LAYER_STATS` reports "filters skipped: 0" for both, which is wrong.
- Once mapped, triple-chain moves toward the browsers and away from exact.

### usvg geometry and reference tolerance

**clip-edges B:** 3 files, 16 pairs (`evenodd-clip-thin-ring`, and `clip-path-concentric-circles-evenodd` in both corpora).
- usvg draws a circle as four 90° cubics (0.1-unit tolerance, kurbo's minimum of 4), which bulges by 2.7e-4 r. The mask draws that geometry exactly.
- The skeptic's correction: 16-arc input clears only 6 of the 16 pairs, leaves 10, and creates 2 new ones (concentric at 4x, 0→164), because WebKit draws the same bulge.
- The bulge is the cause only at 1.5-2x. Elsewhere it is WebKit's own error.
- Separately, and unmeasured: femtovg's own `Path::ellipse` / `arc` use the same KAPPA90 cubics for API users.

### Triage tooling

Score these against an analytic or area reference rather than best-of-three:
- blur files (σ×8 ≤ 532 for the 8x area);
- filtered content under a rotated CTM or a fractional user origin (use the WPT `-ref` match file);
- feOffset edges at fractional device shifts.

## Unresolved (not ready to file)

- **`offset-circle-shape` at 3, 1 pair.** femtovg's fill edge on an r = 90 px circle is 43 px off exact (max 25/255) where WebKit is exact. The browsers disagree among themselves by more (Chromium against WebKit 50 px). Whether it is the fringe or the flattening chords has not been separated: run the file with a finer `tess_tol` before deciding on a comment on #13.
- **`feblend-in-clipped-layer` at 0.33, 1 pair.** 44 px against WebKit, on the clip edge. Issue 4's fix does not move the count.

## Clusters not in this input (14 files, 39 pairs)

| cluster | files | pairs |
|---|---|---|
| firefox-artwork | 2 | 11 |
| morphology | 4 | 12 |
| subpixel-sliver | 4 | 8 |
| dasharray | 2 | 6 |
| svgenius-033 | 2 | 2 |

From the sweeps:
- Issues 1, 3 and 4 do not explain any of them: the cull scan, the 400-step texture sweep (wallpaper moves by at most 1 px) and Sweep A.
- Sweep B moves `lists-empty-state-light` and `dasharray-n-0-solid`, so check them against issue 2 when their verdicts arrive.

## Posting notes

- Titles follow the maintainer's plain style.
- Every issue gets a five-column sheet with any remaining red captioned. Issues 4 and 5 still need theirs made.

## Totals for the 143 files covered

| outcome | files | notes |
|---|---|---|
| Femtovg issues 1-5 | 26 | some files appear in two issues |
| Draft 6, pending your decision | 23 | |
| Not femtovg's | 92 | |
| Unresolved | 2 pairs | `offset-circle-shape` at 3 (counted in the 143); `feblend-in-clipped-layer` at 0.33 (that file is already in issue 4) |