# Text probes

Text that femtovg's text code draws and the rest of the corpus does not have: a gradient that is radial, in
bounding-box units, on a stroke, across several glyph runs, in a turned or stretched group, on both sides of the
size at which femtovg stops using the glyph atlas, and inside a layer; and four probes without a gradient. Each file
is 200 x 200, so at the fit (`z1`) the canvas scale is exactly 1, the one scale at which femtovg takes gradient text
from the atlas. All of it is set in Arial or Times New Roman, which the reference Chromium and usvg resolve to the
same static faces on macOS.

The harness draws the text as glyph runs (`--cfg harness_text`, "Text as glyph runs" in `harness/README.md`); without
that these files draw nothing. Frames are at the `harness/corpus_run` framings and the reference is Chromium 131
rasterizing in software (`refs.py chromium`). femtovg is master d70ffeb (`m389g`) and femtovg/femtovg#389 at 86cb3de
(`p389g`), which applies a gradient across the whole run when text is drawn as outlines.

| probe | what it draws |
|---|---|
| `gradient-radial` | a radial gradient in user space |
| `gradient-bbox-units` | two gradients in bounding-box units, SVG's default, the second with a `gradientTransform` |
| `gradient-stroke` | a gradient stroke and no fill |
| `gradient-across-runs` | one gradient across a line in two fonts and three `tspan`s, which is three glyph runs |
| `gradient-transformed-groups` | gradient text in a turned, a skewed, a stretched and a mirrored group |
| `gradient-size-threshold` | one gradient on an 88 px line and a 96 px line: at `z1` the first comes from the atlas and the second is drawn as outlines |
| `gradient-in-layers` | gradient text in a group with opacity, which is a layer, and in a group clipped by a path |
| `gradient-fade` | a gradient from opaque to transparent, over a light and a dark band |
| `solid-transformed-groups` | a solid fill and a solid stroke in the same four groups |
| `stroke-wide-round` | a 10 px stroke with round joins on 100 px text |
| `stroke-dashed` | a dashed stroke |
| `fill-opacity-overlap` | glyphs that overlap, filled at half opacity |

## master and #389

The question for a change is whether any frame ends farther from the reference than it was.

Bit for bit (`identity.py m389g p389g`, 12 files at 9 framings): 46 frames are the same and 62 differ. The four
probes without a gradient are the same at every framing. The six gradient probes whose text is 92 px or less at the
fit are the same at `z1`, where both builds take the text from the atlas, and differ wherever else the text is in
the frame. `gradient-size-threshold` and `gradient-transformed-groups` differ at `z1` as well: at scale 1 a 96 px
line is drawn as outlines, and so is text in a group that is turned or stretched. With `TEXT_AS_PATHS=1` all 108
frames are the same on the two builds.

Against Chromium (`ab_refs.py m389g p389g refs=chr`, the four framings that have a reference): 26 of 48 frames
change, all 26 toward Chromium. Of the 1,099,691 pixels the builds differ on, 1,084,892 end nearer Chromium and 3,669
farther, and their mean distance from it goes from 104.1 to 4.5 of 255. No frame is farther from Chromium with #389
by the share of pixels beyond 8/255, by the share beyond 20/255 or by the structural share.

Structural share of the frame against Chromium, in percent, master and then #389 where the two differ:

| probe | z1 | z2 | z4 | hd |
|---|---|---|---|---|
| `gradient-radial` | 0.000 | 7.324 -> 0.000 | 23.699 -> 0.000 | 3.447 -> 0.000 |
| `gradient-bbox-units` | 0.000 | 7.369 -> 0.000 | 24.340 -> 0.000 | 3.812 -> 0.000 |
| `gradient-stroke` | 0.000 | 6.217 -> 0.000 | 22.728 -> 0.000 | 3.557 -> 0.000 |
| `gradient-across-runs` | 0.000 | 1.865 -> 0.000 | 6.092 -> 0.000 | 1.087 -> 0.000 |
| `gradient-transformed-groups` | 0.686 -> 0.000 | 4.945 -> 0.000 | 1.039 -> 0.000 | 2.578 -> 0.000 |
| `gradient-size-threshold` | 2.736 -> 0.000 | 17.937 -> 0.000 | 17.912 -> 0.000 | 10.269 -> 0.000 |
| `gradient-in-layers` | 0.000 | 5.720 -> 0.000 | 25.084 -> 0.000 | 3.019 -> 0.000 |
| `gradient-fade` | 0.000 | 6.327 -> 0.000 | 19.977 -> 0.000 | 3.075 -> 0.000 |
| `solid-transformed-groups` | 0.003 | 0.000 | 0.000 | 0.000 |
| `stroke-wide-round` | 0.000 | 0.000 | 0.000 | 0.000 |
| `stroke-dashed` | 0.014 | 1.071 | 1.399 | 0.136 |
| `fill-opacity-overlap` | 0.000 | 0.000 | 0.000 | 0.000 |

`text-probes.png` has every probe at `hd` on master, on #389, on #389 with text as paths and in Chromium.

## Differences that are in both builds

`stroke-dashed` differs from Chromium on master and on #389 alike. femtovg cuts the dashes of a glyph it draws as an
outline in font units, and strokes a glyph from the atlas without dashes. Drawn as paths the same text is at
2.64 % of pixels beyond 20/255 at `z4`, and as glyph runs at 14.76 %.

`fill-opacity-overlap` is the other way round. A glyph run fills each glyph on its own and covers an overlap twice,
as Chromium does. usvg's outlines of the line are one path and cover it once, so the text drawn as paths is the one
that differs (0.073 % structural at `z4`). The line is anchored at its start because usvg and Chromium place a
middle-anchored line with `letter-spacing` differently.
