#327 [CLOSED] Thin filled shapes render bolder than browser coverage AA (fringe overlap on sub-pixel fills)
Thin filled shapes — sub-2-device-pixel crescents, hairlines drawn as closed fills rather than strokes — render substantially bolder in femtovg than the coverage-based AA browsers produce. Found while sweeping a 26-file Firefox-ecosystem SVG corpus against Chromium 149 across zoom ladders.

**Minimal repro:** one closed cubic crescent (a cartoon smile), pure fill `#090707`, anti-alias on, no strokes: [thin-fill-crescent.svg](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/thin-fill-crescent.svg). femtovg (top of each pair) vs Chromium 149 (bottom) at 2×/4×/8× device scale:

![smile comparison](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/thin-fill-overink-smile.png)

Coverage-weighted ink (sum of darkness over the tile) and pixels darker than 20/255:

| device scale | femtovg ink / Chromium ink | px >20 femtovg | px >20 Chromium |
|---|---|---|---|
| 2× | **2.18×** | 153 | 79 |
| 4× | 1.55× | 422 | 290 |
| 8× | 1.28× | 1317 | 1049 |

The overshoot is a roughly constant per-edge-pixel excess — it dominates when the shape is thinner than the AA fringe and washes out as geometry grows — which points at the fringe-based AA inherited from nanovg: fill edges get an expanded ~1px alpha ramp, and for a shape thinner than the fringe the two edge ramps overlap, so interior alpha exceeds the true area coverage. Browsers (Skia's analytic AA, and supersampling rasterizers) compute per-pixel coverage of the actual geometry, so a 0.5px-thick crescent correctly renders as a ~50%-alpha hairline instead of a bold stroke.

**In the wild:** Mozilla's `fox-with-box-on-cloud.svg` illustration ([SVG](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/fox-with-box-on-cloud.svg)) draws all its face detail (smile, muzzle, whisker lines) as thin closed fills. femtovg / Chromium / diff overlay at 2.1×:

![fox scene](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/thin-fill-fox-scene.png)

8.1% of scene pixels differ beyond 20/255, and cartoon-style assets in the corpus with the same idiom (`puzzle-fox`, `splash-logo`, `kit`) carry 4–7% deltas with the same edge-bolding signature.

Happy to work on a fix — the candidate directions I see are (a) clamping interior alpha where opposing fringes overlap (cheap, shader- or tessellation-side), or (b) shrinking the opaque core by the fringe half-width so ramp+core integrates to the true coverage for sub-fringe thicknesses, which is what the stroke path already gets right via `stroke_thr`. If there's a preferred direction, I'll take it.

## New York Times marks (2026-10-03)

Five NYT marks ([corpus/nyt](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/corpus/nyt): the Cooking wordmark, three game icons, the Crossplay app icon) and the NYT tile logo of the firefox.com enterprise image, on master 9d574e0 against Chromium 131 from thumbnail size up to 4x. No structural difference at any zoom, and the tile logo renders bit-identically under `evenodd` and `nonzero`, so it is not winding: it is this issue. Ink weight against Chromium within the artwork's crop:

| mark | ~20 px | ~50 px | ~100 px | fit (200 px) | 2x | 4x |
|---|---:|---:|---:|---:|---:|---:|
| enterprise NYT tile logo | +101 % | +22 % | +4 % | +0.3 % | 0.0 % | -0.2 % |
| Cooking wordmark | +101 % | +15 % | +3 % | +1.0 % | 0.0 % | +0.1 % |
| game icon (bbcae) | +75 % | -2 % | +1 % | -0.5 % | +0.1 % | -0.1 % |
| Letter Boxed | +24 % | +0.3 % | +0.2 % | -0.1 % | 0.0 % | 0.0 % |
| Crossplay app icon | +9 % | +1.9 % | +0.4 % | +0.2 % | 0.0 % | 0.0 % |

Inside the enterprise image itself the NYT tile logo is 9x11 px at 1x and carries +41 % ink, +15 % at 2x, +3 % at 4x.

Master's fringe fills, #358's exact coverage and Chromium 131 at the small sizes (each row's caption has both builds' ink weight and pixels beyond 20/255):

![NYT marks at thumbnail sizes: fringe fills clog, exact coverage matches Chromium](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/nyt-fringe-vs-coverage.png)

#358 brings every one within 3 % of Chromium's ink (the tile logo at ~20 px: 24 % of the crop beyond 20/255 down to 0.7 %). Its cost on these frames at 460x260, steady state on an M4 Max: the Crossplay icon 1.6 to 2.7 ms, the game icon 1.2 to 1.9 ms, the wordmark 1.1 to 1.3 ms.

--- comments: 3
> matthargett: Most of what this issue measures turns out to be #308, the clockwise-winding edge shift, and femtovg/femtovg#336 fixes that part.

The fringe is extruded along each point's miter vector, whose direction follows the contour's point order, so a clockwise contour pushed it outward and the fill landed a whole fringe too wide. A thin shape pays that on **both** of its edges at once, which is why the effect looked so much larger on thin geometry than on ordinary shapes — exactly the "roughly constant per-edge-pixel excess" described above.

Ink versus exact area for a filled bar at 45°, measured against analytic ground truth rather than another renderer:

| bar width | master | with #336 |
|---|---|---|
| 0.25px | 9.36× | 2.44× |
| 0.5px | 5.27× | 1.45× |
| 1px | 2.99× | 1.12× |
| 2px | 2.06× | **0.98×** |
| 4px | 1.49× | **1.02×** |

At 30° the same shape: 9.15× / 5.08× / 3.04× / 2.03× / 1.52× becomes 2.98× / 1.46× / 1.00× / 1.00× / 1.00×.

So anything about 1px and wider is now within a couple of percent of its true coverage, and 2px and wider is exact.

**What is left is the real subject of this issue.** Below roughly one device pixel the ramps extruded from opposite edges still overlap, and they blend `src-over` rather than combining as coverage, so the interior ends up darker than the true area. Cross-section of a 0.5px bar at 45°, alpha per pixel across the bar:

```
x=126  x=127  x=128        sum    exact
 0.04   0.94   0.04        1.02    0.707     -> 1.45x
```

The peak re
> matthargett: Here is what the diff looks like with femtovg/femtovg#336 applied, on this issue's own in-the-wild asset.

![fox after #336](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/thin-fill-fox-post-336.png)

`fox-with-box-on-cloud.svg` vs Chromium 131, same harness as the original measurement:

| zoom | master | with #336 |
|---|---|---|
| 100% | 3.91% | 3.91% |
| 210% | 8.14% | 8.14% |
| 400% | 7.02% | 7.02% |

**Identical** — #336 does not move this asset at all. Its contours already wind the way the fringe extrusion expects, so none of its residual was the #308 dilation. That makes it the clean isolation of what this issue is really about: everything red in the third column is fringe-versus-coverage, with nothing from the winding bug mixed in.

Worth noting the sign, because it changes the shape of the fix. On this asset femtovg carries *less* ink than Chromium, not more (0.95x at 100%, 0.89x at 210%) — the muzzle outline and smile come out fainter than the reference rather than bolder, visible in the middle row above. The over-inking in the synthetic crescent and the under-inking here are the same root cause seen from two sides: the ramp is a fixed ~1px wide in device space regardless of the geometry under it, so sub-pixel features get their coverage spread over too wide a band. Whether that reads as bolder or fainter depends on whether the opposing ramps overlap and blend up, or the feature is thin enough that the spread just dilutes it.

So a fix tha
> matthargett: As of master 0d09c8f (#336, #339, #322/#323 and #340 merged) the two sheets at the top of this issue are regenerated from that build, and what remains is confined to fills thinner than about one device pixel.

The in-the-wild witnesses are near parity: the crescent is 1.07× / 0.996× / 1.01× Chromium 131 ink at 2×/4×/8× (Firefox is 0.98× / 1.00× / 1.00× of Chromium on the same tiles), and `fox-with-box-on-cloud.svg` is 1.03 % / 1.38 % / 0.96 % of pixels beyond 20/255 at 100/210/400 % with 0.000 % structural and whole-frame ink 1.004 / 0.996 / 0.999. The "identical" fox table in my previous comment came from a build without #336; with #336 as merged the 210 % figure is 1.38 %, and what is left on the fox is ramp pixels on ordinary 2–3 px outlines, slightly under-inked (0.52 vs 0.56), not bolding. `puzzle-fox` was not re-measured (not in a local corpus).

What remains, on synthetic ladders (ink over exact area, no strokes): the two 1 px ramps of a convex fill composite source-over instead of adding as coverage, so a bar of width w centred on a pixel row peaks at 1 − ((1−w)/2)² where coverage is w, and the concave (stencil) path is worse because each wall's ramp reaches full alpha on its inner side regardless of the opposite wall. Everything 2 px and wider is exact on both paths; the browsers themselves sit at 0.9–1.2× here.

| fill width | rect at 45°, master | Chromium / Firefox | ring R = 8, master | Chromium / Firefox |
|---|---|---|---|---|
| 0.25 px | 2.48× | 0.48× / 0.48× 
