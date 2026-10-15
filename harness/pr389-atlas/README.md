# Gradient fills from the scaled atlas on #389

This repeats the October 12 fills-only atlas prototype on current master and
current #389, using the local demo-assets mirror after merging Matt's
rebeckerspecialties/demo-assets at `9d6da07`.

| Binary | Source | Features |
|---|---|---|
| `m15` | master `9f5ad26` | defaults + wgpu |
| `p15` | #389 `828c7a0` | defaults + wgpu |
| `a15` | #389 `828c7a0` + fills-only atlas patch | defaults + wgpu |
| `m15sw`, `p15sw`, `a15sw` | the same three trees | defaults + wgpu + swash |

All binaries use one Cargo target directory, the same resolved dependencies,
and release builds with debug information disabled. Every build has
`harness_text`, so text reaches femtovg's glyph-run renderer. usvg supplies
the glyph layout; these runs do not exercise femtovg's shaping-cache keys.
Unregistered build names keep the environment identical, including
`SINGLE_SHADOW_LAYER=1`. No additional text rasterization or cache-key fix is
part of the atlas prototype. Gradient/image strokes retain the outline path.

The prototype updates the two routing tests from the old experiment and
keeps #389's outline-paint tests above the atlas size limit. A new test checks
that both gradient and image fills through the scaled atlas retain the paint
matrix of an ordinary path, including a scale with a nontrivial residual.

## Scripts reused

- `corpus_run/files.py`: enumerate the corpus and retain its stable keys.
- `corpus_run/refs.py`: software Chromium 131 and the installed Firefox.
- `corpus_run/accuracy.py`, `ab_refs.py`, `sheet.py`: reference comparisons,
  changed-frame summaries and evidence images.
- `corpus_run/run.py pixels`: full-corpus hashes for all six builds.
- `corpus_run/pass_time.py`: alternating paired timing, before-submit CPU
  time, first-frame timing, and scenes drifting by 0.37 pixels per frame.
- The October 12 `text-atlas-poc/perf/check/interleaved.py`, copied into
  `tools/` with only import and temporary-file paths changed: paired warm
  instruction counts, `(run(1200) - run(200)) / 1000`, without memory sampling.
- `corpus_run/run.py memory`: sequential memory and optional allocator
  diagnostics. The two ALLOC fields preserve counters the harness already
  emitted.
- `corpus_run/soak.py`: three passes over the whole corpus on one canvas.
- `corpus_run/pass_count.py`: temporary pass-counter instrumentation, reverted
  after each separate instrumented build. Allocator/pass measurements use
  separate binaries and are excluded from the primary performance results.

`build.sh` accepts an optional `HARNESS_FEATURES` variable to use the same
builder for both feature sets. It still defaults to `wgpu`.

## Run

`run.py` orchestrates these existing scripts. `POC_RUN_DIR` must contain
`src/master`, `src/p389`, `src/poc2389`, `bin` and a shared `target` directory.
Its `results` directory holds raw data and logs. Each stage is explicit:

```sh
export POC_RUN_DIR=/private/tmp/femtovg-pr389-atlas-repeat
git worktree add --detach "$POC_RUN_DIR/src/master" 9f5ad26
git worktree add --detach "$POC_RUN_DIR/src/p389" 828c7a0
git worktree add --detach "$POC_RUN_DIR/src/poc2389" da58dfb
cp harness/pr389-atlas/Cargo.lock.snapshot "$POC_RUN_DIR/src/master/Cargo.lock"
cp harness/pr389-atlas/Cargo.lock.snapshot "$POC_RUN_DIR/src/p389/Cargo.lock"
cp harness/pr389-atlas/Cargo.lock.snapshot "$POC_RUN_DIR/src/poc2389/Cargo.lock"
export HARNESS_BIN="$POC_RUN_DIR/bin"
export CARGO_TARGET_DIR="$POC_RUN_DIR/target"
export CARGO_PROFILE_RELEASE_DEBUG=0
bash harness/build.sh "m15:$POC_RUN_DIR/src/master" "p15:$POC_RUN_DIR/src/p389" "a15:$POC_RUN_DIR/src/poc2389"
python3 harness/pr389-atlas/run.py setup smoke build-swash smoke
python3 harness/pr389-atlas/run.py tests refs
python3 harness/pr389-atlas/run.py pixels accuracy comparisons
python3 harness/pr389-atlas/run.py perf instructions memory soak counters
python3 harness/pr389-atlas/run.py timing-summary figures
python3 harness/pr389-atlas/run.py history-check timing-noise
python3 harness/pr389-atlas/run.py soak-repeats
POC_RESULTS="$POC_RUN_DIR/results" python3 harness/pr389-atlas/summarize.py
```

The `setup` stage also copies the previous instruction-count script from the
saved October 12 investigation in the sibling femtovg-demo-assets checkout.
Once `tools/interleaved.py` exists, the measurements do not need that copy.
`setup` can also reuse the saved helpers when the old investigation is absent.
Reference captures and corpus comparisons may overlap; performance runs are
sequential and begin only after builds, tests and captures have finished.
The paired-analysis helper retains its original `mbase` and `poc` field
names for the before and after samples; the filename identifies the actual
build pair. `timing-noise` compares a binary with an identical alias, and
`history-check` separates repeat-frame changes from counter instrumentation.

The primary accuracy set is every corpus SVG containing a text element at
nine framings: `z01,z025,z05,z1,z2,z4,zt2,zt4,hd`. The full-corpus hash check
uses `z1,z2,z4,hd`. Timing covers every text file at those four framings,
with additional cold/short/long/drifting samples on all gradient-text files
and solid/no-text controls. Raw samples and complete per-frame results are
retained so averages cannot hide regressions.
