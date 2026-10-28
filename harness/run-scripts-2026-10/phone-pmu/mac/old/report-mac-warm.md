### mac: arm64 iOS 27.2 (26B5091g)

| perf level | name | cores | L1I | L1D | L2 (shared by) |
|---|---|---|---|---|---|
| 0 | Performance | 12 | 192 KiB | 128 KiB | 16384 KiB (6 cores) |
| 1 | Efficiency | 4 | 128 KiB | 64 KiB | 4096 KiB (4 cores) |

cache line 128 B, page 16384 B, RAM 128.0 GiB

#### mac: render-thread counts per pass (thread_selfcounts, E-cores; median frame of passes 1..n, summed over files x zooms)

| phase | variant | instructions/pass | vs master | cycles/pass | vs master | IPC | P-core share | encode share | wall ms/pass | runs spread (instr / cyc) | thermal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| curve | master | 183.9 M | +0.0 % | 101.4 M | +0.0 % | 1.81 | 0.0 % | 93 % | 85 | nan / nan % | ? |
| curve | A (tol 1/16) | 202.8 M | +10.3 % | 124.2 M | +22.5 % | 1.63 | 0.0 % | 93 % | 122 | 0.5 / 2.2 % | ?,? |
| curve | B (straddle) | 186.3 M | +1.3 % | 109.1 M | +7.6 % | 1.71 | 0.0 % | 93 % | 86 | nan / nan % | ? |
| curve | C (straddle + tol 1/8) | 198.0 M | +7.7 % | 120.5 M | +18.9 % | 1.64 | 0.0 % | 92 % | 158 | 3.8 / 12.7 % | ?,? |
| curvehd | master | 73.6 M | +0.0 % | 40.1 M | +0.0 % | 1.84 | 0.0 % | 94 % | 35 | nan / nan % | ? |
| curvehd | A (tol 1/16) | 83.8 M | +13.8 % | 46.2 M | +15.0 % | 1.82 | 0.0 % | 95 % | 39 | 0.3 / 9.6 % | ?,? |
| curvehd | B (straddle) | 74.8 M | +1.6 % | 41.1 M | +2.5 % | 1.82 | 0.0 % | 94 % | 34 | nan / nan % | ? |
| curvehd | C (straddle + tol 1/8) | 79.7 M | +8.2 % | 43.0 M | +7.1 % | 1.85 | 0.0 % | 94 % | 32 | 0.5 / 3.9 % | ?,? |
| busey | master | 837.8 M | +0.0 % | 572.2 M | +0.0 % | 1.46 | 0.0 % | 82 % | 582 | nan / nan % | ? |
| busey | A (tol 1/16) | 853.3 M | +1.9 % | 611.9 M | +6.9 % | 1.39 | 0.1 % | 82 % | 1095 | 1.0 / 9.3 % | ?,? |
| busey | B (straddle) | 841.0 M | +0.4 % | 584.8 M | +2.2 % | 1.44 | 0.0 % | 82 % | 674 | nan / nan % | ? |
| busey | C (straddle + tol 1/8) | 864.6 M | +3.2 % | 696.1 M | +21.7 % | 1.24 | 0.0 % | 82 % | 1886 | 4.2 / 28.8 % | ?,? |
| buseyhd | master | 293.3 M | +0.0 % | 179.8 M | +0.0 % | 1.63 | 0.0 % | 77 % | 280 | nan / nan % | ? |
| buseyhd | A (tol 1/16) | 298.4 M | +1.7 % | 216.9 M | +20.6 % | 1.38 | 0.5 % | 78 % | 236 | 0.9 / 21.7 % | ?,? |
| buseyhd | B (straddle) | 294.0 M | +0.2 % | 193.7 M | +7.7 % | 1.52 | 0.8 % | 77 % | 236 | nan / nan % | ? |
| buseyhd | C (straddle + tol 1/8) | 297.7 M | +1.5 % | 204.5 M | +13.7 % | 1.46 | 0.3 % | 77 % | 302 | 0.8 / 6.2 % | ?,? |

#### mac: cold frames (rep 0, drawn right after another file) vs warm frames, master

| phase | warm instr/pass | cold instr/pass | cold - warm |
|---|---|---|---|
| curve | 183.9 M | 717.5 M | +290 % |
| curvehd | 73.6 M | 587.9 M | +698 % |
| busey | 837.8 M | 1088.4 M | +30 % |
| buseyhd | 293.3 M | 493.9 M | +68 % |

#### mac: per frame, key files (instructions on the render thread, median frame, mean of the runs)

