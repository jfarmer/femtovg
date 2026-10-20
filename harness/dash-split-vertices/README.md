# A dash split into a new subpath at every vertex it crosses

`Path::dashed_with_tolerance` flattens the path and calls `dash_line_segment`
once per chord, which `move_to`/`line_to`s every visible piece: a dash that
crosses a vertex is stroked as several open subpaths, each with its own butt
caps and no join between them. Where the vertex is a corner of the path, the
dash loses its join. Where the pieces are shorter than the 1 px fringe, they
add ink: any open butt-capped subpath shorter than the fringe inks as if it
were 0.8-0.9 px long, and a last chord shorter than half the fringe over-inks
too; even a dasher that keeps each dash whole meets that floor.

All numbers: femtovg master 06243b80 through the corpus harness on WGPU
(`bin/_logos_full_mst4`), Chromium 131, Firefox 159, WebKit (macOS 27.2) and
the area reference (Chromium at 8x, 8 x 8 blocks averaged). Ink is summed
luminance; "off" is more than 20/255 in some channel.

## Files

- `portrait.py` writes the variants of `corpus/buseybench/gemini-3-7-flash.svg`
  (the four dashed iris rings, lines 297/298 and 347/348) into
  `$CORPUS_RUN_OUT/svg`, and `$CORPUS_RUN_OUT/files.json` with the SVGs of this
  directory: `p00_orig`, `p01_nodash` (rings removed), `p02_dash_arcs` (one arc
  subpath per dash: the sheet's "after"), `p04_emul_split` (femtovg's own
  pieces, emulated in f32, one `M a L b` each), `p05_emul_joined` (the same
  pieces, one polyline per dash), `p06_arcs_floor_z2` (p02 with each dash
  under a pixel at z2 drawn a pixel long at its length's opacity; z2 only).
  Also `g38_orig`, `g38_nodash`, `g38_arcs` (`gemini-3-8-flash.svg`, its two
  dashed iris rings at lines 277/312, r=15 and r=14.5, dash 2,3, stroke-width
  1.5, opacity 0.8: as it is, removed, one arc per dash) and `opus_orig`,
  `opus_joined` (`claude-opus-5-5.svg`, its two dashed polylines at lines
  229/230, dash 5 4, stroke-width 1.5: as it is, and one subpath per dash, so
  the dash that crosses each corner keeps its miter join).
- `lines.py` writes the reductions here, 200 x 200 units so that z1 draws one
  unit to one pixel. `repro.svg` is the issue's repro as written there (two
  lines, the second with a collinear point every 0.5 px). `corner.svg`: a
  16-unit stroke, dash 100 20, whose first dash crosses a 90 degree corner;
  `corner-split.svg` femtovg's three pieces written out; `corner-joined.svg`
  one subpath per dash, the first through the corner. The rest are
  20 rows of 1 px white lines on black, butt caps:
  `line-plain`, `line-points` (a collinear point every 0.5 px), `line-points-1px`,
  `line-points-03` (every 0.3 px), all `stroke-dasharray="2 2"`; written out
  without a dash array: `line-split` (femtovg's pieces), `line-joined`,
  `line-joined-03` (one polyline per dash through the points),
  `line-segments` (one segment per dash); `pieces` (isolated segments
  0.1-4 px long), `pieces-scaled` (those under 1 px drawn 1 px long about their
  centre at length x opacity); `endchord-plain` / `endchord-short` (2 px
  segments, the second with a collinear point 0.05-1.5 px before the end).
- `measure.py` prints the numbers below and writes `numbers_mst4.json`;
  `sheet.py` draws `../../issue-dash-split-vertices.png` (before | after |
  Chromium | before vs Chromium | after vs Chromium) and prints the red left
  in each after-vs-Chromium crop; `locate.py` places a variant's off pixels
  on the iris rings by radius and angle. `emul_stats.json`: chords, dashes and
  pieces per ring.

## Reproduce

```
export CORPUS_RUN_OUT=~/runs/dash-split-vertices      # any directory
python3 portrait.py
cd ../corpus_run                                      # bin/_logos_full_mst4: harness/build.sh mst4:<femtovg 06243b80>
python3 accuracy.py mst4 framings=z1,z2,hd png=$CORPUS_RUN_OUT/png
python3 refs.py chromium framings=z1,z2,hd; python3 refs.py firefox framings=z1,z2,hd
python3 refs_webkit.py framings=z1,z2,hd; python3 refs_ideal.py framings=z1,z2,hd
cd ../dash-split-vertices
python3 measure.py mst4; python3 sheet.py; python3 locate.py z2 p02_dash_arcs all3
```

## Numbers

`p04_emul_split` renders bit-identically to `p00_orig` at z1, z2 and hd, and
`line-split` to `line-points` at all three. Per eye, the r=21 ring (dash 3,2)
is 32 chords and 27 dashes, 18 of them split, 45 pieces (32 under 1 px at z2);
the r=16 ring (dash 2,3) 32 chords, 21 dashes, 13 split, 34 pieces (all under
1 px at z2).

### gemini-3-7-flash

Portrait, both iris boxes (each the rings plus 2 px): ring ink over the same
renderer's `p01_nodash` frame, relative to the area reference's; px off all
three browsers' frames of `p00_orig`.

| | z1 ink | z1 px | z2 ink | z2 px | hd ink | hd px |
|---|---:|---:|---:|---:|---:|---:|
| femtovg master | 2.86 | 60 | 1.51 | 65 | 1.02 | 47 |
| one polyline per dash (p05) | 1.99 | 33 | 1.16 | 30 | 1.00 | 9 |
| one arc per dash (p02) | 2.00 | 36 | 1.08 | 18 | 1.00 | 16 |
| p02, dashes under 1 px lengthened (p06) | | | 0.96 | 1 | | |
| Chromium | 0.72 | | 0.80 | | 0.99 | |
| Firefox | 0.75 | | 0.85 | | 0.98 | |
| WebKit | 0.81 | | 0.92 | | 0.98 | |

At z2 master's ring ink is 1.90x Chromium's, 1.79x Firefox's, 1.65x WebKit's;
at hd 1.03x, 1.04x and 1.04x (the dashes are 2-3 px long there).
Without the rings femtovg is 0 px off all three in the boxes at z1 and z2, 3 at
hd. At hd p02 is 3 px off the area reference in the boxes, master 83; the
16 px p02 leaves off all three browsers are all within 20/255 of the area
reference. At z2 Chromium is itself 105 px off the
area reference in the boxes without the rings (femtovg 4).

Where p02's 18 px at z2 sit (`locate.py`): 15 on the r=16 ring, whose 0.78 px
dashes are shorter than the fringe; 2 on the r=21 ring at 357 degrees, its
0.76 px closing dash (130 to 131.95 units); 1 on another r=21 dash (336.6
degrees). p06, which lengthens every dash under a pixel, closing dashes
included, leaves that last one. 5 of the 18 sit at 356-357 degrees, within a
pixel of where the circles start and end. There Skia joins a closed contour's
last dash to its first (`SkDashPath::InternalFilter`, "join up with the
(skipped) initial segment"), so Chromium draws one 4.95-unit dash across the
r=21 ring's start and one 2.53-unit dash across the r=16 ring's; p02, like
master, draws two subpaths that meet there with butt caps. Of the 9 px of
p02 more than 20/255 off the area reference in the sheet's left-iris crop, 6
are on the r=16 ring, 1 on the r=21 ring's closing dash, and 2 inside the
iris (r 8-11 units), off the area reference without the rings too.

### gemini-3-8-flash

Both iris boxes (rings plus 2 px), same metrics:

| | z1 ink | z1 px | z2 ink | z2 px | hd ink | hd px |
|---|---:|---:|---:|---:|---:|---:|
| femtovg master | 3.47 | 16 | 1.80 | 31 | 1.02 | 13 |
| one arc per dash (g38_arcs) | 2.40 | 3 | 1.20 | 8 | 0.98 | 2 |
| Chromium | 0.66 | | 0.80 | | 1.00 | |
| Firefox | 0.73 | | 0.84 | | 0.98 | |
| WebKit | 0.64 | | 0.82 | | 0.95 | |

Without the rings femtovg is 0, 0 and 2 px off all three in the boxes (held to
the browsers' frames without the rings). Held to the browsers' frames with
the rings, the frame without them is 5 px off all three at z2 (140 at hd):
at z2 master's rings are further from the browsers than no rings at all.

### Corners

`corner.svg` at z1: `corner-split.svg` (the three pieces `M a L b`) renders
bit-identically to it at z1, z2 and hd. The outer corner square of the first
dash (8 x 8 px) averages 0 in femtovg and 255 in Chromium, Firefox, WebKit and
the area reference: 64 px off all three browsers. `corner-joined.svg`: 255,
0 px off.

`claude-opus-5-5.svg` at hd, within 6 px of each corner of its dashed
polylines (the corner lies 1.39 units into a dash): master is 2 px off all
three browsers per corner, 28 and 45/255 off the area reference; `opus_joined`
0 and 0. The two frames differ at 14 px: 11 within 3 px of a corner, 3 by
1/255 elsewhere (the dashes written out to four decimals). At z1 the corners
move by up to 13/255 and no pixel is off all three; at z2 they are outside the
frame.

### The repro

`repro.svg` at z1, ink over the exact 80 px per line: the plain line femtovg
1.004 (Chromium 1.000, Firefox and WebKit 1.004, area 1.004); the line with
points femtovg 1.435 (Chromium and Firefox 0.871, WebKit 1.042, area 1.004).
The f32 emulation of the dasher gives the Canvas snippet's subpath counts:
40 (plain), 160 (points) and 3 for the corner's 2 dashes.

### Lines

Lines at z1, ink relative to the exact ink (length x 1 px; the area reference
measures 1.00 on every file):

| | femtovg | Chromium | Firefox | WebKit | femtovg px off all three |
|---|---:|---:|---:|---:|---:|
| line-plain | 1.00 | 1.00 | 1.00 | 1.00 | 0 |
| line-points (0.5 px) | 1.39 | 0.87 | 0.86 | 1.10 | 2,678 |
| line-points-03 (0.3 px) | 1.86 | 0.82 | 0.81 | 1.27 | 3,497 |
| line-points-1px | 0.95 | 0.94 | 0.94 | 1.05 | 0 |
| line-joined, held to line-points | 1.00 | | | | 303 |
| line-joined-03, held to line-points-03 | 1.14 | | | | 1,646 |
| line-segments, held to line-points / -03 | 1.00 | | | | 303 / 1,113 |

line-segments is 0 px off the area reference against either file; line-joined-03
930. Chromium and Firefox are 920 and 960 px off the area reference on
line-points, WebKit 2,529.

Isolated segments (`pieces`), ink / exact by length: femtovg 8.74 (0.1 px),
4.15 (0.2), 3.50 (0.25), 2.66 (0.3), 2.15 (0.4), 1.69 (0.5), 1.36 (0.6), 1.15
(0.7), 1.21 (0.75), 1.09 (0.8), 1.00 from 0.9 px; Chromium and Firefox
0.90-1.00; WebKit 2.14, 1.40, 1.26, 1.17, 1.08, 1.03, then 0.99-1.01.
`pieces-scaled`: femtovg 1.00 (0.998-1.010) at every length; 180 -> 16 px off
all three (the 16: 0.5-0.7 px segments inside one pixel, whose stand-in spreads
24/255 into the next).

`endchord-short`, ink / exact by last-chord length: femtovg 1.12 (0.05 px),
1.10 (0.1), 1.09 (0.2), 1.06 (0.3), 1.03 (0.4), 1.00 from 0.5; `endchord-plain`
1.00. Chromium and Firefox 0.93-0.99, WebKit 0.99-1.07.
