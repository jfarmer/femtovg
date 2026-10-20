# A fill's fringe draws a spike where its curve turns back on itself

Where a fill's flattened outline turns back at a point inside a curve (a hairpin or a cusp), the antialiasing fringe runs several pixels past the turn as a thin spike. Each ear of BuseyBench's [glm-5v-turbo](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/glm-5v-turbo.svg) ends in such a hairpin: the last cubic of lines 123 and 128 runs past the path's start point, (252, 465) on the left ear, and turns back to it. At 2x each ear grows a thin spike, 3 px long in the portrait and 6 px on the ear drawn alone, where Chromium 131, Firefox 159, WebKit (macOS 27.2) and the 8x area reference draw nothing: 6 px across both ears more than 20/255 off all three browsers, 7 at 1x. At 1080p there is none: the turn spans three points.

![Hairpin spikes on femtovg master and with the prototype, against Chromium, with difference maps: both ears of glm-5v-turbo at 2x, the left one at 1x, the ear alone, and a cusp](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue-fill-reversal-spike.png)

Pixels more than 20/255 off all three browsers; in brackets, the ink in a 30 x 16 px window on the turn:

| | master 06243b80 | prototype (offset bounded) | any-of bevel test | area reference |
|---|---:|---:|---:|---:|
| [ear.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/fill-reversal-spike/ear.svg) at 2x / 1x | 17 (122.6) / 11 | 3 (114.0) / 3 | 7 (116.0) / 6 | (112.7) |
| [cusp.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/fill-reversal-spike/cusp.svg) at 2x | 12 (18.9) | 9 (16.1) | 14 (17.9) | (13.4) |
| glm-5v-turbo ear windows, 2x / 1x | 6 / 7 | 0 / 0 | 1 / 6 | |
| 6,957 corpus and reftest frames: moved (closer to / further from Chromium) | | 26 (18 / 1) | 1,027 (223 / 513) | |

**Mechanism.** [`calculate_joins`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1167-L1175) gives each point a miter vector `dmpos` = dm / |dm|², up to 24.5 long. For fills, which pass [`LineJoin::Miter`](https://github.com/femtovg/femtovg/blob/06243b80/src/lib.rs#L1388), it sets `BEVEL` only on corners past the miter limit ([L1203-L1212](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1203-L1212)), so a point inside a curve is never beveled, however sharp the turn. At such a point `expand_fill` puts the fan vertex at `p + 0.5 dmpos` and, for a concave contour as the ear is, runs the fringe strip from `p - 0.5 dmpos` to `p + 1.5 dmpos` ([L949-L963](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L949-L963), [L985-L1003](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L985-L1003)). On the ear at 2x the turn, point 31 at (127.35, 111.45), is flagged `LEFT | INNERBEVEL`, with |dmpos| = 14.54. Its outer strip vertex lands at (120.12, 110.69), 7.3 px past the turn along the ear's top edge, and the strip quads to it draw the spike. Its fan vertex (134.58, 112.21) and inner strip vertex (149.04, 113.73) land past the ear's far side; on the ear drawn alone they leave a detached 3 px dash there, which the portrait does not show.

Separately, `expand_fill` takes `bevel_join` only when a point has both `BEVEL` and `INNERBEVEL` ([L998](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L998)), where [nanovg's `nvg__expandFill`](https://github.com/memononen/nanovg/blob/ce3bf745eb2d2dbc14a50bf2446783f691ac4353/src/nanovg.c#L1950) and femtovg's [`expand_stroke`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1078) take either: e52ab3ea (2020) turned nanovg's any-of test into `contains()`; be1bf333 restored it for strokes only. Restoring it here is not the fix either: it clears the spike at 2x (portrait ear windows 6 -> 1) but not at 1x (7 -> 6), and over the corpus it moves 513 frames further from Chromium (223 closer), Ghostscript Tiger and fox-with-box-on-cloud at every framing among them.

**Repro.** At 400 x 400 this is the 2x frame shifted by whole pixels: on master the spike is row 180, x 93-98, and the dash row 182, x 107-109; the prototype leaves only x 98, at the hook.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="400" height="400">
  <rect width="1024" height="1024" fill="#fff"/>
  <path d="M 252,465 C 218,465 218,535 252,535 C 278,535 285,500 272,478 C 260,460 242,465 252,465 Z"/>
</svg>
```

```rust
use femtovg::{Color, Paint, Path};

canvas.set_size(400, 400, 1.0);
canvas.clear_rect(0, 0, 400, 400, Color::white());
canvas.scale(0.390625, 0.390625); // 1024 units in 400 px
let mut ear = Path::new();
ear.move_to(252.0, 465.0);
ear.bezier_to(218.0, 465.0, 218.0, 535.0, 252.0, 535.0);
ear.bezier_to(278.0, 535.0, 285.0, 500.0, 272.0, 478.0);
ear.bezier_to(260.0, 460.0, 242.0, 465.0, 252.0, 465.0); // left past (252, 465) and back
ear.close();
canvas.fill_path(&ear, &Paint::color(Color::black()));
```

**What a fix looks like.** The sheet's after is a prototype ([fill-extrusion-bound.patch](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/fill-reversal-spike/fill-extrusion-bound.patch)): in `expand_fill` only, the offset of a point without `BEVEL` is bounded to the miter limit `expand_fill` already takes ([2.4](https://github.com/femtovg/femtovg/blob/06243b80/src/lib.rs#L1388)), so the outer vertex lands 1.2 px past the turn and the dash goes. Of 6,957 frames (BuseyBench, the corpus and WPT-derived reftests, at three or four framings) it moves 26: 18 closer to Chromium (glm-5v-turbo, Ghostscript Tiger at every framing, six svgenius icons, ember at 1x), 7 with an unchanged count, and 1 further (ember at 2x: 3 px change by at most 2/255, one crossing the threshold).

What it leaves sits on the 0.23 px hook and in the cusp's sub-pixel tip, #418's thin-tip case; through an exact-area mask, which draws no fringe (both builds then render the same frame), both reductions are at 0. Strokes share `calculate_joins` and spike too (`stroke-width="4"` at 2x: to x 115, 12 px left of the turn); the prototype leaves them alone.

Related: #418 (thin tips, the residual here), #410 (a different fringe error, on self-crossing fills), #327 and #408. Probes, numbers and both patches: [demo-assets harness/fill-reversal-spike](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/fill-reversal-spike).