| frame | points m / a / c | master instr | A | B | C | master cycles | A | B | C |
|---|---|---|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | 12735 / 17996 / 15079 | 26.87 M | +13.3 % | +1.6 % | +7.5 % | 10.15 M | +16.3 % | +5.0 % | +10.1 % |
| curvehd c_puzzle-fox z1 | 3983 / 5625 / 4705 | 4.61 M | +23.8 % | +2.0 % | +13.1 % | 2.44 M | +21.8 % | +1.1 % | +11.2 % |
| curvehd c_mr-settodefault z1 | 4981 / 6981 / 5794 | 6.50 M | +19.6 % | +2.4 % | +10.5 % | 3.61 M | +21.3 % | +5.7 % | +8.9 % |
| curvehd c_duckduckgo z1 | 1273 / 2095 / 1814 | 2.40 M | +23.0 % | +1.9 % | +16.1 % | 1.81 M | +25.9 % | +5.1 % | +14.0 % |
| curvehd c_nyt-crossplay z1 | 1729 / 2162 / 1993 | 2.67 M | +10.5 % | +1.4 % | +7.9 % | 1.71 M | +8.6 % | -0.7 % | +2.4 % |
| curve c_tiger z1 | 5872 / 8036 / 6828 | 22.29 M | +7.7 % | +1.1 % | +4.7 % | 8.13 M | +19.3 % | +11.6 % | +14.4 % |
| curve c_tiger z4 | 10917 / 15480 / 13040 | 19.05 M | +12.9 % | +1.8 % | +9.2 % | 7.06 M | +26.8 % | +7.9 % | +23.1 % |
| curvehd svgenius x10 z1 | 10518 / 14607 / 12857 | 16.45 M | +16.7 % | +1.9 % | +11.2 % | 10.92 M | +16.1 % | +1.7 % | +7.8 % |
| curve svgenius x10 z1 | 4971 / 6990 / 5773 | 12.95 M | +11.4 % | +0.9 % | +9.3 % | 8.99 M | +28.0 % | +6.8 % | +19.6 % |

#### mac: cost per flattened point (points per pass from the anatomy probe)

| phase | variant | points/pass | vertices/pass | extra points vs master | extra instr per extra point | extra cycles per extra point |
|---|---|---|---|---|---|---|
| curve | master | 74312 | 349268 | +0 (+0.0 %) | - | - |
| curve | A (tol 1/16) | 102478 | 482788 | +28166 (+37.9 %) | 673 | 809 |
| curve | B (straddle) | 74312 | 349268 | +0 (+0.0 %) | same points; +32 per point | same points; +103 per point |
| curve | C (straddle + tol 1/8) | 86418 | 406279 | +12106 (+16.3 %) | 1166 | 1580 |
| curvehd | master | 37534 | 192464 | +0 (+0.0 %) | - | - |
| curvehd | A (tol 1/16) | 52535 | 270917 | +15001 (+40.0 %) | 678 | 402 |
| curvehd | B (straddle) | 37534 | 192464 | +0 (+0.0 %) | same points; +31 per point | same points; +27 per point |
| curvehd | C (straddle + tol 1/8) | 44941 | 231481 | +7407 (+19.7 %) | 819 | 386 |
| busey | master | 35846 | 160046 | +0 (+0.0 %) | - | - |
| busey | A (tol 1/16) | 48832 | 223478 | +12986 (+36.2 %) | 1195 | 3059 |
| busey | B (straddle) | 35846 | 160046 | +0 (+0.0 %) | same points; +89 per point | same points; +353 per point |
| busey | C (straddle + tol 1/8) | 41580 | 187564 | +5734 (+16.0 %) | 4688 | 21616 |
| buseyhd | master | 17685 | 87579 | +0 (+0.0 %) | - | - |
| buseyhd | A (tol 1/16) | 24265 | 122681 | +6580 (+37.2 %) | 771 | 5628 |
| buseyhd | B (straddle) | 17685 | 87579 | +0 (+0.0 %) | same points; +39 per point | same points; +783 per point |
| buseyhd | C (straddle + tol 1/8) | 21144 | 106197 | +3459 (+19.6 %) | 1255 | 7135 |

#### mac: memory (phys_footprint sampled every 0.2 ms; BuseyBench portraits)

| variant | busey peak (max frame) | busey peak (median of per-frame peaks) | buseyhd peak (max frame) | graphics part at hd peak | lifetime max of the run | footprint after last frame |
|---|---|---|---|---|---|---|
| master | 1318.3 MiB | 1290.0 MiB | 1431.8 MiB | 1304.9 MiB | 1431.8 MiB | 1361.9 MiB |
| A (tol 1/16) | 1320.0 MiB | 1286.7 MiB | 1435.5 MiB | 1305.0 MiB | 1435.5 MiB | 1362.4 MiB |
| B (straddle) | 1315.6 MiB | 1287.4 MiB | 1429.4 MiB | 1304.9 MiB | 1429.4 MiB | 1360.1 MiB |
| C (straddle + tol 1/8) | 1318.6 MiB | 1165.9 MiB | 1431.3 MiB | 1305.0 MiB | 1431.3 MiB | 1359.5 MiB |

