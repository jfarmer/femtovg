# CPU counters on the efficiency cores: M4 Max and the A15 Apple TV

Tools from the thin-fill masks work (femtovg/femtovg#408): what a change costs on
the efficiency cores in cycles, instructions, L1D misses, branch mispredicts,
peak footprint and, on the TV, GPU time and partial renders. The scripts keep the
absolute paths of the machine they ran on (`~/src/femtovg-wt/...`,
`~/src/femtovg-pmu`); adjust them before running elsewhere.

- `femtovg-events.tracetemplate`: Instruments' CPU Counters in manual mode,
  sampling every millisecond with the user stack: `BRANCH_MISPRED_NONSPEC`,
  `L1D_CACHE_MISS_LD`, `L1I_CACHE_MISS_DEMAND`, instructions, cycles,
  `INST_BRANCH`, `L1D_CACHE_MISS_ST`, `L1D_TLB_MISS`. It is the CPU
  Bottlenecks template with its options' JSON switched to
  `configurationType: {manual: {}}` (the events were already listed in it). Use
  `xcrun xctrace record --template femtovg-events.tracetemplate --launch --
  /usr/sbin/taskpolicy -c background BINARY ...` for the efficiency cores on the
  Mac, `--device UDID ... --launch -- BUNDLE_ID` on a device.
- `pmc_agg.py EXPORT.xml PROCESS 'pattern|...'`: totals of the
  `counters-profile` table per core type and per function whose stack matches;
  `LEAVES=n` adds the n costliest leaf functions, `FOCUS=pattern` only within
  stacks holding it. Sampled totals vary between recordings by up to a quarter:
  compare rates (misses a thousand instructions, mispredicts a thousand
  branches), and take exact counts from the thread's own counters.
- `add_bench.py WORKTREE REV`: adds to a femtovg worktree, for a build that is
  not committed, the ignored test `zz_raster_bench`, which rasterizes the masks
  of a capture (`FILL_MASK_DUMP`, see the patch it describes) and prints the
  thread's exact instructions and cycles a pass per CPU kind
  (`thread_selfcounts`); `RASTER_IMPL=old` runs REV's rasterizer in the same
  binary. `ab.sh SET ITERS ROUNDS` alternates old and new on the efficiency and
  the performance cores; `ab2.sh` two binaries; `rec.sh` records one with the
  template.
- `e2e.py BUILD... -- KEY:FRAMING...`: harness frames in motion (`FRAME_DRIFT`),
  instructions and cycles a frame from the difference of a long and a short run
  under `taskpolicy -c background`, and the peak footprint (`MEM_PEAKS`).
  `pass_time.py`'s 20-frame time includes the first frame's pipeline compiles
  and atlas creation; time suspects at 200 frames.
- `tv/`: the A15 Apple TV ("team h") runs of the femtovg-pmu app's `thin` and
  `thinhd` phases (eight thin-fill files, moving): `run_thin.sh` under the
  template (per-frame CSV: the render thread's efficiency-core instructions and
  cycles, peak footprint and its graphics part), `run_gpu.sh` under GPU and
  Metal GPU Counters (`../../runs/clearload/scripts/frames.py`: GPU time,
  bandwidth, partial renders), `tv_table.py` the table, `wait_wake.sh` the wait
  for a TV that went to sleep - a sleeping tvOS forbids launching an app
  ("System is asleep - foreground app launch forbidden"), and only the remote
  wakes it.

The device app needs `NO_THIN_FILL_MASKS` handled in its own canvas set-up
(the harness's `main` is not run there), the harness's memory sampler built for
`target_os = "tvos"`, and the frame counter advanced per frame for
`FRAME_DRIFT`; build-harness.sh and lib.rs in femtovg-pmu have all three.
- `ios/`: the iPhone 16 Pro Max (A18 Pro), paired over Wi-Fi, where one counters
  recording of a 7 s run takes about seven minutes. `run_fast.sh` launches the
  app with `devicectl --console` (14 s a run) and fetches its soak CSV, whose
  rows carry the render thread's exact instructions and cycles per CPU kind,
  the process's, its energy (`task_energy_nj`) and the peak footprint;
  `round.sh N` runs the six variants (#408, + belt, + image staging, each with
  the masks on and off) forward and back; `ios_table.py` the table;
  `run_thin.sh` one run under the events template; `run_gpu.sh`,
  `gpu_round.sh` and `gpu_table.py` GPU time per frame (the A18 Pro's default
  Metal GPU Counters set has no bandwidth or partial renders).
- `m4belt/`: the M4's efficiency cores under the events template, harness
  frames in motion: `rec.sh BUILD FILE TAG [off]` writes the whole recording's
  counters and, with `pmc_agg.py`'s `ONLY=render_scene|flush_to_output|::submit`,
  the frame loop's alone (`pmcf-*`; sampled totals of a whole run mix in the
  start-up and varied by twice between recordings); `m4_table.py` and
  `m4f_table.py` the rates and shares.

`../corpus_run/area_changed.py BEFORE AFTER` scores only the frames
`identity.py` found to differ against the area reference, where `area_ab.py`
renders every frame that has one.
