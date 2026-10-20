# wgpu per-frame setup costs, 2026-10-13/14

Evidence for the fork branch `wgpu-frame-setup` (on upstream master 9f5ad261). Apple M4 Max, Metal, harness at 1080p
(`da/harness/build.sh`, every cfg master has, `CARGO_PROFILE_RELEASE_DEBUG=0`, target `target-fsetup`).

Pushed commits: 2de63e42 (viewport bind groups per target size, kept through #366's LRU helper with capacity 128)
and ea98ca1c (uploads through a StagingBelt in the frame's own command buffer). No PR opened.

Builds kept in `bin/_logos_full_fs_*`: `base` master; `time` master with timers around the setup calls
(`fs-time-instrumentation.patch`, never committed); `p3b` the upload change alone on master (prototype, `p3_belt.py
--uniforms`); `vp` = 2de63e42; `all` = ea98ca1c; `allw` = ea98ca1c plus one 4-byte queue.write_buffer a frame
(`allw.patch`). Deleted after use: `stats` (counters, `fs-stats-instrumentation.patch`), prototypes `p1` (viewport
groups kept for the last flush only), `p2` (uniform staging Vec kept across flushes), `p3a` (vertices + indices
through the belt, uniforms still queued: fails the two-flush test).

| file | what |
|---|---|
| `scan.py`, `scan.jsonl`, `files.json` | counter build over 1,267 corpus files, one 1080p frame each: commands, passes, viewport bind groups created, distinct target sizes, staging regrowths, bytes written to the vertex / index / uniform buffers |
| `calls.py`, `measure3.txt` | timer build on master: microseconds a frame in the viewport bind groups, each write_buffer and encoder.finish |
| `rr.py`, `gate.py`, `rr2.txt`, `measure3.txt`, `rr.jsonl` | round-robin timing of base / vp / p3b / all, each round started once the other processes used under 3.5 cores (at most 2 minutes' wait); the CPU the others used is printed beside each file |
| `rr3.txt` | the same for the final binaries (base / vp / all), others at a median 1.9-2.1 cores |
| `allw.txt` | full-screen fills: with one queue write a frame added back, the gain of the two commits together falls to that of each alone; instructions return to master's |
| `mem.py`, `mem.txt` | footprint and graphics memory at the peak, after the frames and 0.5 s later, base vs all |
| `test_assertions.log` | the suite on the final commits, optimized with debug assertions and overflow checks (no disk for a debug tree) |
| `msg1.txt`, `msg2.txt` | the commit messages |
| `rr1_loaded.txt` | the first attempt, at load 23-68; not used |
| `instr.py`, `instr_proto.txt` | instructions and cycles a frame (long run minus short run); `instr_proto.txt` was taken at load 30-60 and its spreads are 4-16 %, see `measure3.txt` for the gated pass |
| `hashes.py`, `hashes_all.txt` | SHA-256 of the second frame, 1,280 files at 1080p and at the 460 x 260 fit, base vs all: 2,560 identical |
| `test_release.log`, `test_debug.log` | `cargo test --features wgpu`: release on the final commits, 564 passed; the debug profile on the earlier version (same upload code, viewport groups kept for the last flush only), 563 passed |
| `p1_viewport.py`, `p2_staging.py`, `p3_belt.py`, `p*.patch` | the prototypes |
