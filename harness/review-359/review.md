# Review of femtovg/femtovg#359 (Allow gradients to specify color space)

Reviewed at head 45398ede, trial-merged with master cbc175e8 (CHANGELOG.md is the only conflict). Built and tested locally on WGPU/Metal (M4 Max).

**Does it do what the earlier review asked?** Yes, every point:
- Non-sRGB gradients go through the existing 256-texel LUT; the two-stop shader and both backends' shaders are untouched (the PR changes no shader file). A two-stop gradient given a non-sRGB space is promoted to a two-stop MultiStop, so sRGB two-stop gradients keep the shader path.
- `LinearRgb` is in the enum (with Oklab, Oklch, Hsl; `#[non_exhaustive]`, `Ord + Hash`, serde-gated).
- `GradientStop` / `MultiStopGradient` ordering uses `total_cmp` on offsets, colour channels and tint, and includes the space; `PartialEq` follows `Ord`.
- Naming is `with_interpolation_space` / `set_interpolation_space`; `Color` stays sRGB.
- CHANGELOG entry present; tronical's stale-comment nit is reworded.

**Results**
- Merged tree: 683 tests pass with `--features wgpu` (including 20-odd new unit tests); `cargo fmt --check` clean; `--no-default-features` and wasm32 builds clean; clippy reports the same 12 warnings as master (none new).
- #350: closes it. The NaN probe from the issue (a `[0, 0.5, 1]` gradient drawn first, then `[0, NaN, 1]`): on master the NaN bar takes the first gradient's ramp (centre pixel (220, 30, 30) after it, (124, 124, 30) alone, 190 levels apart); with the PR the NaN stop is dropped and both are (30, 125, 124), 0 levels apart. The PR covers all three bullets of #350's proposal and its test list (non-finite stops through every constructor, differing LUTs, `[0, 0.5, 1]` unchanged, #329/#326 tests green).
- #378: closes its femtovg half. A 256 x 64 horizontal red-to-lime gradient against Chromium 131 (CSS `in <space>` gradients and an SVG `color-interpolation="linearRGB"` gradient; middle row, levels in any channel):

| space | max diff | px > 2 | px > 8 | midpoint femtovg / Chromium |
|---|---:|---:|---:|---|
| sRGB (default) | 1 | 0 | 0 | (127,128,0) / (127,128,0) |
| linearRGB (CSS and SVG reference identical) | 6 | 8 | 0 | (187,187,0) / (187,187,0) |
| Oklab | 7 | 9 | 0 | (208,168,0) / (207,168,0) |
| Oklch | 8 | 4 | 0 | (248,148,0) / (248,149,0) |
| HSL | 2 | 0 | 0 | (255,254,0) / (254,255,0) |
| black to white, linearRGB | 6 | 5 | 0 | (187,187,187) both |
| red-yellow-blue, linearRGB | 12 | 29 | 2 | (254,254,0) / (254,254,12) |
| transparent red to blue, linearRGB (straight alpha) | 6 | 3 | 0 | (221,128,221) / (220,127,221) |

  The usvg half of #378 is untouched: usvg drops `color-interpolation`, so the WPT pair in #378 still renders in sRGB through any usvg-driven consumer until resvg reads the attribute.

**Findings (none blocking)**
1. The LUT is sampled with the half-texel lag of #429: texel i holds the colour at i/256 and is drawn at (i+0.5)/256. In sRGB the lag is invisible; in linearRGB, where a channel rises steeply from zero, it shows: the red-yellow-blue ramp is 12 levels off at the yellow stop (blue is 0 where Chromium has 12). All of the table's maxima sit at a stop or at an end. Baking texel i at (i+0.5)/256 would remove it; that is a one-line change in `gradient_span` and independent of this PR.
2. `set_interpolation_space(Srgb)` on a gradient promoted to MultiStop leaves it a MultiStop (same pixels, LUT instead of the exact shader, and 8-bit quantisation). Demoting an exactly-spanning two-stop MultiStop back to TwoStop would make `with_interpolation_space(LinearRgb).with_interpolation_space(Srgb)` a no-op.
3. `total_cmp` orders -0.0 before 0.0, so offsets -0.0 and 0.0 are now different cache keys (a second LUT texture, and `GradientStop(-0.0, c) != GradientStop(0.0, c)`). Harmless; normalising -0.0 to 0.0 in `from_stops` removes it.
4. Dropping a non-finite stop changes the drawn gradient (`[0, NaN, 1]` becomes a two-stop gradient). That matches the doc comments and Canvas 2D's `IndexSizeError` stance; worth a sentence in the CHANGELOG, which only mentions the colour space.
5. The CHANGELOG conflict with master is trivial; the author needs to merge master.

**Interaction with #429 (hard stops):** the design is compatible but not additive: the per-fragment stop evaluator #429 proposes would be exact in sRGB only; non-sRGB gradients keep the LUT (and its blurred hard stops) unless the evaluator also converts per fragment. #359 changes the same `gradient_span` and `gradient_store` code, so whichever lands second rebases.

**Recommendation:** approve after the master merge. Items 1-4 can be follow-ups; item 1 is worth doing together with #429. Merging closes #350 and, for the femtovg side, #378.
