### a14: iPhone13,2 iOS 26.5 (23F77)

| perf level | name | cores | L1I | L1D | L2 (shared by) |
|---|---|---|---|---|---|
| 0 | Performance | 2 | 192 KiB | 128 KiB | 8192 KiB (2 cores) |
| 1 | Efficiency | 4 | 128 KiB | 64 KiB | 4096 KiB (4 cores) |

cache line 128 B, page 16384 B, RAM 3.6 GiB

#### a14: render-thread counts per pass (thread_selfcounts, E-cores; median frame of passes 1..n, summed over files x zooms)

| phase | variant | instructions/pass | vs master | cycles/pass | vs master | IPC | P-core share | encode share | wall ms/pass | runs spread (instr / cyc) | thermal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| curve | master | 174.0 M | +0.0 % | 130.5 M | +0.0 % | 1.33 | 0.0 % | 92 % | 244 | 2.7 / 42.2 % | nominal,nominal,nominal/fair,nominal,nominal,nominal |
| curve | A (tol 1/16) | 192.9 M | +10.9 % | 140.5 M | +7.7 % | 1.37 | 0.0 % | 93 % | 261 | 1.0 / 33.1 % | nominal,nominal,fair,nominal,nominal,nominal |
| curve | B (straddle) | 175.5 M | +0.8 % | 134.4 M | +3.0 % | 1.31 | 0.0 % | 92 % | 250 | 1.7 / 47.3 % | nominal,nominal,fair,nominal,nominal,nominal |
| curve | C (straddle + tol 1/8) | 184.4 M | +6.0 % | 126.0 M | -3.4 % | 1.46 | 0.0 % | 93 % | 269 | 2.1 / 27.2 % | nominal,nominal,fair/nominal,nominal,nominal,nominal |
| curve | pp5 (point costs) | 157.3 M | -9.6 % | 107.3 M | -17.8 % | 1.47 | 0.0 % | 91 % | 261 | 1.4 / 4.0 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curve | pc2 (pp5 + C) | 165.1 M | -5.1 % | 110.9 M | -15.0 % | 1.49 | 0.0 % | 92 % | 266 | 1.5 / 7.9 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curvehd | master | 71.0 M | +0.0 % | 55.3 M | +0.0 % | 1.28 | 0.0 % | 94 % | 216 | 2.5 / 38.8 % | nominal,nominal,nominal/fair,nominal,nominal,nominal |
| curvehd | A (tol 1/16) | 81.7 M | +15.1 % | 59.5 M | +7.7 % | 1.37 | 0.0 % | 94 % | 244 | 1.3 / 55.4 % | nominal,nominal,fair,nominal,nominal,nominal |
| curvehd | B (straddle) | 71.8 M | +1.2 % | 53.7 M | -2.8 % | 1.34 | 0.0 % | 94 % | 218 | 2.0 / 32.4 % | nominal,nominal,fair,nominal,nominal,nominal |
| curvehd | C (straddle + tol 1/8) | 77.4 M | +9.0 % | 54.6 M | -1.3 % | 1.42 | 0.0 % | 94 % | 231 | 1.4 / 31.0 % | nominal,nominal,fair/nominal,nominal,nominal,nominal |
| curvehd | pp5 (point costs) | 61.6 M | -13.1 % | 42.9 M | -22.5 % | 1.44 | 0.0 % | 93 % | 222 | 1.3 / 4.8 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curvehd | pc2 (pp5 + C) | 66.6 M | -6.2 % | 45.6 M | -17.4 % | 1.46 | 0.0 % | 93 % | 228 | 1.7 / 3.5 % | nominal,nominal,nominal,nominal,nominal,nominal |
| busey | master | 872.1 M | +0.0 % | 965.1 M | +0.0 % | 0.90 | 0.0 % | 80 % | 1362 | 2.1 / 24.8 % | nominal,nominal,nominal/fair,nominal,nominal,nominal |
| busey | A (tol 1/16) | 877.2 M | +0.6 % | 936.2 M | -3.0 % | 0.94 | 0.0 % | 81 % | 1270 | 3.1 / 18.0 % | nominal,nominal,fair,nominal,nominal,nominal |
| busey | B (straddle) | 869.3 M | -0.3 % | 921.3 M | -4.5 % | 0.94 | 0.0 % | 81 % | 1380 | 3.3 / 31.0 % | nominal,nominal,fair,nominal,nominal,nominal |
| busey | C (straddle + tol 1/8) | 873.4 M | +0.1 % | 933.5 M | -3.3 % | 0.94 | 0.0 % | 81 % | 1364 | 2.7 / 34.9 % | nominal,nominal,fair/nominal,nominal,nominal,nominal |
| busey | pp5 (point costs) | 862.1 M | -1.2 % | 918.7 M | -4.8 % | 0.94 | 0.0 % | 80 % | 1303 | 2.7 / 22.6 % | nominal,nominal,nominal,nominal,nominal,nominal |
| busey | pc2 (pp5 + C) | 866.2 M | -0.7 % | 935.5 M | -3.1 % | 0.93 | 0.0 % | 80 % | 1325 | 3.4 / 29.7 % | nominal,nominal,nominal,nominal,nominal,nominal |
| buseyhd | master | 292.4 M | +0.0 % | 333.8 M | +0.0 % | 0.88 | 0.0 % | 80 % | 557 | 3.8 / 27.4 % | nominal,nominal,nominal/fair,nominal,nominal,nominal |
| buseyhd | A (tol 1/16) | 294.9 M | +0.8 % | 325.3 M | -2.5 % | 0.91 | 0.0 % | 80 % | 519 | 2.7 / 18.7 % | nominal,nominal,fair,nominal,nominal,nominal |
| buseyhd | B (straddle) | 291.7 M | -0.3 % | 317.9 M | -4.7 % | 0.92 | 0.0 % | 80 % | 590 | 3.5 / 38.4 % | nominal,nominal,fair,nominal,nominal,nominal |
| buseyhd | C (straddle + tol 1/8) | 302.3 M | +3.4 % | 338.7 M | +1.5 % | 0.89 | 0.0 % | 79 % | 723 | 18.0 / 57.8 % | nominal,nominal,fair/nominal,nominal,nominal,nominal |
| buseyhd | pp5 (point costs) | 286.6 M | -2.0 % | 310.9 M | -6.8 % | 0.92 | 0.0 % | 79 % | 530 | 2.9 / 18.6 % | nominal,nominal,nominal,nominal,nominal,nominal |
| buseyhd | pc2 (pp5 + C) | 290.1 M | -0.8 % | 312.9 M | -6.2 % | 0.93 | 0.0 % | 79 % | 553 | 3.1 / 7.2 % | nominal,nominal,nominal,nominal,nominal,nominal |

