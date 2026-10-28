# Dashing starts a new subpath at every vertex a dash crosses

femtovg's dasher dashes the flattened path chord by chord, so a dash that crosses a vertex is stroked as several open subpaths, butt-capped and unjoined. At a corner of the path the dash loses its join: a 16 px stroke loses its 8 x 8 px outer corner, and the dashed polylines of BuseyBench's [claude-opus-5-5.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/claude-opus-5-5.svg) lose their miter tips (2 px per corner off Chromium, Firefox and WebKit at 1080p). On a curve, pieces shorter than the 1 px fringe add ink: the dashed iris rings of [gemini-3-7-flash.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/gemini-3-7-flash.svg) (stroke-width 1.5, dashes 2 and 3 units) come out as bright dots where the browsers draw a faint ring, with 1.65-1.90x their ink at z2 (the portrait fitted to 200 px, zoomed 2x). At 1080p, where the dashes are 2-3 px long, the ink is within 5 % of theirs, but 47 px of the irises are off all three. The rings of [gemini-3-8-flash.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/gemini-3-8-flash.svg) show the same: 31 -> 8 px off all three at z2 with one arc per dash.

![Before (femtovg master 06243b80), after (the fix direction written into the SVG), Chromium 131, and both against Chromium: the left iris of gemini-3-7-flash.svg at z2, one arc per dash; a corner of claude-opus-5-5.svg's dashed line at 1080p and a 16 px dashed corner at 1x, the dash as one subpath; a dashed line with a collinear point every 0.5 px at 1x, one segment per dash; isolated segments 0.1 to 0.5 px long at 1x, drawn 1 px long at their length's opacity](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue-dash-split-vertices.png)

| gemini-3-7-flash, both irises | z2 ink | z2 px | 1080p ink | 1080p px |
|---|---:|---:|---:|---:|
| femtovg master 06243b80 | 1.51 | 65 | 1.02 | 47 |
| femtovg, its pieces joined into one polyline per dash | 1.16 | 30 | 1.00 | 9 |
| femtovg, one arc subpath per dash | 1.08 | 18 | 1.00 | 16 |
| Chromium 131 | 0.80 | | 0.99 | |
| Firefox 159 | 0.85 | | 0.98 | |
| WebKit (macOS 27.2) | 0.92 | | 0.98 | |
| area reference (Chromium at 8x) | 1.00 | | 1.00 | |

Ink: what the rings add over the same renderer's frame without them, relative to the area reference. px: more than 20/255 off all three browsers (0 at z2 and 3 at 1080p without the rings). At 1080p one arc per dash is 3 px off the area reference on the irises, master 83; the 16 px it leaves off all three browsers are all within 20/255 of it.

