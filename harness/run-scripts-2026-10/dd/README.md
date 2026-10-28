# path-dedupe (repeated vertex) evidence, 2026-10-09

Branch `path-dedupe` 0d36c10 on upstream master d70ffeb, worktree `~/src/femtovg-wt/dd`. Not pushed.
Run everything through `python3 tool.py SCRIPT ...` (registers the builds, CORPUS_RUN_OUT = this dir).
`refs/` holds symlinks into `../pr/refs` plus references generated here for the moved frames (make_refs.sh).

- `pair_sweep.py m8 rv framings=z1,z2,z4,hd,z05,z025,z01`: 8,372 pairs, 464 changed (accuracy.jsonl, png_changed/).
- `classify_rv.py m8 rv` -> classify.jsonl: merges per frame (rvd, RV_DIAG=1), every changed pixel inside a merged
  contour's box or (layers) the same boxes shifted by the layer origin (`layer_offsets.py`).
- `cmp_control.py`: hole-strip probe vs its control. `cmp_m8x.py`: master with exact-repeat LineTos dropped
  (m8x_lineto_exact.patch) equals the fix on all 93 exact-only frames. `genuine.py`: pixels farther from agreeing refs.
- `hash_cmp.py rv rvf`: the final form renders all 8,372 frames as rv.
- Cost: `cpu/cb_instr.py` (PathCache::new alone, in-crate test bench `cpu/cache_bench_test.rs` appended by
  `cpu/build_cb.sh`; LO=20 HI=1020) is the reliable code-cost measure; `cpu/cpu_instr.py` (Void-canvas frame) and
  `instr.py` (harness) carry 1-2 % of binary-layout noise across builds (variant e2 did less work than rvf and
  counted 1.2 % more). Logs: instr*.log.
- Sheet: sheets/pr-repeated-vertex.png; description draft: desc/pr-repeated-vertex.md.