#### a14: cold frames (rep 0: the first frame of a file, drawn right after another file; pipelines and shaders the previous frame did not use were dropped) vs warm frames (rep >= 1)

| phase | variant | warm instr/pass | cold instr/pass | cold - warm | cold vs master cold | warm cycles/pass | cold cycles/pass | cold cycles vs master cold |
|---|---|---|---|---|---|---|---|---|
| curve | master | 174.0 M | 710.7 M | +308 % | +0.0 % | 130.5 M | 439.1 M | +0.0 % |
| curve | A (tol 1/16) | 192.9 M | 726.3 M | +276 % | +2.2 % | 140.5 M | 444.0 M | +1.1 % |
| curve | B (straddle) | 175.5 M | 708.5 M | +304 % | -0.3 % | 134.4 M | 442.8 M | +0.8 % |
| curve | C (straddle + tol 1/8) | 184.4 M | 718.3 M | +290 % | +1.1 % | 126.0 M | 419.8 M | -4.4 % |
| curve | pp5 (point costs) | 157.3 M | 690.9 M | +339 % | -2.8 % | 107.3 M | 396.3 M | -9.7 % |
| curve | pc2 (pp5 + C) | 165.1 M | 700.4 M | +324 % | -1.5 % | 110.9 M | 400.6 M | -8.8 % |
| curvehd | master | 71.0 M | 588.1 M | +729 % | +0.0 % | 55.3 M | 351.9 M | +0.0 % |
| curvehd | A (tol 1/16) | 81.7 M | 598.9 M | +633 % | +1.8 % | 59.5 M | 351.8 M | -0.0 % |
| curvehd | B (straddle) | 71.8 M | 587.0 M | +718 % | -0.2 % | 53.7 M | 339.3 M | -3.6 % |
| curvehd | C (straddle + tol 1/8) | 77.4 M | 593.6 M | +667 % | +0.9 % | 54.6 M | 337.2 M | -4.2 % |
| curvehd | pp5 (point costs) | 61.6 M | 578.3 M | +838 % | -1.7 % | 42.9 M | 322.1 M | -8.5 % |
| curvehd | pc2 (pp5 + C) | 66.6 M | 585.4 M | +779 % | -0.5 % | 45.6 M | 326.9 M | -7.1 % |
| busey | master | 872.1 M | 1134.4 M | +30 % | +0.0 % | 965.1 M | 1116.7 M | +0.0 % |
| busey | A (tol 1/16) | 877.2 M | 1133.4 M | +29 % | -0.1 % | 936.2 M | 1080.1 M | -3.3 % |
| busey | B (straddle) | 869.3 M | 1130.3 M | +30 % | -0.4 % | 921.3 M | 1074.1 M | -3.8 % |
| busey | C (straddle + tol 1/8) | 873.4 M | 1133.6 M | +30 % | -0.1 % | 933.5 M | 1081.5 M | -3.1 % |
| busey | pp5 (point costs) | 862.1 M | 1118.0 M | +30 % | -1.4 % | 918.7 M | 1063.1 M | -4.8 % |
| busey | pc2 (pp5 + C) | 866.2 M | 1122.9 M | +30 % | -1.0 % | 935.5 M | 1089.8 M | -2.4 % |
| buseyhd | master | 292.4 M | 495.7 M | +70 % | +0.0 % | 333.8 M | 453.2 M | +0.0 % |
| buseyhd | A (tol 1/16) | 294.9 M | 498.1 M | +69 % | +0.5 % | 325.3 M | 450.4 M | -0.6 % |
| buseyhd | B (straddle) | 291.7 M | 498.1 M | +71 % | +0.5 % | 317.9 M | 443.2 M | -2.2 % |
| buseyhd | C (straddle + tol 1/8) | 302.3 M | 508.1 M | +68 % | +2.5 % | 338.7 M | 461.9 M | +1.9 % |
| buseyhd | pp5 (point costs) | 286.6 M | 489.0 M | +71 % | -1.3 % | 310.9 M | 428.6 M | -5.4 % |
| buseyhd | pc2 (pp5 + C) | 290.1 M | 493.1 M | +70 % | -0.5 % | 312.9 M | 425.0 M | -6.2 % |

