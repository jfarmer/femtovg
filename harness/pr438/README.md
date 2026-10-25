# femtovg#438 (premultiplied gradient interpolation): cost of the LUT routing, 2026-10-25

`zz_gradient_premul_bench_wgpu.rs` (copy into tests/ of the PR, c2b9b7ee): N fading two-stop linear gradients
(opaque hue -> same hue at alpha 0, or an alpha that changes every frame), wgpu headless on M4 E-cores
(`taskpolicy -c background`), 1000x1000 target. Render-thread instructions/cycles from thread_selfcounts (median
frame), CPU energy from rusage_info_v6 ri_energy_nj, footprint ri_phys_footprint. GPU time did not register
(task_power_info_v2 gpu utilisation 0).

| N, scene | mode | instr/frame | cycles/frame | CPU mJ/frame | footprint |
|---|---|---:|---:|---:|---:|
| 500 static | straight (two-stop shader) | 13.0 M | 4.45 M | 0.67 | 458.7 MB |
| 500 static | premultiplied (LUT) | 23.3 M | 10.1 M | 1.40 | 462.7 MB |
| 500 animated | straight | 13.0 M | 4.45 M | 0.67 | 461.8 MB |
| 500 animated | premultiplied | 61.1 M | 31.0 M | 3.75 | 464.4 MB |
| 5000 animated | straight | 129.7 M | 43.1 M | 6.52 | 644.9 MB peak |
| 5000 animated | premultiplied | 622.1 M | 346.1 M | 42.7 | 712.9 MB peak |

Two rounds agree within 2 %. Accuracy (`zz_gradient_premul_accuracy`, white -> transparent white over black,
1024 px): LUT path max 1/255, mean 0.34/255 against the exact ramp; two-stop shader max 1/255, mean 0.13/255.
