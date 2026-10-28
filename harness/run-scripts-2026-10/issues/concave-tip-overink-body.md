A concave fill that is wide overall but narrows to a point, a crescent or a spike, puts far more ink into the last pixels before each point than their area: the tips come out dark and blunt where Chromium 131, Firefox 159 and WebKit fade them out. In BuseyBench the tip windows hold 72, 38, 46 and 56 pixels more than 20/255 off all three browsers at 2x (grok-4-5's hair spikes, gemini-3-7-flash's lip crescent, gemini-3-1-pro-preview's mouth corners, gemini-3-1-pro-preview-custom-tools' eye shadows and lips), and 76, 26 and 17 at 1080p. #408's exact-area masks judge a fill by its whole outline's mean width ([`is_thin`](https://github.com/femtovg/femtovg/blob/06243b80/src/clip/fill.rs#L19-L21), under 2 px for a concave fill); these measure 2.4 to 7.6 px at 2x, so they keep the stencil-and-fringe path. This is what is left of #327.

![Tips on femtovg master and with every fill drawn through an exact-area coverage mask, against Chromium, with difference maps: a hair spike at 2x and 1080p, two mouth corners at 2x, a straight wedge, the wedge cut into collinear pieces, and the lip alone](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue-concave-tip-overink.png)

Black on white at 2x, both 28 x 28 px tip windows: ink relative to the 8x area reference, and pixels more than 20/255 off it (for femtovg, the same pixels as those off all three browsers).

| both tips | femtovg master 06243b80 | Chromium 131 | Firefox 159 | WebKit (macOS 27.2) |
|---|---:|---:|---:|---:|
| [wedge](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/concave-tip-overink/wedge.svg), one segment a side | 1.11, 12 px | 0.99, 0 px | 0.99, 0 px | 0.98, 0 px |
| [the same wedge](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/concave-tip-overink/wedge-split.svg), each side in 18 collinear pieces | 1.78, 50 px | 1.02, 2 px | 1.02, 2 px | 0.99, 0 px |
| [lip crescent](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/concave-tip-overink/lip.svg) | 1.32, 38 px | 1.00, 4 px | 1.00, 4 px | 1.00, 0 px |

**Where the ink comes from.** A software replay of the WGPU concave-fill passes, from the vertices and commands femtovg emits, matches the frames within 0.9/255 and puts +15.2 of the lip's +15.3 px of excess tip ink in the fringe pass; all 38 pixels off the area have stencil 0. For a concave contour `expand_fill` gives each edge a strip from 0.5 px outside it to 1.5 px inside ([`lw = fringe_width + woff`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L986-L1002)) and insets the fill fan by half a fringe ([`woff`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L946-L962)), so each strip's inner half falls where the fan is stenciled and the fringe pass ([`concave_fill`](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu.rs#L2100-L2146), stencil equal to 0) skips it. Where the sliver is under about 1.5 px wide at a vertex, that vertex's strip reaches past the opposite edge, where nothing is stenciled, and the fringe pass draws it: next to the lip's left tip a pixel of area 0.00 gets 0.61 from the far edge's strip alone.

So it takes vertices in the narrow part, which flattening a curved sliver puts there. The straight wedge has none and stays at +1.4 px a tip (its point's own mitered join); cut into collinear pieces it puts down +10.2 px a tip. Dropping each strip's inner half in the replay takes the lip from 38 to 6 px off the area; blending each pixel once only takes it to 32.

**Repro**, at 400 x 400 the 2x frame above shifted by whole pixels:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="400" height="400">
  <rect width="1024" height="1024" fill="#fff"/>
  <path d="M 280 725 C 344 880, 680 880, 744 725 C 680 840, 344 840, 280 725 Z"/>
</svg>
```

```rust
use femtovg::{Color, Paint, Path};

canvas.set_size(400, 400, 1.0);
canvas.clear_rect(0, 0, 400, 400, Color::white());
canvas.scale(0.390625, 0.390625); // 1024 units in 400 px
let mut lip = Path::new();
lip.move_to(280.0, 725.0);
lip.bezier_to(344.0, 880.0, 680.0, 880.0, 744.0, 725.0);
lip.bezier_to(680.0, 840.0, 344.0, 840.0, 280.0, 725.0);
lip.close();
canvas.fill_path(&lip, &Paint::color(Color::black()));
```

**What a fix looks like.** The sheet's after draws every fill through an exact-area coverage mask (the harness's `FILL_MASKS`, with [the rasterizer #408's masks use](https://github.com/femtovg/femtovg/blob/06243b80/src/clip/coverage.rs#L1-L12)): the tips carry 0.99 to 1.00 of their area and the portraits' tip windows go to 0, except 2 and 3 px at 2x. Directions:

- Judge thinness locally: send a fill with a sub-pixel tip, or just the tip, through #408's masks. These fills' bounds (3,400 to 60,000 px at 1080p) fit `THIN_FILL_SPAN`; the test runs on every concave fill, so it has to be cheap.
- End each concave ramp half a pixel inside its edge, as the convex half fringe does ([`lw = woff`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L989-L995)): 6 px off the area on the lip in the replay, not 0.
- Exact coverage for every fill (#13, #357, the closed draft #358).

Related: #327 (closed by #408), #408. Probes, numbers and the replay: [demo-assets harness/concave-tip-overink](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/concave-tip-overink).