#### a14: per frame, key files (instructions on the render thread, median frame, mean of the runs)

| frame | points m / a / c | master instr | A | B | C | pp5 | pc2 | master cycles | A | B | C | pp5 | pc2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | 12735 / 17996 / 15079 | 24.27 M | +15.6 % | +1.1 % | +8.3 % | -12.8 % | -6.0 % | 13.27 M | +16.5 % | +0.4 % | +6.5 % | -18.2 % | -11.6 % |
| curvehd c_puzzle-fox z1 | 3983 / 5625 / 4705 | 4.68 M | +24.6 % | +1.7 % | +14.3 % | -20.3 % | -9.4 % | 3.33 M | +12.7 % | -6.2 % | +2.4 % | -29.4 % | -21.4 % |
| curvehd c_mr-settodefault z1 | 4981 / 6981 / 5794 | 6.66 M | +20.9 % | +2.3 % | +11.0 % | -18.2 % | -9.6 % | 5.50 M | +10.5 % | -5.1 % | +0.1 % | -27.4 % | -22.2 % |
| curvehd c_duckduckgo z1 | 1273 / 2095 / 1814 | 2.38 M | +23.7 % | +1.1 % | +18.3 % | -15.0 % | -2.4 % | 2.67 M | +3.7 % | -5.5 % | -4.4 % | -29.5 % | -22.9 % |
| curvehd c_nyt-crossplay z1 | 1729 / 2162 / 1993 | 2.56 M | +11.6 % | +1.7 % | +9.9 % | -16.2 % | -8.1 % | 2.14 M | +2.9 % | -4.2 % | -5.2 % | -27.2 % | -21.5 % |
| curve c_tiger z1 | 5872 / 8036 / 6828 | 19.34 M | +9.5 % | +0.6 % | +5.2 % | -6.8 % | -2.9 % | 9.92 M | +10.1 % | +2.1 % | +1.0 % | -11.6 % | -8.9 % |
| curve c_tiger z4 | 10917 / 15480 / 13040 | 16.67 M | +15.3 % | +1.5 % | +9.5 % | -11.1 % | -3.4 % | 8.78 M | +16.2 % | +4.0 % | +6.1 % | -16.8 % | -9.6 % |
| curvehd svgenius x10 z1 | 10518 / 14607 / 12857 | 16.21 M | +18.3 % | +1.6 % | +12.3 % | -17.5 % | -8.3 % | 14.16 M | +7.6 % | -4.2 % | -4.9 % | -30.3 % | -23.6 % |
| curve svgenius x10 z1 | 4971 / 6990 / 5773 | 12.41 M | +11.2 % | +0.4 % | +5.2 % | -11.3 % | -7.6 % | 10.80 M | +9.3 % | +5.1 % | -8.7 % | -21.7 % | -21.0 % |

