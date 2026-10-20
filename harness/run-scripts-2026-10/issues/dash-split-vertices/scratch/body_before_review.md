# Dashing starts a new subpath at every vertex a dash crosses

femtovg's dasher flattens the path and dashes each chord on its own, so a dash that crosses a vertex of the flattening is stroked as several open subpaths, each with its own butt caps. Where the pieces are shorter than the 1 px fringe, every extra pair of caps adds ink. The dashed iris rings of BuseyBench's [gemini-3-7-flash.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/gemini-3-7-flash.svg) (`<circle r="21" stroke-dasharray="3,2">` and `<circle r="16" stroke-dasharray="2,3">`, stroke-width 1.5) come out as distinct bright dots where Chromium, Firefox and WebKit draw a faint ring. With the portrait fitted to 200 px and zoomed 2x (z2), femtovg puts down 1.90x Chromium's ink there, 1.79x Firefox's and 1.65x WebKit's.

![Before (femtovg master), after (the same dashes written as one arc or one segment per dash; for the isolated segments, each drawn 1 px long at its length's opacity), Chromium 131, and both against Chromium and against the 8x area reference: the left iris of gemini-3-7-flash.svg at z2, a dashed line with a collinear point every 0.5 px at 1x, and isolated butt-capped segments 0.1 to 1 px long at 1x](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue-dash-split-vertices.png)

| Both iris boxes | z2 ink | z2 px | hd ink | hd px |
|---|---:|---:|---:|---:|
| femtovg master 06243b80 | 1.51 | 65 | 1.02 | 47 |
| femtovg, its pieces joined into one polyline per dash | 1.16 | 30 | 1.00 | 9 |
| femtovg, one arc subpath per dash | 1.08 | 18 | 1.00 | 16 |
| Chromium 131 | 0.80 | | 0.99 | |
| Firefox 159 | 0.85 | | 0.98 | |
| WebKit (macOS 27.2) | 0.92 | | 0.98 | |
| area reference (Chromium at 8x) | 1.00 | | 1.00 | |

Ink is what the four rings add over the same renderer's frame without them, relative to the area reference. px counts pixels more than 20/255 off all three browsers; without the rings there are 0 at z2 and 3 at hd. z2 is a 460 x 260 frame at 0.39 px per unit; hd is 1920 x 1080 at 1.05 px per unit. At hd all 16 px left by one arc per dash are within 20/255 of the area reference (master is 83 px off it).

[`Path::dashed_with_tolerance`](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L197-L228) flattens the path ([L203](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L203)) and calls [`dash_line_segment`](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L1073) once per chord ([L213-L215](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L213-L215)). The `DashCursor` carries the phase from chord to chord, but every visible piece gets its own `move_to`/`line_to` ([L1092-L1093](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L1092-L1093)). A dash that crosses n vertices becomes n + 1 open subpaths, and `expand_stroke` caps each one at both ends ([cache.rs#L1049-L1060](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1049-L1060), [#L1104-L1115](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1104-L1115)).

I wrote the iris circles out as femtovg's own pieces, one `M a L b` subpath each, using an f32 emulation of the flattener and the dasher on usvg's cubics. That renders bit-identically to the original at z1, z2 and hd. Per eye, 18 of the outer ring's 27 dashes and 13 of the inner ring's 21 are split. At z2, 66 of the 79 pieces are under a pixel.

A butt cap's antialiasing ramp is a fringe long and centred on the endpoint ([`butt_cap_start`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1270)/[`butt_cap_end`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1281), called with `d = -fringe_width * 0.5`). The caps of abutting pieces therefore overlap across the vertex. Pieces a pixel long add no ink; shorter ones add more the shorter they get. The straight-line table is at 1x, with 1 px wide lines dashed 2 2 in 20 rows. Ink is relative to the exact ink, which the area reference matches:

| A 160 px line | femtovg | Chromium | Firefox | WebKit | femtovg px off all three |
|---|---:|---:|---:|---:|---:|
| no inner points | 1.00 | 1.00 | 1.00 | 1.00 | 0 |
| a collinear point every 1 px | 0.95 | 0.94 | 0.94 | 1.05 | 0 |
| every 0.5 px | 1.39 | 0.87 | 0.86 | 1.10 | 2,678 |
| every 0.3 px | 1.86 | 0.82 | 0.81 | 1.27 | 3,497 |

The points move the browsers too: Chromium and Firefox lose ink and WebKit gains some. The area reference stays at 1.00.

### Subpaths shorter than the fringe

Dashed or not, an open butt-capped subpath shorter than the fringe inks as if it were 0.8-0.9 px long, whatever its real length. Its two cap ramps overlap and both draw. The quad between them is inverted and culled, because both stroke paths cull back faces ([wgpu.rs#L1923](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu.rs#L1923), [#L1961](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu.rs#L1961), [#L2030](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu.rs#L2030)).

| Isolated 1 px wide segment at 1x, ink vs exact | 0.1 px | 0.25 px | 0.5 px | 0.75 px | 0.9 px and up |
|---|---:|---:|---:|---:|---:|
| femtovg | 8.74 | 3.50 | 1.69 | 1.21 | 1.00 |
| Chromium, Firefox | 0.90 | 0.99 | 0.99 | 1.00 | 0.98-1.00 |
| WebKit | 2.14 | 1.26 | 1.03 | 1.00 | 0.99-1.00 |

The end cap also starts half a fringe back along the last chord, so a last chord shorter than half a fringe puts the ramp over the previous segment. A 2 px segment with a collinear point 0.05, 0.1 or 0.3 px before its end inks 1.12x, 1.10x or 1.06x. From 0.5 px it is exact.

Keeping each dash whole is therefore not enough where dashes are short. One polyline per dash keeps the flattening's vertices inside each dash, short first and last chords included: that gives 1.14x on the 0.3 px line and 30 px on the irises. One segment or arc per dash gives 1.00x and 18 px. The 18 sit on the inner ring, whose 0.78 px dashes are shorter than the fringe. Drawn a pixel long at their length's opacity, they leave 1 px.

At z1 (0.20 px per unit) every dash in the file is shorter than a pixel. There femtovg puts down 2.86x the area's ink in the iris boxes, and one arc per dash still gives 2.00x; the browsers give 0.72-0.81x.

### Repro

```svg
<svg viewBox="0 0 200 200" width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200"/>
  <path d="M20 28 L180 28" stroke="#fff" stroke-width="1" stroke-dasharray="2 2" fill="none"/>
  <!-- the same line with a collinear point every 0.5 px (written out in line-points.svg) -->
  <path d="M20 36 L20.5 36 L21 36 ... L180 36" stroke="#fff" stroke-width="1" stroke-dasharray="2 2" fill="none"/>
</svg>
```

```rust
use femtovg::{Color, Paint, Path, Verb};

// at 1x (set_size(.., 1.0)), on black
let paint = Paint::color(Color::white()).with_line_width(1.0).with_line_dash(&[2.0, 2.0]);

let mut plain = Path::new();
plain.move_to(20.0, 28.0);
plain.line_to(180.0, 28.0);

let mut points = Path::new();
points.move_to(20.0, 36.0);
for i in 1..=320 {
    points.line_to(20.0 + 0.5 * i as f32, 36.0);
}

canvas.stroke_path(&plain, &paint);
canvas.stroke_path(&points, &paint);

// The same 40 dashes: one subpath each, and four 0.5 px subpaths each.
let subpaths = |p: &Path| p.dashed(&[2.0, 2.0], 0.0).verbs().filter(|v| matches!(v, Verb::MoveTo(..))).count();
assert_eq!((subpaths(&plain), subpaths(&points)), (40, 160));
```

### What a fix looks like

- Keep a dash one subpath. While the cursor is still inside a dash at the end of a chord, `line_to` the next point, and `move_to` only where a dash begins. With the iris dashes written that way, the irises go from 65 to 30 px and from 1.51x to 1.16x.
- Do as Skia does: emit each dash as a piece of the original segment or curve, and let the stroker flatten it in device space like any other path. `SkDashPath::InternalFilter` calls `SkContourMeasure::getSegment` once per dash, moving to the dash's start, and `getSegment` returns curve pieces. That is the sheet's after: 18 px and 1.08x on the irises, 1.00x on the lines.
- For the floor, do for length what `stroke_path_internal` already does for width. A stroke thinner than the fringe is drawn a fringe wide with its alpha scaled by its width ([lib.rs#L1623-L1635](https://github.com/femtovg/femtovg/blob/06243b80/src/lib.rs#L1623-L1635)). Likewise, a subpath shorter than the fringe could be drawn a fringe long about its centre, with its coverage scaled by length / fringe. The paint's alpha applies to the whole draw, so a per-subpath scale would go into the cap vertices' along coordinate, which the stroke shader multiplies in ([shader.wgsl#L430](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu/shader.wgsl#L430)). Written into the SVG, this takes isolated segments to 1.00x at every length (180 -> 16 px off all three browsers) and the irises' arcs from 18 px to 1.

Related: #279 added the dasher. #327 was the same fringe overlap across a fill's width, which #408 handles for thin fills with coverage masks; strokes do not go through them. Area coverage, as in #13 (and #358 for fills), has no such floor: the 8x area reference puts down 0.94-1.05x the exact ink at every segment length. I measured on WGPU, but the dasher and the stroke geometry are shared by both backends.

Probes: [demo-assets harness/dash-split-vertices](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/dash-split-vertices).
