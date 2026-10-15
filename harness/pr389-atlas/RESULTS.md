# #389 with scaled-atlas gradient fills, 2026-10-15

The atlas experiment still trades visual accuracy for reuse of glyph masks.
The default-feature accuracy result reproduces the October 12 result. Swash
improves the atlas result against Chromium, but the result remains mixed,
especially against Firefox.

## Sources and validation

The local `demo-assets` mirror includes Matt's
`rebeckerspecialties/demo-assets` at `9d6da07`, merged as `0daebdc` while
preserving our glyph-run text support. This run is on the isolated
`demo-harness/poc2389-2026-10-15` branch. The implementation is on
`demo-harness/poc2389-atlas-2026-10-15` at `da58dfb`.

| Variant | Source |
|---|---|
| master | `9f5ad26` |
| #389 | `828c7a0`, including that master |
| #389 + atlas | `da58dfb`, the saved fills-only PoC applied to `828c7a0` |

Every variant was built with default features plus wgpu, and again with
Swash added. The six builds use identical Cargo.lock files (SHA-256
`6b4f508cd0cdbe4bbd3a705fb582a79f0385f34cc31f19dd3d7a27ea0b64248b`).
Machine: Apple M4 Max, 128 GiB RAM, macOS 26.6.2; rustc 1.96.0, LLVM 22.1.2.
Release builds have debug information disabled. References are software
Chromium 131.0.6778.204 and installed Firefox 158.0.

The atlas patch changes fills only. Gradient/image strokes keep outlines;
large text and unsupported transforms still use #389's corrected outline
path. It introduces no cache-key changes. The harness uses usvg's layout,
so it does not exercise femtovg's shaping-cache keys.

Validation: 564 tests pass with wgpu, 247 library tests pass with wgpu and
Swash, and `cargo fmt --check` passes. The old routing assertions were
updated; #389's outline-paint tests now use text above the atlas size limit.
A new test checks the atlas paint matrix against a path's matrix for both
gradient and image paints, including a nontrivial residual scale.

## Reach

Full corpus: 1,280 SVGs, four framings, six builds = 30,720 successful
renders, no failures. Counts below are per feature set, over 5,120 frames:

| Comparison | Frames changed | Files changed |
|---|---:|---:|
| master -> #389 | 33 | 10 |
| #389 -> #389 + atlas | 9 | 5 |

The counts are the same with Swash. All changed files contain gradient text;
no other corpus file changes. The atlas changes are confined to
`gui-gradient-linear`, `native-canvas`, `gradient-across-runs`,
`gradient-bbox-units`, and `gradient-in-layers` at these four framings.

## Accuracy

All 68 files containing a text element were measured at nine framings,
including reduced sizes and top-pivot zooms: 612 frames per build. Both
browsers captured all 612 references. The six variants rendered all 3,672
frames successfully.

The existing `ab_refs.py` classifies a frame by the change in its share of
pixels more than 20/255 from the browser, with 0.005 percentage points as
the level band. These are counts among frames whose rendered pixels change,
not percentages of the entire corpus.

| Comparison | Reference | Improved | Worsened | Level | Changed frames |
|---|---|---:|---:|---:|---:|
| master -> #389, either feature set | Chromium | 68 | 1 | 8 | 77 |
| master -> #389, either feature set | Firefox | 68 | 1 | 8 | 77 |
| #389 -> atlas, default features | Chromium | 11 | 25 | 2 | 38 |
| #389 -> atlas, default features | Firefox | 11 | 26 | 1 | 38 |
| #389 -> atlas, Swash | Chromium | 25 | 10 | 3 | 38 |
| #389 -> atlas, Swash | Firefox | 14 | 23 | 1 | 38 |

#389's sole worsening is the tiny `gradient-fade` at `z01`: +0.009
percentage points against Chromium, +0.008 against Firefox. No frame
worsens by more than 0.1 points with #389.