#### a14: cost per flattened point (points per pass from the anatomy probe)

| phase | variant | points/pass | vertices/pass | extra points vs master | extra instr per extra point | extra cycles per extra point |
|---|---|---|---|---|---|---|
| curve | master | 74312 | 349268 | +0 (+0.0 %) | - | - |
| curve | A (tol 1/16) | 102478 | 482788 | +28166 (+37.9 %) | 671 | 357 |
| curve | B (straddle) | 74312 | 349268 | +0 (+0.0 %) | same points; +20 per point | same points; +53 per point |
| curve | C (straddle + tol 1/8) | 86418 | 406279 | +12106 (+16.3 %) | 858 | -367 |
| curve | pp5 (point costs) | 74312 | 349268 | +0 (+0.0 %) | same points; -225 per point | same points; -312 per point |
| curve | pc2 (pp5 + C) | 86418 | 406279 | +12106 (+16.3 %) | -737 | -1615 |
| curvehd | master | 37534 | 192464 | +0 (+0.0 %) | - | - |
| curvehd | A (tol 1/16) | 52535 | 270917 | +15001 (+40.0 %) | 715 | 282 |
| curvehd | B (straddle) | 37534 | 192464 | +0 (+0.0 %) | same points; +22 per point | same points; -41 per point |
| curvehd | C (straddle + tol 1/8) | 44941 | 231481 | +7407 (+19.7 %) | 867 | -95 |
| curvehd | pp5 (point costs) | 37534 | 192464 | +0 (+0.0 %) | same points; -249 per point | same points; -331 per point |
| curvehd | pc2 (pp5 + C) | 44941 | 231481 | +7407 (+19.7 %) | -592 | -1300 |
| busey | master | 35846 | 160046 | +0 (+0.0 %) | - | - |
| busey | A (tol 1/16) | 48832 | 223478 | +12986 (+36.2 %) | 392 | -2225 |
| busey | B (straddle) | 35846 | 160046 | +0 (+0.0 %) | same points; -80 per point | same points; -1220 per point |
| busey | C (straddle + tol 1/8) | 41580 | 187564 | +5734 (+16.0 %) | 223 | -5512 |
| busey | pp5 (point costs) | 35846 | 160046 | +0 (+0.0 %) | same points; -280 per point | same points; -1294 per point |
| busey | pc2 (pp5 + C) | 41580 | 187564 | +5734 (+16.0 %) | -1039 | -5153 |
| buseyhd | master | 17685 | 87579 | +0 (+0.0 %) | - | - |
| buseyhd | A (tol 1/16) | 24265 | 122681 | +6580 (+37.2 %) | 371 | -1277 |
| buseyhd | B (straddle) | 17685 | 87579 | +0 (+0.0 %) | same points; -43 per point | same points; -894 per point |
| buseyhd | C (straddle + tol 1/8) | 21144 | 106197 | +3459 (+19.6 %) | 2848 | 1428 |
| buseyhd | pp5 (point costs) | 17685 | 87579 | +0 (+0.0 %) | same points; -328 per point | same points; -1292 per point |
| buseyhd | pc2 (pp5 + C) | 21144 | 106197 | +3459 (+19.6 %) | -677 | -6026 |

#### a14: memory (phys_footprint sampled every 0.2 ms; BuseyBench portraits)

