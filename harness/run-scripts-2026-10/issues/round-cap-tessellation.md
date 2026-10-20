# Round caps and joins fall short of their arc: thin strokes end short and pointed

`expand_stroke` draws round caps and joins inside their arc and a chord short. Under 1.62 px wide a cap is a triangle, under 3.03 px three chords; the chords cut 0.11-0.24 px inside the arc, up to nearly twice `tess_tol` (0.125); joins turning up to 90° on strokes under 3 px are bevels. In BuseyBench at 1080p it shows on [claude-opus-5-5](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/claude-opus-5-5.svg)'s eyelashes, [glm-5v-turbo](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/glm-5v-turbo.svg)'s lashes and [gpt-5-6-luna-pro](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/gpt-5-6-luna-pro.svg)'s hair. WebKit (macOS 27.2) and the area reference draw them round; Chromium 131 and Firefox 159 are off the exact coverage too, on joins about as much as master at 1x and 2x.

![Before (master 06243b80), after (prototype), Chromium 131, and both against Chromium](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue-round-cap-tessellation.png)

| px > 20/255 off the exact coverage, 1x / 2x / 1080p | femtovg 06243b80 | prototype | Chromium 131 | Firefox 159 | WebKit |
|---|---:|---:|---:|---:|---:|
| [caps.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/round-cap-tessellation/caps.svg): 60 round caps, 0.5-8 px at 1x | 156 / 334 / 936 | 10 / 0 / 1 | 125 / 272 / 519 | 125 / 271 / 549 | 8 / 3 / 0 |
| [joins.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/round-cap-tessellation/joins.svg): 16 round joins, 1.5-6 px at 1x, 30-120° | 25 / 46 / 119 | 3 / 4 / 0 | 29 / 60 / 82 | 28 / 59 / 83 | 0 / 0 / 0 |

On master a cap 1-8 px wide puts down 0.04-1.2 px² (4-31 %) less than its half disc.

**Why.** [`expand_stroke`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1035) takes `ncap = curve_divisions(half width, PI, tess_tol)`, a count of chords ([L1263-L1267](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1263-L1267)), and [`round_cap_start`/`round_cap_end`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1291-L1321) place that many points. The rim sits half a fringe outside the half width ([L1037](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1037)) and the [stroke mask](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu/shader.wgsl#L429-L430) falls to zero on each chord, so the half-coverage outline is the polygon inscribed in the half width's circle (that polygon is 64 % of the half disc under 1.62 px). [`round_join`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1352) takes `clamp(ceil(turn / PI * ncap), 2, ncap)` points: two, a bevel, up to 120° under 1.62 px and 90° under 3.03 px. nanovg's [`nvg__expandStroke`](https://github.com/memononen/nanovg/blob/ce3bf745eb2d2dbc14a50bf2446783f691ac4353/src/nanovg.c#L1738-L1740) does the same.

**Repro**, at 1x. Master: 27 px off the area reference, 13 off all three browsers; prototype: 1 and 1.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <rect width="200" height="200" fill="#000"/>
  <g stroke="#fff" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path d="M74.3 74.5 h12" stroke-width="1.5"/>
    <path d="M74.55 79 h12" stroke-width="2"/>
    <path d="M74.8 84.5 h12" stroke-width="3"/>
    <path d="M75.05 91 h12" stroke-width="4"/>
    <path d="M104.25 75.25 h16.5 v8" stroke-width="3"/>
  </g>
</svg>
```

```rust
use femtovg::{Color, LineCap, LineJoin, Paint, Path};

canvas.set_size(200, 200, 1.0);
canvas.clear_rect(0, 0, 200, 200, Color::black());
let round = Paint::color(Color::white()).with_line_cap(LineCap::Round).with_line_join(LineJoin::Round);
let mut line = Path::new();
line.move_to(74.3, 74.5);
line.line_to(86.3, 74.5);
canvas.stroke_path(&line, &round.clone().with_line_width(1.5));
let mut corner = Path::new();
corner.move_to(104.25, 75.25);
corner.line_to(120.75, 75.25);
corner.line_to(120.75, 83.25);
canvas.stroke_path(&corner, &round.with_line_width(3.0));
// The line's caps: 3 points each, a triangle. The corner's join: 2 points, a bevel; its outer corner pixel (121, 74) is 128, the area 236.
```

**What a fix looks like.** [The prototype](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/round-cap-tessellation/prototype.patch), the sheet's after:

- Chords from the rim's radius at half the tolerance, one point more than chords; joins take the same chords per half turn. A 1-3 px cap goes from 3-4 points to 6-8; frame times not measured.
- Inner points placed so the fan puts down the exact area: by the shader's ramp a fan puts down `2k` times its polygon's area, `k = 1/2 - t/2 + t²/6`, `t = fringe / rim`. The target is the half disc of the stroke's own width at the alpha a stroke under the fringe [is drawn at](https://github.com/femtovg/femtovg/blob/06243b80/src/lib.rs#L1623-L1635).

Chords alone over-ink caps up to about 2 px (a pixel-wide ramp around a half turn adds π/24 px², a third of a 1 px cap) and move BuseyBench at 1x away: 10 frames toward Chromium, 17 away. Straddling the chords as #393 does for curves leaves thin caps over-inked and moves 40 frames away from Chromium (mode 5); the inner-radius rule trades reduction accuracy against away-counts ([modes.txt](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/round-cap-tessellation/modes.txt)).

In every corpus file that asks for round caps or joins (36 BuseyBench portraits, 10 others), 137 of 138 frames change: 89 toward Chromium, 25 away; 78 / 11 against the area reference; 58 / 8 off all three. None moves more than 9 px further from Chromium, except firefox's lists-empty-state-nova (+14, +94), which comes 33 and 80 px nearer the area reference, and none more than 2 px further from the area reference. The 24 reftests of the degenerate-paths, dashes and joins group render identically.

Related: listed in #337. #393 made curves' chords straddle them; caps and joins stayed inscribed. #401 fixed caps at repeated ends. #339 set the sub-fringe alpha the target uses. Not filed: a thin 90° join's inner corner under-inks, prototype or not (sheet, last row). Measured on WGPU; both backends share the stroke geometry. Probes and every number: [demo-assets harness/round-cap-tessellation](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/round-cap-tessellation).