[`Path::dashed_with_tolerance`](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L197-L229) flattens the path ([L203](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L203)) and calls [`dash_line_segment`](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L1073) once per chord ([L213-L215](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L213-L215)). The `DashCursor` carries the phase across chords, but each visible piece gets its own `move_to`/`line_to` ([L1092-L1093](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L1092-L1093)), which `expand_stroke` caps at both ends ([cache.rs#L1049-L1060](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1049-L1060), [#L1104-L1115](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1104-L1115)). Written out as one `M a L b` subpath per piece (for the irises, from an f32 emulation of the flattener and the dasher), the pieces render bit-identically to the dashed originals at z1, z2 and 1080p. Per eye, 31 of the rings' 48 dashes are split.

A piece shorter than the fringe inks as if it were 0.8-0.9 px long: its two cap ramps, each a fringe long and centred on an end ([`butt_cap_start`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1270)/[`butt_cap_end`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1281), `d = -fringe_width * 0.5`), overlap and both draw, and the quad between them faces away and is culled (wgpu stencil strokes [L1923](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu.rs#L1923), [L1961](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu.rs#L1961), plain strokes [L2030](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu.rs#L2030); GL [opengl.rs#L1421-L1424](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/opengl.rs#L1421-L1424)). Isolated 1 px wide segments at 1x measure 8.74x the exact ink at 0.1 px, 1.69x at 0.5 px, 1.00x from 0.9 px (Chromium and Firefox 0.90-1.00x). A line dashed 2 2 with a collinear point every 0.5 px inks 1.39x (the browsers 0.86-1.10x); with a point every pixel it inks 0.95x, against Chromium's and Firefox's 0.94x. Of the 18 px that one arc per dash leaves on the irises, 15 sit on the inner ring, whose dashes are 0.78 px long, and 2 on the outer ring's 0.76 px closing dash.

### Repro

```svg
<svg viewBox="0 0 200 200" width="200" height="200" xmlns="http://www.w3.org/2000/svg">
<rect width="200" height="200" fill="#000"/>
<path d="M40 60 L120 60 L120 160" stroke="#fff" stroke-width="16" stroke-dasharray="100 20" fill="none"/>
</svg>
```

The first dash's outer corner stays black. `repro.svg` in the probes is the two lines below as SVG, points written out: 1.00x and 1.44x the exact ink at 1x.

```rust
use femtovg::{Color, Paint, Path, Verb};

// at 1x (set_size(.., 1.0)), on black
let paint = Paint::color(Color::white()).with_line_width(1.0).with_line_dash(&[2.0, 2.0]);

let mut plain = Path::new();
plain.move_to(20.0, 28.0);
plain.line_to(180.0, 28.0);

let mut points = Path::new(); // the same line with a collinear point every 0.5 px
points.move_to(20.0, 36.0);
for i in 1..=320 {
    points.line_to(20.0 + 0.5 * i as f32, 36.0);
}

let mut corner = Path::new();
corner.move_to(40.0, 60.0);
corner.line_to(120.0, 60.0);
corner.line_to(120.0, 160.0);

canvas.stroke_path(&plain, &paint); // 1.00x the exact ink
canvas.stroke_path(&points, &paint); // 1.44x
canvas.stroke_path(&corner, &Paint::color(Color::white()).with_line_width(16.0).with_line_dash(&[100.0, 20.0]));

let subpaths = |p: &Path, dash: &[f32]| p.dashed(dash, 0.0).verbs().filter(|v| matches!(v, Verb::MoveTo(..))).count();
assert_eq!(subpaths(&plain, &[2.0, 2.0]), 40); // 40 dashes
assert_eq!(subpaths(&points, &[2.0, 2.0]), 160); // the same 40, four pieces each
assert_eq!(subpaths(&corner, &[100.0, 20.0]), 3); // 2 dashes
```

### What a fix looks like

- Keep a dash one subpath: `line_to` across a chord's end while inside a dash, `move_to` only where a dash begins. That brings back the joins inside a dash (the corner 64 -> 0 px off all three browsers, claude-opus-5-5 2 -> 0 per corner) and takes the irises from 65 to 30 px.
- Do as Skia does: `SkDashPath::InternalFilter` calls `SkPathMeasure::getSegment` (that is, `SkContourMeasure::getSegment`) once per dash, which returns pieces of the original lines and curves for the stroker to flatten with their joins, and on a closed contour it joins the last dash to the first. The sheet's after is one arc per dash without that closing join: 18 px and 1.08x on the irises, 1.00x on the lines; 5 of the 18 px sit where the circles start and end, where Chromium draws one dash across.
- For the floor, do for length what `stroke_path_internal` does for width with #339's linear rule ([lib.rs#L1623-L1635](https://github.com/femtovg/femtovg/blob/06243b80/src/lib.rs#L1623-L1635)): draw a subpath shorter than the fringe a fringe long about its centre, with its coverage scaled by length / fringe. The paint's alpha applies to the whole draw, so the scale would go into the cap vertices' along coordinate, which the stroke shader multiplies in ([shader.wgsl#L430](https://github.com/femtovg/femtovg/blob/06243b80/src/renderer/wgpu/shader.wgsl#L430)). Written into the SVG, this takes isolated segments to 1.00x at every length (180 -> 16 px off all three browsers) and the irises' arcs from 18 px to 1.

Listed in #337 without an issue; #279 added the dasher. #337's zero-length dashes that draw no caps (`resvg-dasharray-0-n-square-caps`, `-round-caps`) come from the same dasher, which drops them ([`skip_empty_entries`](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L950-L959), `step > dist_tol` at [L1089](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L1089)). #327 was the same fringe overlap across a fill's width, which #408 handles for thin fills with coverage masks; strokes do not go through them. Area coverage (#13; #358, closed, for fills) has no such floor: the 8x area reference puts down 0.94-1.05x the exact ink at every segment length. Measured on WGPU; the dasher and the stroke geometry are shared by both backends.

Probes: [demo-assets harness/dash-split-vertices](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/dash-split-vertices).