| variant | busey peak (max frame) | busey peak (median of per-frame peaks) | buseyhd peak (max frame) | graphics part at hd peak | lifetime max of the run | footprint after last frame |
|---|---|---|---|---|---|---|
| master | 864.1 MiB | 741.6 MiB | 969.5 MiB | 896.0 MiB | 970.0 MiB | 903.6 MiB |
| A (tol 1/16) | 856.0 MiB | 807.4 MiB | 966.8 MiB | 896.1 MiB | 966.8 MiB | 905.3 MiB |
| B (straddle) | 868.6 MiB | 733.5 MiB | 971.2 MiB | 896.0 MiB | 971.5 MiB | 903.0 MiB |
| C (straddle + tol 1/8) | 855.8 MiB | 784.9 MiB | 969.4 MiB | 896.0 MiB | 969.4 MiB | 901.1 MiB |
| pp5 (point costs) | 852.5 MiB | 797.6 MiB | 966.4 MiB | 895.6 MiB | 966.4 MiB | 903.3 MiB |
| pc2 (pp5 + C) | 852.3 MiB | 797.0 MiB | 966.4 MiB | 895.9 MiB | 966.4 MiB | 900.5 MiB |

#### a14: event mix of the render thread on the E-cores (Instruments counters-profile samples; per 1000 instructions unless noted)


**curve (460x260, z1/2/4)**

| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| master | 97 % | 1.57 | 11.6 % (5.9/2.9/2.7) | 31.4 % | 22.0 % | 13.8 % | 13.30 | 10.64 | 5.07 | 4.261 | 0.283 | 3.13 | 3.18 | 13.8 % | 14.7 % |
| A (tol 1/16) | 96 % | 1.58 | 13.7 % (7.3/3.4/3.0) | 30.1 % | 21.1 % | 13.1 % | 13.29 | 10.92 | 5.07 | 4.114 | 0.266 | 2.85 | 3.03 | 14.1 % | 14.6 % |
| B (straddle) | 83 % | 1.42 | 11.9 % (6.1/3.1/2.8) | 31.5 % | 21.9 % | 13.7 % | 13.65 | 10.85 | 5.11 | 4.492 | 0.273 | 3.12 | 3.11 | 14.0 % | 19.1 % |
| C (straddle + tol 1/8) | 96 % | 1.56 | 13.0 % (6.8/3.3/3.0) | 31.0 % | 21.8 % | 13.5 % | 13.19 | 10.64 | 5.04 | 4.135 | 0.286 | 2.95 | 3.03 | 15.0 % | 14.2 % |
| pp5 (point costs) | 96 % | 1.51 | 10.2 % (5.6/2.4/2.2) | 32.4 % | 22.1 % | 14.0 % | 13.81 | 10.69 | 5.15 | 4.727 | 0.311 | 3.46 | 3.64 | 13.7 % | 17.0 % |
| pc2 (pp5 + C) | 96 % | 1.54 | 12.3 % (7.3/2.6/2.5) | 32.1 % | 21.9 % | 13.9 % | 13.36 | 10.56 | 5.04 | 4.577 | 0.292 | 3.36 | 3.38 | 14.6 % | 15.6 % |

**curvehd (1080p)**

| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| master | 91 % | 1.37 | 14.2 % (7.6/3.5/3.1) | 30.6 % | 21.4 % | 13.0 % | 13.06 | 11.14 | 4.91 | 3.975 | 0.296 | 2.63 | 3.12 | 17.8 % | 15.9 % |
| A (tol 1/16) | 87 % | 1.50 | 16.5 % (9.1/4.0/3.4) | 28.8 % | 20.9 % | 12.6 % | 12.90 | 11.40 | 4.95 | 3.843 | 0.251 | 2.24 | 2.71 | 17.4 % | 12.9 % |
| B (straddle) | 86 % | 1.48 | 14.3 % (7.6/3.6/3.2) | 30.2 % | 22.1 % | 13.4 % | 13.18 | 10.99 | 4.91 | 4.039 | 0.269 | 2.66 | 3.06 | 18.5 % | 13.8 % |
| C (straddle + tol 1/8) | 83 % | 1.37 | 15.6 % (8.4/3.8/3.4) | 29.6 % | 21.8 % | 13.0 % | 13.11 | 11.32 | 4.97 | 3.904 | 0.295 | 2.45 | 3.06 | 19.0 % | 14.9 % |
| pp5 (point costs) | 86 % | 1.31 | 12.7 % (7.4/2.8/2.5) | 32.0 % | 22.1 % | 13.8 % | 13.71 | 11.38 | 5.09 | 4.462 | 0.327 | 3.04 | 3.69 | 17.1 % | 18.0 % |
| pc2 (pp5 + C) | 89 % | 1.35 | 15.6 % (9.7/3.1/2.7) | 30.9 % | 21.8 % | 13.5 % | 13.08 | 10.84 | 4.90 | 4.550 | 0.292 | 2.94 | 3.38 | 18.2 % | 17.3 % |

