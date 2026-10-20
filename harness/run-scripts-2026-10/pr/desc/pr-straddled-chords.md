Stacked on #392: this PR is its last two commits.

A fill covers a pixel by its share inside the path as it was flattened. Every chord cuts inside its curve's bend by up to its sagitta, so every curved edge falls short of the curve. Quartering the tolerance fixes that, but at 1.41 times the points and 10 to 21 % more instructions on curve-heavy files. This PR gets almost the same accuracy for less.

- **Straddle each curve with its chords.** Each point between two chords moves outward, toward their control points, by the mean of the two chords' shifts. A chord's shift is 3/8 of its control points' mean distance from it, which is half the sagitta on a circular arc. The chords then cross the curve and stray about half the sagitta either side of it, instead of all of it inside. A cubic's ends stay where the path put them.
- **The clip test.** #380 lets a draw skip a clip whose shape holds it. That test now allows a moved point its shift at a round corner, and nothing at a point the path put or past a straight side.
- **Flatten at half the tolerance (0.125).** Round joins and caps take a few more segments with it.

### Evidence

![the tiger, the Firefox mascot, DuckDuckGo, puzzle-fox, two icons and a 270 px circle at 1080p: master, this PR, the exact area, each one's difference from it, Chromium's GPU rasterizer and each one's difference from that](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-straddled-chords.png?v=64e2b00)

The exact area is Chromium 131 at 8 device pixels a pixel, averaged. In the difference panels, orange is 9 to 20/255 off and red is beyond that. Chromium's GPU rasterizer flattens about as coarsely as master did, so the circles move away from it while they move onto the exact area.

**Against the exact area,** over the 1,170 frames that have it, master d70ffeb against this PR:

| | master | this PR |
|---|---:|---:|
| pixels beyond 20/255 | 6,544,877 | 6,391,965 |
| pixels beyond 8/255 | 7,429,062 | 7,052,239 |

- 715 frames end nearer the area by their summed difference, and 41 end farther.
- On cc0d841, quartering the tolerance cut 155,334 pixels beyond 20/255 and this approach cut 153,333. That is 98.7 % of the gain at about 1.2 times the points instead of 1.41.

**The 41 that end farther** are large circles and arcs at 1080p; 39 of them are clip probes and clip-path reftests.

- SVG's circle reaches femtovg as four cubics, which bulge past the true circle by up to 0.027 % of its radius: 0.07 px at 270 px.
- This PR follows those cubics closely. At 270 px its polygon encloses 25 px² less than the cubics do, and master's 92 px² less.
- Master's chords happened to cancel the bulge. The last row of the sheet shows it.

**Over the whole corpus,** 1,888 of 4,784 frames change. Against Firefox, 608 move nearer and 173 farther; against software Chromium, 437 and 372.

### Tests

- `the_loop_flattens_a_cubic_as_the_recursion_did` now models the straddle.
- `only_a_point_between_chords_stands_off_by_the_straddle`, `a_vertex_takes_no_slack_from_the_paths_curves`, and a new straight-side case in `an_outlines_stray_gives_no_way_past_a_straight_side` pin down the clip test. Each fails if its part of the allowance is dropped.
- 556 tests pass with `wgpu` and 304 without.

### Cost

Instructions per frame at 1080p against master d70ffeb, with #392 under this PR:

| | change |
|---|---:|
| the tiger | -4.7 % |
| puzzle-fox | -3.6 % |
| the Firefox mascot | -4.3 % |
| the card pages | -6.7 to -8.8 % |
| eight icons | median -2.4 %, worst +0.7 % |
| DuckDuckGo | +1.7 % (within its 4.1 % spread) |

- **This PR on its own** adds 6 to 12 % over #392 on curve-heavy files, and 0.4 to 0.6 % on the card pages.
- **Frame time,** in paired runs against master on a loaded machine: cards -3.1 %, tiger -0.3 %, puzzle-fox +1.1 %. I will time them again on an idle one.
- **Phones.** On the A12 and A14 efficiency cores, an earlier revision measured -5.1 / -5.2 % instructions and -4.6 / -4.9 % cycles against master.
