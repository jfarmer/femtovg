# Round caps and joins drawn short of their arc

`expand_stroke` takes the number of points in a round cap from
`curve_divisions(half width, PI, tess_tol)`, which counts chords, and draws one
chord fewer than it asks for. The fan's rim sits at the half width plus half the
fringe and its antialiasing ramp falls to nothing on the chords, so the cap's
half-coverage outline is the polygon inscribed in the circle of the half width.
Under 1.62 px wide a cap is two chords (a triangle, 64 % of the half disc), under
3.03 px three, under 4.86 px four. Swept over every width from 1 px to 100 px, the
chords cut 0.108-0.237 px inside the arc (just above and just below 1.616 px, where
a fourth point comes in), up to nearly twice the tolerance of 0.125. `round_join` takes its point count
from the same number: under 1.62 px any turn up to 120 degrees gets two points,
the bevel's chord, and under 3.03 px any turn up to 90 degrees.

All numbers: femtovg master 06243b80 through the corpus harness on WGPU
(`bin-caps/_logos_full_mstc`, built from 06243b80 with the harness of demo-assets
692a9958; it renders the BuseyBench frames bit-identically to `bin/_logos_full_mst4`),
the prototype (`bin-caps/_logos_full_caps`, `prototype.patch` on 06243b80),
Chromium 131, Firefox 159, WebKit (macOS 27.2) and the area reference (Chromium
at 8x, 4x at 1080p, blocks averaged). "Off" is more than 20/255 in some channel.
Framings: z1 = the 200-unit box at 1x in 460 x 260, z2 = 2x, hd = 1080p.

## Files