**busey (both framings)**

| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| master | 87 % | 1.13 | 4.1 % (1.2/1.1/1.8) | 28.3 % | 17.0 % | 10.8 % | 22.92 | 13.81 | 9.43 | 7.570 | 0.394 | 6.32 | 2.27 | 23.6 % | 15.7 % |
| A (tol 1/16) | 75 % | 1.10 | 4.4 % (1.4/1.2/1.8) | 28.3 % | 17.1 % | 10.9 % | 22.35 | 13.85 | 9.17 | 7.227 | 0.337 | 6.11 | 2.22 | 27.2 % | 14.8 % |
| B (straddle) | 77 % | 1.20 | 4.2 % (1.2/1.1/1.8) | 28.4 % | 17.1 % | 10.9 % | 22.76 | 13.69 | 9.28 | 7.513 | 0.377 | 6.32 | 2.28 | 23.0 % | 16.9 % |
| C (straddle + tol 1/8) | 89 % | 1.14 | 4.4 % (1.4/1.2/1.8) | 28.5 % | 17.0 % | 10.8 % | 22.82 | 13.65 | 9.37 | 7.494 | 0.368 | 6.40 | 2.23 | 23.8 % | 16.1 % |
| pp5 (point costs) | 87 % | 1.12 | 3.8 % (1.1/1.0/1.7) | 28.5 % | 17.2 % | 11.0 % | 23.14 | 13.72 | 9.35 | 7.558 | 0.371 | 6.31 | 2.27 | 24.6 % | 15.9 % |
| pc2 (pp5 + C) | 84 % | 1.15 | 4.1 % (1.3/1.1/1.8) | 28.7 % | 17.1 % | 10.9 % | 23.00 | 13.97 | 9.50 | 7.899 | 0.408 | 6.53 | 2.31 | 23.5 % | 16.3 % |

#### a14: L1D misses and SIMD instructions per frame pass, and per extra point (ratios x thread_selfcounts instructions)

| phase | variant | L1D ld misses/pass | L1D st misses/pass | SIMD instr/pass | extra L1D ld misses per extra point | extra SIMD per extra point | extra non-SIMD per extra point |
|---|---|---|---|---|---|---|---|
| curve | master | 2315 k | 1852 k | 20.16 M |  |  |  |
| curve | A (tol 1/16) | 2565 k | 2106 k | 26.49 M | 8.8 | 224.6 | 446.1 |
| curve | B (straddle) | 2396 k | 1903 k | 20.96 M |  |  |  |
| curve | C (straddle + tol 1/8) | 2432 k | 1962 k | 24.00 M | 9.7 | 317.3 | 540.3 |
| curve | pp5 (point costs) | 2172 k | 1682 k | 15.98 M |  |  |  |
| curve | pc2 (pp5 + C) | 2206 k | 1744 k | 20.38 M | -9.0 | 18.5 | -755.0 |
| curvehd | master | 926 k | 790 k | 10.10 M |  |  |  |
| curvehd | A (tol 1/16) | 1054 k | 931 k | 13.50 M | 8.5 | 226.6 | 488.1 |
| curvehd | B (straddle) | 947 k | 789 k | 10.29 M |  |  |  |
| curvehd | C (straddle + tol 1/8) | 1015 k | 876 k | 12.08 M | 11.9 | 267.9 | 599.0 |
| curvehd | pp5 (point costs) | 845 k | 701 k | 7.85 M |  |  |  |
| curvehd | pc2 (pp5 + C) | 871 k | 721 k | 10.37 M | -7.5 | 36.6 | -628.5 |

