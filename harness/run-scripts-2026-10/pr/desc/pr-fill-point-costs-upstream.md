This replaces #391, moved into this repository so that the next change can stack on it.

Every point a curve is flattened into costs work downstream: joins, the fringe, and three vertices for each triangle of the fill. This PR takes that cost down without changing a pixel, so that the next PR can flatten curves more finely without a frame costing more than it does on master.

### Commits

1. **Flatten a cubic in a loop, testing a piece before halving it.** The recursion becomes a loop over a fixed stack of the right halves still to flatten, so a flat piece is never split. It gives the same points in the same order: a test keeps the recursion as its reference over 3,000 cubics, including curves that need all ten halvings and curves that need more.
2. **Reverse a contour's directions instead of working them out again.** A fill that turns a contour round, and turns it back afterwards, negates the directions it already has. The values are equal; only a zero can come back as -0.0, which nothing reads. Two new tests cover it, and `a_stroke_after_a_fill_still_sees_the_path_as_written` now strokes the same `Path` it filled, so it reads the cache the fill handed back.
3. **Size a clip's winding triangles before building them.**
4. **Draw a fill as the fan it is, a vertex a point.** A fill was three vertices for every triangle of its fan (48 bytes a triangle). It is now the fan itself, one 16-byte vertex a point.
   - OpenGL draws `GL_TRIANGLE_FAN`.
   - WGPU has no fans, so it draws one `u32` index list built each frame. That needs no base vertex, which WebGL 2 and some Apple GPUs lack, and no vertex buffer rebind per draw, which costs about 1,400 instructions on Metal.
   - WebGL uses the same index list, because ANGLE emulates a fan draw by draw.
   - On Apple's OpenGL an indexed draw costs about 7,000 instructions more than a fan, so native OpenGL keeps fans.
   - A fan longer than 65,535 vertices is split into several about the same first vertex, because Mesa's vc4 (Raspberry Pi 3) splits a longer one about the wrong vertex.

### Output

Identical to master on every frame I rendered:

- WGPU harness: all 10,764 corpus frames (1,196 files at 9 framings, z0.1 to z4 and 1080p), compared by hash.
- OpenGL (Apple's driver, hidden window): 10 SVG files at two scales (one frame is blank) and the clip check, through both the fan path and the indexed path.

There are no screenshots because there is nothing to compare. 554 tests pass with `wgpu` and 302 without; clippy reports nothing new; the `wasm32` build checks.

New tests:

- `the_loop_flattens_a_cubic_as_the_recursion_did`
- `reversing_gives_the_directions_worked_out_again`
- `a_fill_hands_a_reversed_contour_back_as_it_found_it`
- `fan_indices_take_each_fills_fans_in_turn`
- `a_contour_longer_than_a_fan_goes_as_several`
- `fill_fans_wgpu`: one renderer, fills longer than any before them, including a 196,000-point contour drawn as three fans, each checked against its exact area.

Each fails when the code it covers is broken on purpose.

### Performance

Instructions retired per frame at 1080p, WGPU on Metal (M4 Max), master d70ffeb against this branch. Counts are the difference of a 100-frame and a 600-frame run (200 and 1,700 frames for the icons), median of 5.

| | master | this PR | change |
|---|---|---|---|
| 200 cards, plain | 31.22 M | 28.30 M | -9.4 % |
| 200 cards, rounded clips | 39.43 M | 36.72 M | -6.9 % |
| 200 cards, circle clips | 38.61 M | 35.76 M | -7.4 % |
| Ghostscript tiger | 27.94 M | 25.06 M | -10.3 % |
| puzzle-fox (Firefox) | 5.12 M | 4.41 M | -14.0 % |
| mr-settodefault | 9.04 M | 8.12 M | -10.2 % |
| duckduckgo.com | 5.11 M | 4.84 M | -5.5 % |
| NYT Crossplay app icon | 3.18 M | 2.89 M | -9.2 % |
| 8 svgenius icons | | | median -9.8 %, range -13.5 to -0.2 % |

- **Frame time.** Paired, alternating runs of 300 frames, median of 15 pairs, on a lightly loaded machine:
  - 200 cards: 2.174 to 2.079 ms (-3.5 %, faster in 14 of 15 pairs)
  - tiger: 2.320 to 2.276 ms (-6.7 %, 14 of 15)
  - puzzle-fox: 0.781 to 0.755 ms (-3.5 %, 11 of 15)
- **OpenGL.** Apple's driver, `gl_fill_bench`: 200 cards -8.1 % instructions, 200 rounded cards -6.2 %.
- **Phones.** Efficiency cores, PMU counters, warm frames, cycles compared only at the same clock. These were measured on an earlier revision of commit 4, which rebound the vertex buffer for each fill instead of building the index list, against cc0d841:

  | | instructions | cycles | other |
  |---|---|---|---|
  | iPhone XS (A12), curve-heavy files | -10.7 % | -10.3 % | L1D load/store misses -8 / -15 % |
  | iPhone 12 (A14), curve-heavy files | -10.4 % | -9.3 % | L1D load/store misses -7 / -10 % |

  Peak memory is unchanged and `__text` is 7.1 KB larger.

### Not measured

- WebGL in a browser: there is no wasm harness yet.
- OpenGL ES 2 on a Raspberry Pi. It draws fans where it drew triangle lists, and splits long ones as above.

### Next

The next PR flattens curves more finely for about what this one saves. Each point between two chords moves outward by the mean of the two chords' shifts, so the chords cross the curve instead of cutting inside every bend. The tolerance halves to 0.125, and the clip's "holds the draw" test allows for the shift at the points that moved.

Over 1,170 frames with an exact-area reference, pixels further than 20/255 from it fall from 6,706,157 to 6,552,824. Quartering the tolerance alone reaches 6,550,823 at 41 % more points, so the next PR gets 98.7 % of that gain.

With this PR under it, instructions stay below master: tiger -4.7 %, puzzle-fox -4.8 %, the card pages -6.7 to -8.9 %, icons median -1.3 %. On the phones it is -5.1 / -5.2 % instructions and -4.6 / -4.9 % cycles. These were measured against cc0d841 and will be measured again on this PR. That PR will carry the five-column comparison sheets.
