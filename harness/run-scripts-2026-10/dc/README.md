# flatten-degenerate-cubic evidence, 2026-10-09

Branch `flatten-degenerate-cubic` 80e1739 on upstream master d70ffeb, worktree `~/src/femtovg-wt/dc`. Not pushed.
- `tabs_300.svg`: 300 tabs as rounded_rect_varying(x, y, 60, 24, 6, 6, 0, 0) emits them (two point cubics each).
- `count_point_cubics.py`: point cubics in the corpus from the harness PATH_DUMP (3 files, 7 of 57,390 curves).
- `timing.py`: paired frame_ms / encode_ms (MEM_PEAKS=1, FRAMES=300, 7 rounds) for m8 vs dc.
- Rendering: `../dd/tool.py hash_cmp.py m8 dc` -> 8,372 of 8,372 frames identical.
- Instructions: `../dd/tool.py instr.py m8 dc -- ...` (frame) and `../dd/cpu/cb_instr.py m8 dcn -- ...` (PathCache::new;
  dcn = the fix without the cfg(test) counter, which the test-build bench would otherwise carry).
- Description draft: desc/pr-degenerate-cubic.md.