The atlas's largest default-feature worsening against Chromium is
`gradient-bbox-units` at `z2`, 2.80% -> 3.43% (+0.637 points). Against
Firefox the same frame goes 0.35% -> 2.40% (+2.052 points). With Swash,
Chromium's worst atlas worsening is `native-canvas` at `z1`,
2.18% -> 2.42% (+0.236 points); Firefox's is `native-canvas` at `z2`,
3.78% -> 4.84% (+1.055 points).
The two references disagree about which mask coverage and placement is
closer, so a result against Chromium alone does not describe the full tradeoff.

Evidence sheets (renderings, both browsers, and each build's differences):

- [master -> #389, defaults](results/m15-p15.png)
- [#389 -> atlas, defaults](results/p15-a15.png)
- [master -> #389, Swash](results/m15sw-p15sw.png)
- [#389 -> atlas, Swash](results/p15sw-a15sw.png)

## CPU work and frame time

Retired instructions per warm frame are measured as
`(run(1200) - run(200)) / 1000`, three alternating pairs, with memory
sampling disabled. They count the whole harness process, including the
renderer and its wait for the GPU; recording/encoding time is measured
separately. All nine measured workloads that take the new atlas route use
fewer instructions in every pair, with either feature set.

| Workload | Framing | #389, M instructions | Atlas, M instructions | Paired change, defaults | Paired change, Swash |
|---|---|---:|---:|---:|---:|
| gui-gradient-linear | hd | 3.207 | 2.139 | -33.28% | -32.96% |
| gui-gradient-linear | z2 | 3.035 | 2.131 | -29.78% | -32.00% |
| native-canvas | z2 | 50.465 | 42.110 | -16.56% | -16.50% |
| gradient-across-runs | z2 | 1.890 | 0.936 | -50.36% | -50.42% |
| gradient-bbox-units | z2 | 1.852 | 0.928 | -49.88% | -49.89% |
| gradient-in-layers | z2 | 3.342 | 2.374 | -28.91% | -28.98% |
| gradient-radial | z05 | 1.350 | 0.891 | -34.07% | -34.09% |
| gradient-fade | z05 | 1.187 | 0.951 | -19.88% | -19.45% |
| gradient-size-threshold | z05 | 1.302 | 0.909 | -30.23% | -29.93% |

The instruction-count columns are the default-feature builds' separate
medians; percentages are medians of within-pair changes. The Swash column
comes from its own paired runs. Strokes and transformed groups that remain
on outlines show no comparable saving.

Wall-clock estimates below exclude the first 20 frames: paired runs of
20 and 220 frames yield the mean of frames 21 through 220, five pairs.
The two time columns are separate medians, so their ratio need not equal the
paired percentage. The wall-time controls vary more than the instruction
counts, and the raw paired ranges are retained.

| Workload | Framing | #389 -> atlas, defaults (ms) | Paired change | #389 -> atlas, Swash (ms) | Paired change |
|---|---|---:|---:|---:|---:|
| gui-gradient-linear | z2 | 0.360 -> 0.277 | -23.1% | 0.391 -> 0.319 | -22.0% |
| gui-gradient-linear | hd | 0.376 -> 0.329 | -13.1% | 0.456 -> 0.357 | -21.9% |
| native-canvas | z2 | 4.808 -> 4.309 | -10.4% | 5.366 -> 4.634 | -12.9% |
| gradient-across-runs | z2 | 0.263 -> 0.193 | -26.5% | 0.274 -> 0.186 | -33.7% |
| gradient-bbox-units | z2 | 0.273 -> 0.201 | -25.4% | 0.288 -> 0.206 | -28.2% |
| gradient-in-layers | z2 | 0.402 -> 0.352 | -19.1% | 0.475 -> 0.381 | -19.8% |

Across all 272 text frames, most of which take the same route on both
builds, the median changes in the 50-frame averages are small:

| Comparison | Median frame time | Median recording/encoding time |
|---|---:|---:|
| master -> #389, defaults | -0.2% | -0.1% |
| #389 -> atlas, defaults | -0.1% | +0.0% |
| master -> #389, Swash | +0.0% | +0.1% |
| #389 -> atlas, Swash | +0.1% | -0.1% |

Those 50-frame averages include the first frame. The subset of eligible
gradient text shows the saving; a corpus-wide average obscures it. The
recorded drifting runs translate the scene by 0.37 pixels per frame.
They keep the scale fixed, so they do not measure the atlas-baking cost of
an animated zoom.

## First draw

The first-frame timer starts after the SVG is parsed and the device and
target exist. It includes first-use font loading, glyph masks and pipelines.
Five alternating pairs:

| Workload | Framing | First frame, defaults (ms) | Paired delta | First frame, Swash (ms) | Paired delta |
|---|---|---:|---:|---:|---:|
| gui-gradient-linear | z2 | 21.359 -> 25.686 | +4.139 ms | 18.167 -> 17.506 | -0.692 ms |
| gui-gradient-linear | hd | 20.975 -> 25.613 | +4.780 ms | 18.328 -> 18.110 | -0.678 ms |
| native-canvas | z2 | 66.066 -> 65.850 | +0.517 ms | 53.504 -> 52.158 | -1.557 ms |
| gradient-bbox-units | z2 | 17.031 -> 19.451 | +2.421 ms | 14.403 -> 13.522 | -0.658 ms |

The Swash improvements at `z2` have the same sign in all five pairs; the
GUI's `hd` row improves in four of five. The default `native-canvas` row has
mixed signs. These are separate
medians and paired deltas, not subtractions of the printed columns.

The independent first-frame instruction measurement, `run(1) - run(0)`
without memory sampling, agrees about the direction on `gui-gradient-linear`
at `z2`: defaults add 50.65 M instructions (117.77 M -> 168.42 M), while
Swash saves 18.32 M (119.37 M -> 101.08 M), by paired median of three runs.
The startup penalty observed without Swash therefore does not describe
the Swash configuration.

## Memory and allocations

Three sequential memory runs cover every text file at the four standard
framings. The following are medians for `z2`; the deltas are paired medians.
Graphics memory is the process's driver-accounted memory, not the bytes of
the glyph masks alone.

| Scene / features | Graphics held after #389 -> atlas (MiB) | Paired delta | Sampled peak process footprint delta |
|---|---:|---:|---:|
| gui-gradient-linear, defaults | 429.203 -> 440.219 | +11.016 MiB | +12.547 MiB |
| gui-gradient-linear, Swash | 429.203 -> 432.234 | +3.031 MiB | +2.938 MiB |
| native-canvas, defaults | 697.000 -> 701.812 | +4.812 MiB | +5.375 MiB |
| native-canvas, Swash | 653.969 -> 646.344 | -7.625 MiB | -9.703 MiB |

The GUI's graphics values are identical in all three repeats. The separate
200-frame diagnostic still holds about 11 MiB extra without Swash and
3 MiB extra with it. The scene matters: `native-canvas` already has atlas
text, and with Swash this change reduces its graphics footprint rather
than increasing it.

Separate counter builds record Rust allocations while frames 2 through 6 are
recorded/encoded. For the gradient GUI at `z2`, both feature sets go from
1,282 to 2,901 allocator calls per frame; this is not an allocation-saving
change on that scene even though it retires fewer instructions. On
`native-canvas` at `z1`, the default builds go from 13,928 to 8,684 calls.
All per-frame allocation counts and requested bytes are retained.

The actual pass counter reports an integer average over six frames. Zeros
in the normal timing logs mean the pass counter was not compiled in; they
do not mean those renders took no passes. Counter builds are separate from
the binaries used for primary timing and instruction measurements.

## Whole-corpus soak and controls

Each soak draws all 1,280 files three times on one canvas at 1080p. All
18 soaks completed, 3,840 frames each. After the first default atlas run
peaked nearly 1 GiB above #389, the whole sequence was repeated twice.
Sampled peak process footprint across the three runs:

| Features | Variant | Median peak (MiB) | Range (MiB) |
|---|---|---:|---:|
| defaults | master | 4,628 | 4,413–4,724 |
| defaults | #389 | 4,663 | 4,470–4,789 |
| defaults | #389 + atlas | 4,938 | 4,707–5,432 |
| Swash | master | 4,715 | 4,554–4,877 |
| Swash | #389 | 4,460 | 4,453–4,739 |
| Swash | #389 + atlas | 4,747 | 4,691–4,825 |

The atlas builds have higher median peaks here, by 275 MiB without Swash
and 287 MiB with it, but the ranges overlap. The first 1 GiB gap does not
repeat at that size. Held memory after each pass varies substantially on
all builds; the CSVs retain it. These are combined harness/library/driver
measurements with the soak script's default transient-image budget, not
an isolated measure of atlas storage or a bound on long-session growth.

Seven-pair comparisons of identical binaries under two names put the
median wall-time noise between -3.4% and +2.7% over the eight control
frames; none has one sign in all seven pairs. This is why small wall-time
changes are not presented as wins. Same-binary Tiger medians are within
0.7% of zero; the original cross-build -15% sample is inconclusive.

The initial three-pair Swash instruction run had an 11.9% decrease on the
pixel-identical `fill-opacity-overlap` control. Seven new pairs put it at
+0.5%; that candidate compared with itself ranges from -12.8% to +14.2%
on this light workload. The initial decrease is not credited to the atlas
change. The other same-binary instruction controls have paired medians
within 0.22% of zero. Rechecking the initial master-to-#389 Swash GUI
outlier gives -0.27% over seven pairs instead of the initial -3.71%.

The instrumented six-frame outputs match uninstrumented six-frame outputs
on the nine strict-hash mismatches found against the single-frame corpus
run. They are repeat-frame changes in
`loading-gltf-model-with-ktx2-textures`, present on master, #389 and the
atlas prototype, rather than changes caused by the counters.

## Scope of this prototype

This reapplies the saved fills-only PoC. It also gives solid scaled-atlas
draws the original canvas paint matrix instead of the residual one. The
solid-color shader ignores that matrix, and solid pixels remain identical
in the full-corpus comparison, but wgpu compares the whole uniform array
when deciding whether to reuse uniforms. This run does not separately
isolate resource/cache effects of those changed, unused matrix values.

The atlas mask keys are upstream's; #384's negative-x key fix is not part
of any variant. Image paint is covered by the paint-matrix unit test,
not by a new image-painted-text raster corpus. The old standalone
spike/paint-model sweep was not repeated. The evidence sheets and the
complete text corpus are the visual evidence for this run. Measurements
are from this M4 Max; neither low-end hardware nor a continuously changing
zoom is measured here.

## OpenGL

The existing OpenGL clip check passes on all three default-feature builds.
`gl_dump_ab.py` draws the 68 text files at scales 0.1953125, 1, 2 and 3:
272 dumps per build. For #389 -> atlas, 270 dumps are identical and two
differ, both in `gui-gradient-linear`. This tool omits SVG clips, masks,
filters and group opacity, so its results describe the text path rather
than a browser-conformance comparison. OpenGL performance and Swash OpenGL
builds are outside this run.

## Reproduction and raw data

[README.md](README.md) describes the existing scripts, source layout and
commands. `results/manifest.json` records source revisions and the machine;
`results/binary-sha256.json` identifies the six normal binaries.
`results/accuracy.jsonl` and `results/pixels.jsonl` retain every frame, and
the `results/logs/accuracy_compare_*.log` files retain the existing harness's
comparison output. The `results/png` and `results/refs` directories retain
rendered frames and references.
