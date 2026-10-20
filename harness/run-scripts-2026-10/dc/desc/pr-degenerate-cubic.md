`tesselate_bezier` keeps a piece when its control points lie close enough to its chord, measured against the chord's length: `(d2 + d3)^2 < tess_tol * chord^2`. A cubic whose four points coincide has a zero chord, so both sides are zero, the test fails, and the cubic is halved down to the depth limit: 4,095 pieces, none of which adds a point. Every square corner of a `rounded_rect_varying` is such a cubic (it emits one for each corner, whatever the radius), as is every curve under a transform that scales to nothing (the canvas builds the path cache before anything could skip it), and a zero-length curve in SVG data. nanovg flattens the same way; Skia sizes a cubic by Wang's formula, which is zero for it, and takes one segment.

The verb loop now skips such a cubic before flattening. The outline keeps the point it already has, exactly as the descent left it, and every other curve pays one comparison. A cubic whose ends meet but whose control points do not, a loop, is flattened as before.

### Cost

M4 Max, 1080p, master d70ffeb -> this PR, medians of paired runs:

| | master | PR |
|---|---:|---:|
| 300 tabs rounded on top (`rounded_rect_varying(.., 6, 6, 0, 0)`): CPU recording and encoding a frame | 6.01 ms | 0.80 ms |
| the same, whole frame | 7.23 ms | 1.49 ms |
| the same, instructions a frame | 112.0 M | 14.8 M |
| an icon with four zero-length curves: encoding | 0.306 ms | 0.286 ms |
| Ghostscript tiger (none): encoding / instructions | 2.033 ms / 27.98 M | 2.033 ms / 27.97 M |
| clip-bench cards page (none): instructions | 31.22 M | 31.30 M |

The corpus renders to the bit as on master: all 8,372 frames of its 1,196 files at 1x, 2x, 4x, 1080p, 0.5x, 0.25x and 0.1x. Its SVGs hold few such curves, 7 of 57,390 in three files, so the saving there is small (0.9 % of a frame's instructions on the ember logo); UI paths make them, and under a scale from zero every curve is one.

### Tests

Unit tests count the pieces the flattener examines: none for a cubic that is a point, none for a rounded rect scaled to nothing (master: 4,095 a curve), and for a tab with two square corners half the pieces of the same rect rounded all round; a loop whose ends meet is still flattened.
