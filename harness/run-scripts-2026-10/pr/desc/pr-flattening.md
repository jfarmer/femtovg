A fill covers a pixel by its share inside the path as it was flattened, so the chords have to stay close to the curve. The flatness test - the one NanoVG took from AGG - compares the square of the control points' distances from the chord with the tolerance, so at 0.25 it let those distances sum to half a pixel and left chords up to a fifth of a pixel inside a curve: an edge pixel of a circle was 0.07 of its coverage off on average and 0.21 at worst, three times what the antialiasing itself is off by. The tolerance is now 0.0625: the chords stay within a tenth of a pixel, and a curved edge is within 0.02 on average and 0.08 at worst. A sixteenth of the old tolerance gains nothing more; the fringe's ramp is what is left.

### Evidence

The corpus files outside BuseyBench that gain the most, whole frames of master and this PR, each one's difference from the exact area (Chromium 131 at 8 device pixels a pixel, each block averaged), and the same difference for Chromium's GPU rasterizer and for WebKit at one device pixel (orange 9-20/255, red beyond 20, a deviating pixel drawn three wide):

![the tiger, a mascot, the DuckDuckGo logo, a puzzle-piece fox and two icons: master, this PR, the exact area, each build's difference from it, and Chromium's GPU rasterizer and WebKit against it](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-finer-flattening.png?v=08d020f)

What stays red is mostly not the curves' chords: on the tiger 1,472 of the 2,759 pixels beyond 20/255 are the same on master (its stripes taper to slivers thinner than a pixel, which the fringes over-ink, #327) and 325 are as far in every browser (seams between abutting shapes, at one sample a pixel).

Over the corpus, master -> PR: 3,025 of 4,784 frames are bit-identical; of the 684 changed frames that have the reference 595 move toward it and 13 away, 207 and one by more than 0.1 points. Of the 2,794,651 pixels that differ, 1,440,766 end nearer the area and 520,064 farther, 6.5 -> 3.7 of 255 from it on average.

| | master | PR | Chromium GPU | Chromium software | Firefox | WebKit |
|---|---:|---:|---:|---:|---:|---:|
| pixels beyond 20/255 of the area, over the 363 changed frames every renderer has | 287,761 | 233,366 | 177,116 | 158,448 | 132,036 | 86,603 |

Pixels beyond 20/255 of the area on the files that gain the most: the tiger 23,719 -> 13,340 over its four framings, the Firefox mascot (mr-settodefault) 8,473 -> 3,134, DuckDuckGo 4,164 -> 184, the puzzle-piece fox 3,641 -> 1,115, and icons such as `page_178` 3,569 -> 27 and `page_110_data` 2,574 -> 84.

### BuseyBench

The portraits gain as a group - 67,246 -> 46,666 pixels beyond 20/255 of the area, 153,846 -> 144,797 beyond 20/255 of software Chromium - but one regresses: at 2x its pixels beyond 20/255 of the area go 217 -> 433, and against Chromium 0.77 % -> 0.94 % of the frame, and the portraits' largest per-pixel differences from Chromium grow (10,904 -> 11,024 summed over the frames). It is not the flattening's error but #327's, which the flattening uncovers: the portrait's stubble is a dozen open curves left under SVG's default black fill, slivers a sixth of a pixel wide. Master flattens most of them to a single chord, which fills nothing (#360); flattened finer they are slivers again, and a fill thinner than a pixel is over-inked by its fringes: three of them, 6 px of ink between them, take 14 px on master and 95 here. The count of pixels that differ from Chromium at all stays where it was over the portraits (29,229,921 -> 29,228,775).

### Tests

`tests/curve_flattening_wgpu.rs`: the fill of a small circle, a large one, an ellipse and an arc of a circle of 300 px against each edge pixel's share inside, within 0.12 at worst and 0.03 on average (0.21 and 0.07 on master).

### Cost

A curve takes 1.41 times the line segments it took (the tiger at 1080p: 12,735 -> 17,996 points), and each point costs what follows it - joins, the fill's fringe, the vertices: about 640 instructions a frame. So the cost is where the curves are: on an M4 Max, instructions a frame at 1080p

| | master | PR | |
|---|---:|---:|---:|
| the tiger | 27.8 M | 31.3 M | +12.6 % |
| the puzzle-piece fox | 5.13 M | 6.19 M | +20.7 % |
| the Firefox mascot | 8.98 M | 10.18 M | +13.5 % |
| DuckDuckGo | 5.08 M | 5.59 M | +10.0 % |
| an icon (`page_326`) | 1.92 M | 2.18 M | +13.3 % |
| a BuseyBench portrait (filters) | 190.5 M | 190.6 M | +0.0 % |

and the frames of those curve-heavy files take 4 % longer in sum (the tiger at 1080p 11 %, the fox 21 %), while over the whole corpus - 2,392 frames at the fit and at 1080p, most of them filter-bound - the frames take 0.3 % longer in sum and the median frame 0.5 %.
