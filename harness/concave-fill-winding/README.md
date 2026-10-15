# Winding a concave fill leaves past its cover

Evidence for femtovg/femtovg's fix of the winding count a concave fill left in
the stencil where its fill vertices reach past the quad that covers it (a fringe
moves them outward from a hole, and from a contour taken for a hole's boundary;
the quad's corner at (minx - f, miny) never had the fringe). The fix draws such
a fill's fans again after the cover, coloring nothing.

- `classify.py LOG A B` / `judge.py A B`: every frame an `identity.py` LOG lists
  as changed, how far it moved, and - for the content changes - at each moved
  pixel whether B is nearer an 8x Chromium area reference than A.
- `corpus_strip.py A B OUT.png KEY:FRAMING...`: 12 x 12 crops around the moved
  pixels, five columns (before, after, Chromium, before vs Chromium, after vs
  Chromium), the moved pixels outlined in magenta
  (`../../pr-cover-winding.png`).
- `cover-scenes.json`: thin triangles and kites at sixteen sub-pixel positions,
  then a frame whose cover takes them in - the scenes of the PR's GPU test, for
  `../hard-mask-scenes/scenes_chromium.py` (`SCENES=`), `wgpu_scenes.rs` and
  `../clip-bench/gl_scenes.rs`. Both backends are pixel-identical on them; master
  puts 10, 9 and 11 pixels of the frame's colour in its hole, the fix none.
- `fill_bench_test.rs`, `build_fb.sh TAG:WORKTREE`, `fb_instr.py`: the in-crate
  bench of `PathCache::new` + `expand_fill` over a file's paths (instructions per
  pass, difference of a long and a short run).

Run of 2026-10-14 (master 9f5ad26, both builds from harness 3ff4ddc): 62 of
11,403 frames move, 132 pixels; 61 by content, 51 nearer the area (101 pixels),
9 farther (20 pixels - a leaked count had painted the later fill's colour where
its own outline under-covers the pixel).
