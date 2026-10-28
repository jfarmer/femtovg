# Dashing starts a new subpath at every vertex a dash crosses

femtovg dashes the flattened path chord by chord, so a dash that crosses a vertex is stroked as several open subpaths, each butt-capped and none joined. At a corner the dash loses its join: a 16 px dashed stroke loses its 8 x 8 px outer corner, and the dashed polylines of BuseyBench's [claude-opus-5-5.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/claude-opus-5-5.svg) lose 2 px per corner against Chromium, Firefox and WebKit at 1080p. On a curve the pieces are shorter than the 1 px fringe and each one adds ink: the dashed iris rings of [gemini-3-7-flash.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/gemini-3-7-flash.svg) (stroke-width 1.5, dashes of 2 and 3 units) come out as bright dots where the browsers draw a faint ring, with 1.65-1.90x their ink at 2x. [gemini-3-8-flash.svg](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/gemini-3-8-flash.svg)'s rings do the same.

![Before (femtovg master 06243b80), after (the fix direction written into the SVG), Chromium 131, and both against Chromium: the left iris of gemini-3-7-flash.svg at 2x with one arc per dash; a dashed corner of claude-opus-5-5.svg at 1080p and a 16 px dashed corner at 1x with the dash as one subpath; a dashed line with a collinear point every 0.5 px at 1x with one segment per dash; segments 0.1 to 0.5 px long at 1x](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue-dash-split-vertices.png)

| gemini-3-7-flash, both irises | ink at 2x | px off all three at 2x | px off all three at 1080p |
|---|---:|---:|---:|
| femtovg master 06243b80 | 1.51 | 65 | 47 |
| femtovg, each dash's pieces joined into one polyline | 1.16 | 30 | 9 |
| femtovg, each dash one arc subpath | 1.08 | 18 | 16 |
| Chromium 131 / Firefox 159 / WebKit (macOS 27.2) | 0.80 / 0.85 / 0.92 | | |

Ink is what the rings add, relative to the 8x area reference; px are pixels more than 20/255 off all three browsers (0 at 2x without the rings).

[`Path::dashed_with_tolerance`](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L197-L229) flattens the path and calls [`dash_line_segment`](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L1073) once per chord. The `DashCursor` carries the dash phase across chords, but every visible piece gets its own `move_to`/`line_to` ([L1092-L1093](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L1092-L1093)), which `expand_stroke` caps at both ends. Written out as one `M a L b` subpath per piece, the irises render bit-identically to the dashed originals; per eye, 31 of the rings' 48 dashes are split.

A piece shorter than the fringe inks as if it were 0.8-0.9 px long: its two cap ramps ([`butt_cap_start`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1270)/[`butt_cap_end`](https://github.com/femtovg/femtovg/blob/06243b80/src/path/cache.rs#L1281)), each a fringe long and centred on an end, overlap, and the quad between them faces away and is culled. Isolated 1 px wide segments at 1x put down 8.74x their exact ink at 0.1 px, 1.69x at 0.5 px and 1.00x from 0.9 px (Chromium and Firefox 0.90-1.00x). That floor is what the one-arc row still leaves: 15 of its 18 px are on the inner ring, whose dashes are 0.78 px long.

**Repro.** The first dash's outer corner stays black:

```svg
<svg viewBox="0 0 200 200" width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" fill="#000"/>
  <path d="M40 60 L120 60 L120 160" stroke="#fff" stroke-width="16" stroke-dasharray="100 20" fill="none"/>
</svg>
```

```rust
use femtovg::{Path, Verb};

let mut plain = Path::new();
plain.move_to(20.0, 28.0);
plain.line_to(180.0, 28.0);
let mut points = Path::new(); // the same line with a collinear point every 0.5 px
points.move_to(20.0, 28.0);
for i in 1..=320 {
    points.line_to(20.0 + 0.5 * i as f32, 28.0);
}
let subpaths = |p: &Path| p.dashed(&[2.0, 2.0], 0.0).verbs().filter(|v| matches!(v, Verb::MoveTo(..))).count();
assert_eq!(subpaths(&plain), 40); // 40 dashes
assert_eq!(subpaths(&points), 160); // the same 40, four pieces each
// Stroked 1 px wide at 1x, white on black: `plain` 1.00x the exact ink, `points` 1.44x.
```

**What a fix looks like.**
- Keep a dash one subpath: `line_to` across a chord's end while inside a dash, `move_to` only where a dash begins. That restores the joins inside a dash (the corner 64 -> 0 px off all three browsers, claude-opus-5-5 2 -> 0 per corner) and takes the irises from 65 to 30 px.
- Better, as Skia does: `SkDashPath::InternalFilter` takes each dash as a piece of the original lines and curves (`SkPathMeasure::getSegment`) for the stroker to flatten with its joins, and joins a closed contour's last dash to its first. One arc per dash, the sheet's after, gives the irises 18 px and 1.08x.
- For the floor, do for length what `stroke_path_internal` does for width ([lib.rs#L1623-L1635](https://github.com/femtovg/femtovg/blob/06243b80/src/lib.rs#L1623-L1635)): draw a subpath shorter than the fringe a fringe long about its centre, its coverage scaled by length / fringe. Written into the SVG, that takes isolated segments to 1.00x at every length and the irises to 1 px.

Listed in #337 without an issue. #337's zero-length dashes that draw no caps come from the same dasher, which drops them ([`skip_empty_entries`](https://github.com/femtovg/femtovg/blob/06243b80/src/path.rs#L950-L959)). Measured on WGPU; the dasher and the stroke geometry are shared by both backends. Probes and every number: [demo-assets harness/dash-split-vertices](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/dash-split-vertices).