- `lines.py` writes the reductions, 200 x 200 units (z1 draws a unit to a pixel,
  white on black) and `shapes.json`, their geometry:
  `caps.svg` (15 widths 0.5-8, a horizontal and a 30-degree stroke each, each
  cell at its own sub-pixel offset: 60 round caps), `caps-butt.svg` (the same
  with butt caps), `joins.svg` (16 polylines, widths 1.5, 2.5, 4, 6, turning 30,
  60, 90, 120 degrees, round joins, butt caps), `joins-miter.svg`,
  `joins-bevel.svg`, `sheet-caps.svg` / `sheet-joins.svg` (the sheet's rows, the
  strokes' sides on quarter pixels, where Chromium's rows of samples agree with
  the area), `repro.svg` (the issue's repro).
- `files.py` writes the run's `files.json` and links the corpus references;
  `render.py` renders it with a build (`mstc`, `caps`, or `capx<m>`: the
  experiment binary with `FEMTOVG_CAP_MODE=m`).
- `measure.py` compares the cap and join windows of `caps.svg`, `caps-butt.svg`
  and `joins.svg` with their exact coverage (16 x 16 samples a pixel), writes
  `numbers.json` (output: `measure.txt`); `capink.py` gives each cap's ink beyond
  the exact half disc in px^2 (`capink.txt`); `repro_count.py` (`repro_count.txt`);
  `counts.py` the point counts and cut depths, and the cut swept over every width
  (`counts.txt`); `split.py` splits `measure.py`'s off pixels into the part past the
  stroke's end (caps) or on the join's arc and the rest (`split.txt`).
- `corpus.py` counts the corpus frames that change and whether each moves toward
  or away from Chromium, the area reference and all three browsers
  (`corpus.json`, `corpus_caps.txt`; the count alone: `corpus_count_only.*`);
  `corpus_summary.py` splits that by BuseyBench and the rest
  (`corpus_summary*.txt`).
- `modes.py` (`modes.txt`): every variant of `experiment-modes.patch` on the
  reductions and the corpus.
- `sheet.py` draws `../../issue-round-cap-tessellation.png` (`sheet.txt`).
- `prototype.patch`: the fix direction on 06243b80. `experiment-modes.patch`:
  the variants behind `FEMTOVG_CAP_MODE` (mode 0 is master, mode 8 the prototype;
  both checked frame for frame by `modes.py`).

## Reproduce

```
export CORPUS_RUN_OUT=~/runs/round-cap-tessellation          # any directory
python3 lines.py; python3 files.py
cd ../corpus_run                                             # missing Chromium refs and the reductions' four refs
python3 refs.py chromium framings=z1,z2,hd
for g in reductions checks sheetred; do python3 refs.py firefox framings=z1,z2,hd group=$g;
  python3 refs_webkit.py framings=z1,z2,hd group=$g; python3 refs_ideal.py framings=z1,z2,hd group=$g; done
cd ../round-cap-tessellation
# binaries: harness/build.sh mstc:<femtovg 06243b80>, caps:<06243b80 + prototype.patch>,
#           capx:<06243b80 + experiment-modes.patch>, with HARNESS_BIN=<dir> (render.py reads HARNESS_BIN)
python3 render.py mstc; python3 render.py caps; for m in 0 1 2 3 4 5 6 7 8 9; do python3 render.py capx$m; done
python3 measure.py mstc capx3 caps; python3 capink.py mstc capx3 caps; python3 repro_count.py; python3 split.py; python3 counts.py
python3 corpus.py mstc caps; python3 corpus_summary.py; python3 modes.py; python3 sheet.py
```

## Mechanism (06243b80)

- `src/path/cache.rs` L1035: `ncap = curve_divisions(stroke_width, PI, tess_tol)`
  with `stroke_width` half the device width (`src/lib.rs` L1655) and
  `tess_tol = TESS_TOL / dpi` = 0.125 (L391, L595). `curve_divisions` (L1263-L1267)
  returns `ceil(arc / da)`, the chords for the arc; `round_cap_start` and
  `round_cap_end` (L1291-L1321) place `ncap` points, `ncap - 1` chords.
- L1037 puts the rim at the half width plus half the fringe; the rim points get
  `u = 0`, the centre `u = 0.5`, and the shader's
  `min(1, (1 - |2u - 1|) * stroke_mult)` (`shader.wgsl` L429-L430,
  `stroke_mult = rim / fringe`, `params.rs` L128) falls to 0 on each chord. Along a
  ray to a rim point the coverage is one half at the half width; along a ray to a
  chord's middle it is one half at `r cos(theta / 2)`.
- `round_join` L1352 / L1377: `n = clamp(ceil(turn / PI * ncap), 2, ncap)` points.

`counts.txt`:

| width px | master points | deepest cut px | share of the half disc | prototype points | widest master join with 2 points |
|---:|---:|---:|---:|---:|---:|
| 1 | 3 | 0.146 | 0.64 | 6 | 120 deg |
| 1.6 | 3 | 0.234 | 0.64 | 7 | 120 deg |
| 2.64 | 4 | 0.177 | 0.83 | 8 | 90 deg |
| 3 | 4 | 0.201 | 0.83 | 8 | 90 deg |
| 4 | 5 | 0.152 | 0.90 | 9 | 72 deg |
| 6 | 6 | 0.147 | 0.94 | 10 | 60 deg |
| 8 | 7 | 0.136 | 0.95 | 11 | 51 deg |
| 26 | 12 | 0.132 | 0.99 | 18 | 30 deg |

The share is the half-coverage polygon's area, not the ink: the ramp brings a 1 px
cap's ink back to 76 % of the half disc and a 1.5 px cap's to 86 % (`capink.txt`).

## The prototype

`prototype.patch`, two parts:

1. Chords from the radius the fan is drawn at, at half the tolerance, and one
   point more than chords: `ncap = curve_divisions(rim, PI, tess_tol / 2) + 1`;
   joins take `ceil(turn / PI * (ncap - 1)) + 1` points.
2. The fan's inner points placed so that it puts down the exact cap's or join's
   area. By the shader's ramp a fan puts down `2 k` times its polygon's area,
   `k = 1/2 - t/2 + t^2/6`, `t = fringe / rim`; the polygon's first and last
   points stay on the stroke's sides. The target is the half disc (or sector) of
   the stroke's own width at the alpha a stroke thinner than the fringe is drawn
   at (`src/lib.rs` L1623-L1635), so `stroke_path_internal` passes the unclamped
   width to `expand_stroke`.

Why part 2: with part 1 alone (mode 3), a cap's ramp adds what any ramp a fringe
wide adds around a half turn, `pi f^2 / 24` = 0.131 px^2 (the outer half of the
ramp is longer than the inner), a third of a 1 px stroke's cap, and a stroke under
the fringe is drawn a fringe wide at alpha width / fringe, so its cap carries ink in
proportion to its width rather than its square. Master's pointed caps happened to
offset both. With part 1 alone caps are over-inked by 0.095-0.165 px^2 from 0.5 px
up to 2 px wide (+0.095 at 2 px), and by 0.03 at 2.5 px. `capink.txt` at z1, excess ink per cap in px^2:

| width px | half disc | master | count alone (mode 3) | prototype |
|---:|---:|---:|---:|---:|
| 0.5 | 0.098 | -0.029 | +0.165 | -0.072 |
| 1 | 0.393 | -0.093 | +0.106 | +0.006 |
| 1.5 | 0.884 | -0.125 | +0.096 | +0.007 |
| 3 | 3.534 | -0.560 | +0.027 | +0.019 |
| 6 | 14.137 | -0.769 | -0.158 | +0.003 |
| 8 | 25.133 | -0.883 | -0.221 | +0.035 |
| 16 (z2) | 100.531 | -2.450 | -0.825 | 0.000 |

Master's shortfall as a share of the half disc: 4-31 % at 1-8 px (24 % at 1 px,
31 % at 1.25 px, 16 % at 3 px, 3.5 % at 8 px).

