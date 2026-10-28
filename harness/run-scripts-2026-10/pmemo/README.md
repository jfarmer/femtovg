# wgpu pipeline lookups, 2026-10-05

Evidence for the fork branches `wgpu-pipeline-memo` (cc33a86) and `wgpu-uniforms-once` (4ae7bc8, on top of it),
both on upstream master eb4fe53. Apple M4 Max, Metal, harness at 1080p. Nothing here is published.

Builds (`build.sh TAG` = the demo-assets harness with every cfg master has; `build_rotate.sh TAG` = `pm_rotate.rs`):
`bin/_logos_full_pm_base` master eb4fe53, `_logos_full_pm` cc33a86, `_logos_full_pmu` 4ae7bc8,
`bin/pm_rotate_base` / `pm_rotate_final` the same two trees.

| file | what |
|---|---|
| `memosim-instrumentation.patch`, `memosim.py`, `memosim.jsonl` | throwaway counters in `update_renderpass`: calls, map lookups, distinct pipelines and what a list of 1..16 recent pipelines would answer (FIFO and LRU), one 1080p frame of each of 1,196 corpus files |
| `instr.py`, `instr_variants.txt` | instructions and cycles a frame (long run minus short run under `/usr/bin/time -l`); variants: list of 2 / 8 / 16 / 64 (`pm2`..`pm64`), FNV map alone (`pmfnv`), list of 16 + FNV (`pm16fnv`) |
| `pm_rotate.rs`, `rotate.py`, `rotate_variants.txt`, `rotate_final.txt` | 1,000 fills a frame rotating through 2..72 pipelines, round-robin medians of the encode time; variants as above plus a ring instead of `truncate` + `insert(0)`, and `pack`: no list, a hand-written `Hash` that packs the key into two words |
| `paired.py`, `measure1.txt`, `measure2.txt`, `paired.jsonl` | paired alternating runs master vs cc33a86, two passes (load 4.5-6 and 4.1-5.4; Firefox and WindowServer busy throughout) |
| `hashes.py`, `hashes_pm.txt`, `hashes_pm_base_pm.jsonl` | SHA-256 of the second frame, 1,209 files at 1080p and at the 460 x 260 fit, master vs cc33a86: 2,418 identical |
| `paired_uniforms.txt`, `instr_uniforms.txt`, `hashes_pmu.txt` | cc33a86 vs 4ae7bc8 |
| `sample_*.txt`, `sample_share.py`, `sample_tree.py` | `/usr/bin/sample` call graphs of the cards page. Its share for the lookups (29-48 % of `flush_to_output` in five runs on master, 0.3 % on the branch while `flush_to_output` itself lost 5 % of its samples) is several times what the counters and the paired timings give (9 % of the encode time): not usable for time shares here |
| `test_wgpu.log`, `test_wgpu_uniforms.log` | `cargo test --features wgpu`, 449 passed on each tree |

Seen in the call graphs and not measured on their own: `RenderPassBuilder::new` creates the viewport uniform buffer
and bind group every frame (and `set_viewport` again for every target of another size); the uniform staging `Vec`
starts empty every frame and grows by doubling; `queue.write_buffer` of the vertices goes through a fresh staging
buffer every frame.