Butt caps (`caps-butt.svg`) are within 0.04 px^2 for every femtovg build at z1
and z2. (At hd these whole-stroke sums carry about 0.7 px^2 of error that every
renderer shares, WebKit and the area reference included; `measure.py`'s windows
are used there.)

Cost: a 1-3 px cap goes from 3-4 points to 6-8 (14-18 vertices from 8-10), a
26 px cap from 12 to 18; `RoundFan::inner_radius` is a square root and a sine
per cap and per round join. Frame times were not measured.

## Numbers

`measure.txt`, px off the exact coverage in the cap and join windows, z1 / z2 / hd:

| | master | count alone | prototype | Chromium | Firefox | WebKit | area ref |
|---|---:|---:|---:|---:|---:|---:|---:|
| caps.svg, 60 caps | 156 / 334 / 936 | 22 / 12 / 51 | 10 / 0 / 1 | 125 / 272 / 519 | 125 / 271 / 549 | 8 / 3 / 0 | 1 / 0 / 0 |
| caps-butt.svg | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 19 / 26 / 30 | 19 / 28 / 31 | 10 / 2 / 0 | 1 / 0 / 0 |
| joins.svg, 16 joins | 25 / 46 / 119 | 3 / 4 / 4 | 3 / 4 / 0 | 29 / 60 / 82 | 28 / 59 / 83 | 0 / 0 / 0 | 0 / 0 / 19 |

`split.txt`: most of Chromium's and Firefox's cap pixels lie past the stroke's end,
on the arc (Chromium 97 / 241 / 485 of 125 / 272 / 519); on the joins at z1 and z2
both are off by about as much as master (29 / 60 against 25 / 46), and on the joins'
arc at z2 Chromium has 40 against master's 42. WebKit and the area reference are the
only ones near the exact coverage. Chromium and Firefox are off along the sides of
these strokes too: on the 3 px
horizontal stroke, whose sides fall at .38 of a pixel, both give 128 and 128 where
the area is 158 and 97 (and femtovg 158 and 97).

`repro_count.txt`, the whole repro frame, off the area reference / off all three
browsers: master 27 / 13, 49 / 32, 125 / 45; prototype 1 / 1, 1 / 3, 2 / 4
(z1, z2, hd). Chromium 3, 24, 286 off the area, WebKit 0.

`corpus_caps.txt`: 70 corpus files, 210 frames: the 36 BuseyBench portraits, 10
other files that ask for round caps or joins (firefox 4, icons 2, babylon,
firefox-com, logos, ember) and the 24 files of the wpt22 group
21-degenerate-paths-dashes-and-joins. 137 frames change: all 108 BuseyBench
frames, 29 of the other 10 files' 30, and none in the wpt22 group, whose one file
with round caps puts them on zero-length dashes, which the dasher drops (#337).
Toward / away:

| | Chromium | area reference | all three browsers |
|---|---:|---:|---:|
| all, z1 | 19 / 13 | 19 / 4 | 11 / 6 |
| all, z2 | 34 / 7 | 30 / 3 | 24 / 1 |
| all, hd | 36 / 5 | 29 / 4 | 23 / 1 |
| BuseyBench, z1 | 16 / 11 | 15 / 4 | 9 / 6 |
| BuseyBench, z2 | 27 / 6 | 26 / 2 | 21 / 1 |
| BuseyBench, hd | 32 / 1 | 24 / 4 | 21 / 1 |

BuseyBench px off all three, before -> after: z1 1101 -> 1091, z2 1561 -> 1509,
hd 4513 -> 4369. A frame that moves away from Chromium does so by 1-9 px, except
firefox/lists-empty-state-nova (+14 at z1, +94 at hd), which comes 33 and 80 px
nearer the area reference: Chromium is the one off there. Against the area
reference no frame moves away by more than 2 px.

The count alone (mode 3, `corpus_summary_count_only.txt`) moves BuseyBench at z1
away: 10 toward / 17 away from Chromium, 6 / 19 from the area, 4 / 20 off all
three; at 1x most portrait strokes are under a pixel wide.

`modes.txt`, all variants: caps z1/z2/hd, joins z1/z2/hd; corpus frames toward /
away from Chromium, the area reference, all three:

| mode | | caps | joins | Chromium | area | all three |
|---:|---|---:|---:|---:|---:|---:|
| 0 | master | 156/334/936 | 25/46/119 | | | |
| 1 | chords from the rim at tess_tol, +1 point | 57/137/660 | 6/9/54 | 78/33 | 66/24 | 49/30 |
| 2 | chords from the half width at tess_tol, +1 point | 80/196/712 | 6/13/54 | 86/27 | 69/19 | 53/22 |
| 3 | chords from the rim at tess_tol/2, +1 point | 22/12/51 | 3/4/4 | 82/32 | 64/31 | 45/33 |
| 4 | 1, inner points pushed out to straddle the arc | 34/22/102 | 6/5/6 | 77/38 | 60/39 | 46/34 |
| 5 | 3 with the straddle | 29/6/1 | 4/4/0 | 71/40 | 57/40 | 44/36 |
| 6 | 3, an approximate equal-ink radius | 13/18/68 | 3/4/5 | 88/14 | 77/6 | 57/10 |
| 7 | 6 with the straddle | 12/0/0 | 3/4/0 | 83/23 | 74/12 | 54/11 |
| 8 | 3, inner points fitted to the exact area (prototype) | 10/0/1 | 3/4/0 | 89/25 | 78/11 | 58/8 |
| 9 | 8 at tess_tol | 16/20/99 | 7/5/7 | 87/25 | 74/15 | 58/9 |

## Portraits on the sheet (hd, `sheet.txt`)

- gpt-5-6-luna-pro, a hair strand's start (stroke-width 25, 26 px, 12 points on
  master): off Chromium 12 -> 1, off the area 6 -> 0. The one left is Chromium's
  (233 against an area of 215, after 211).
- claude-opus-5-5, the tips of the upper eyelashes (stroke-width 1.4, 1.48 px),
  box (858, 456, 42, 24): off Chromium 21 -> 17, off the area 5 -> 1, off all three
  4 -> 0. At the four tips the prototype changes, master is 24-35 levels light of all
  four references, the prototype within 8. The 17 left are unchanged, along the lid's
  upper edge, where Chromium is 19-38 levels off the area reference and the prototype
  within 7. In the window x 845-905, y 440-480 (four lashes): off Chromium 26 -> 22,
  off the area 6 -> 1, off all three 4 -> 0; the whole frame: off all three 44 -> 29,
  off the area 878 -> 856.
- glm-5v-turbo, an upper-lash arch (stroke-width 2.5, 2.64 px): off Chromium
  11 -> 6, off all three 8 -> 3. At the caps (the pixels the prototype changes)
  off Chromium 5 -> 0, off all three 5 -> 0; the 6 left are under the arch's apex,
  pixels the prototype does not change.
- Not on the sheet: grok-4-5's brow ends (stroke-width 4 and 6) move 6 -> 0 off
  Chromium, but none of those pixels is beyond 20/255 of the area reference before or
  after: master is 5-15 levels light of it, Chromium and Firefox 6-29 dark. The
  whole frame at hd is unchanged against the area (776 -> 776) and off all three
  (365 -> 365); it shows Chromium's error more than femtovg's.

Also seen and left alone: the inner corner of a thin 90-degree join under-inks on
master and with the prototype (`sheet-joins.svg`, 3 px: 191 where the browsers
and the area have 239-240).
