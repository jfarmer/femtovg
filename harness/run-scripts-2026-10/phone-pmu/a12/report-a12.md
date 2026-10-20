### a12: iPhone11,6 iOS 18.7.10 (22H374)

| perf level | name | cores | L1I | L1D | L2 (shared by) |
|---|---|---|---|---|---|
| 0 | Performance | 2 | 128 KiB | 128 KiB | 8192 KiB (2 cores) |
| 1 | Efficiency | 4 | 48 KiB | 32 KiB | 2048 KiB (4 cores) |

cache line 128 B, page 16384 B, RAM 3.7 GiB

#### a12: render-thread counts per pass (thread_selfcounts, E-cores; median frame of passes 1..n, summed over files x zooms)

| phase | variant | instructions/pass | vs master | cycles/pass | vs master | IPC | P-core share | encode share | wall ms/pass | runs spread (instr / cyc) | thermal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| curve | master | 167.5 M | +0.0 % | 212.9 M | +0.0 % | 0.79 | 0.0 % | 91 % | 487 | 0.5 / 11.4 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curve | A (tol 1/16) | 186.9 M | +11.6 % | 234.0 M | +9.9 % | 0.80 | 0.0 % | 92 % | 571 | 3.6 / 10.3 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curve | B (straddle) | 169.2 M | +1.0 % | 212.8 M | -0.0 % | 0.80 | 0.0 % | 91 % | 513 | 0.6 / 1.3 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curve | C (straddle + tol 1/8) | 177.9 M | +6.2 % | 220.4 M | +3.6 % | 0.81 | 0.0 % | 92 % | 531 | 0.9 / 1.8 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curve | pp5 (point costs) | 151.0 M | -9.9 % | 194.3 M | -8.7 % | 0.78 | 0.0 % | 90 % | 481 | 0.8 / 3.2 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curve | pc2 (pp5 + C) | 159.4 M | -4.9 % | 205.9 M | -3.3 % | 0.77 | 0.0 % | 91 % | 496 | 0.6 / 11.9 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curvehd | master | 70.9 M | +0.0 % | 89.0 M | +0.0 % | 0.80 | 0.0 % | 90 % | 412 | 1.5 / 16.7 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curvehd | A (tol 1/16) | 81.4 M | +14.8 % | 98.4 M | +10.6 % | 0.83 | 0.0 % | 91 % | 436 | 2.6 / 9.5 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curvehd | B (straddle) | 71.9 M | +1.5 % | 89.2 M | +0.3 % | 0.81 | 0.0 % | 90 % | 417 | 1.3 / 7.5 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curvehd | C (straddle + tol 1/8) | 77.0 M | +8.6 % | 93.2 M | +4.7 % | 0.83 | 0.0 % | 91 % | 424 | 0.7 / 1.4 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curvehd | pp5 (point costs) | 61.6 M | -13.1 % | 77.8 M | -12.6 % | 0.79 | 0.0 % | 89 % | 392 | 0.6 / 5.2 % | nominal,nominal,nominal,nominal,nominal,nominal |
| curvehd | pc2 (pp5 + C) | 66.7 M | -5.9 % | 83.4 M | -6.3 % | 0.80 | 0.0 % | 90 % | 402 | 0.8 / 2.9 % | nominal,nominal,nominal,nominal,nominal,nominal |
| busey | master | 792.6 M | +0.0 % | 1403.3 M | +0.0 % | 0.56 | 0.0 % | 80 % | 1639 | 0.9 / 4.5 % | nominal,nominal,nominal,nominal,nominal,nominal |
| busey | A (tol 1/16) | 802.0 M | +1.2 % | 1417.6 M | +1.0 % | 0.57 | 0.0 % | 80 % | 1620 | 1.0 / 2.0 % | nominal,nominal,nominal,nominal,nominal,nominal |
| busey | B (straddle) | 793.5 M | +0.1 % | 1412.6 M | +0.7 % | 0.56 | 0.0 % | 80 % | 1615 | 1.5 / 6.9 % | nominal,nominal,nominal,nominal,nominal,nominal |
| busey | C (straddle + tol 1/8) | 795.3 M | +0.3 % | 1399.0 M | -0.3 % | 0.57 | 0.0 % | 80 % | 1617 | 0.5 / 1.5 % | nominal,nominal,nominal,nominal,nominal,nominal |
| busey | pp5 (point costs) | 786.9 M | -0.7 % | 1388.5 M | -1.1 % | 0.57 | 0.0 % | 80 % | 1594 | 0.6 / 2.6 % | nominal,nominal,nominal,nominal,nominal,nominal |
| busey | pc2 (pp5 + C) | 787.9 M | -0.6 % | 1389.1 M | -1.0 % | 0.57 | 0.0 % | 80 % | 1612 | 0.8 / 2.0 % | nominal,nominal,nominal,nominal,nominal,nominal |
| buseyhd | master | 286.2 M | +0.0 % | 454.9 M | +0.0 % | 0.63 | 0.0 % | 75 % | 1186 | 1.4 / 12.2 % | nominal,nominal,nominal,nominal,nominal,nominal |
| buseyhd | A (tol 1/16) | 289.7 M | +1.2 % | 453.0 M | -0.4 % | 0.64 | 0.0 % | 75 % | 1170 | 0.5 / 4.8 % | nominal,nominal,nominal,nominal,nominal,nominal |
| buseyhd | B (straddle) | 286.0 M | -0.1 % | 448.0 M | -1.5 % | 0.64 | 0.0 % | 75 % | 1184 | 0.7 / 4.5 % | nominal,nominal,nominal,nominal,nominal,nominal |
| buseyhd | C (straddle + tol 1/8) | 287.7 M | +0.5 % | 447.3 M | -1.7 % | 0.64 | 0.0 % | 75 % | 1198 | 1.0 / 6.4 % | nominal,nominal,nominal,nominal,nominal,nominal |
| buseyhd | pp5 (point costs) | 282.2 M | -1.4 % | 442.6 M | -2.7 % | 0.64 | 0.0 % | 75 % | 1177 | 0.7 / 1.0 % | nominal,nominal,nominal,nominal,nominal,nominal |
| buseyhd | pc2 (pp5 + C) | 283.4 M | -1.0 % | 447.3 M | -1.7 % | 0.63 | 0.0 % | 75 % | 1173 | 0.7 / 3.4 % | nominal,nominal,nominal,nominal,nominal,nominal |

#### a12: cold frames (rep 0: the first frame of a file, drawn right after another file; pipelines and shaders the previous frame did not use were dropped) vs warm frames (rep >= 1)

| phase | variant | warm instr/pass | cold instr/pass | cold - warm | cold vs master cold | warm cycles/pass | cold cycles/pass | cold cycles vs master cold |
|---|---|---|---|---|---|---|---|---|
| curve | master | 167.5 M | 718.3 M | +329 % | +0.0 % | 212.9 M | 680.6 M | +0.0 % |
| curve | A (tol 1/16) | 186.9 M | 740.7 M | +296 % | +3.1 % | 234.0 M | 707.7 M | +4.0 % |
| curve | B (straddle) | 169.2 M | 716.3 M | +323 % | -0.3 % | 212.8 M | 674.5 M | -0.9 % |
| curve | C (straddle + tol 1/8) | 177.9 M | 727.2 M | +309 % | +1.2 % | 220.4 M | 683.4 M | +0.4 % |
| curve | pp5 (point costs) | 151.0 M | 702.2 M | +365 % | -2.3 % | 194.3 M | 658.0 M | -3.3 % |
| curve | pc2 (pp5 + C) | 159.4 M | 705.6 M | +343 % | -1.8 % | 205.9 M | 669.3 M | -1.7 % |
| curvehd | master | 70.9 M | 606.8 M | +756 % | +0.0 % | 89.0 M | 545.3 M | +0.0 % |
| curvehd | A (tol 1/16) | 81.4 M | 615.4 M | +656 % | +1.4 % | 98.4 M | 547.5 M | +0.4 % |
| curvehd | B (straddle) | 71.9 M | 604.1 M | +740 % | -0.4 % | 89.2 M | 538.2 M | -1.3 % |
| curvehd | C (straddle + tol 1/8) | 77.0 M | 607.5 M | +689 % | +0.1 % | 93.2 M | 535.7 M | -1.8 % |
| curvehd | pp5 (point costs) | 61.6 M | 596.9 M | +869 % | -1.6 % | 77.8 M | 525.5 M | -3.6 % |
| curvehd | pc2 (pp5 + C) | 66.7 M | 598.6 M | +798 % | -1.4 % | 83.4 M | 529.4 M | -2.9 % |
| busey | master | 792.6 M | 1056.2 M | +33 % | +0.0 % | 1403.3 M | 1656.8 M | +0.0 % |
| busey | A (tol 1/16) | 802.0 M | 1065.2 M | +33 % | +0.9 % | 1417.6 M | 1662.5 M | +0.3 % |
| busey | B (straddle) | 793.5 M | 1057.4 M | +33 % | +0.1 % | 1412.6 M | 1665.2 M | +0.5 % |
| busey | C (straddle + tol 1/8) | 795.3 M | 1057.5 M | +33 % | +0.1 % | 1399.0 M | 1641.7 M | -0.9 % |
| busey | pp5 (point costs) | 786.9 M | 1050.0 M | +33 % | -0.6 % | 1388.5 M | 1637.0 M | -1.2 % |
| busey | pc2 (pp5 + C) | 787.9 M | 1051.3 M | +33 % | -0.5 % | 1389.1 M | 1636.9 M | -1.2 % |
| buseyhd | master | 286.2 M | 498.7 M | +74 % | +0.0 % | 454.9 M | 650.9 M | +0.0 % |
| buseyhd | A (tol 1/16) | 289.7 M | 501.1 M | +73 % | +0.5 % | 453.0 M | 647.7 M | -0.5 % |
| buseyhd | B (straddle) | 286.0 M | 497.5 M | +74 % | -0.2 % | 448.0 M | 641.7 M | -1.4 % |
| buseyhd | C (straddle + tol 1/8) | 287.7 M | 498.2 M | +73 % | -0.1 % | 447.3 M | 642.9 M | -1.2 % |
| buseyhd | pp5 (point costs) | 282.2 M | 493.4 M | +75 % | -1.1 % | 442.6 M | 636.9 M | -2.1 % |
| buseyhd | pc2 (pp5 + C) | 283.4 M | 494.1 M | +74 % | -0.9 % | 447.3 M | 633.8 M | -2.6 % |

#### a12: per frame, key files (instructions on the render thread, median frame, mean of the runs)

| frame | points m / a / c | master instr | A | B | C | pp5 | pc2 | master cycles | A | B | C | pp5 | pc2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | 12735 / 17996 / 15079 | 23.85 M | +15.4 % | +1.5 % | +8.2 % | -13.1 % | -5.9 % | 22.29 M | +14.5 % | +2.0 % | +7.6 % | -13.3 % | -5.3 % |
| curvehd c_puzzle-fox z1 | 3983 / 5625 / 4705 | 4.58 M | +25.0 % | +2.6 % | +13.5 % | -20.3 % | -9.0 % | 5.29 M | +21.5 % | +3.0 % | +10.7 % | -19.4 % | -10.0 % |
| curvehd c_mr-settodefault z1 | 4981 / 6981 / 5794 | 6.68 M | +20.5 % | +2.3 % | +10.8 % | -17.2 % | -9.0 % | 8.31 M | +15.0 % | +1.6 % | +7.8 % | -15.4 % | -9.1 % |
| curvehd c_duckduckgo z1 | 1273 / 2095 / 1814 | 2.64 M | +21.4 % | +0.9 % | +15.6 % | -12.2 % | -1.2 % | 4.27 M | +13.7 % | -0.5 % | +7.6 % | -10.4 % | -2.8 % |
| curvehd c_nyt-crossplay z1 | 1729 / 2162 / 1993 | 2.52 M | +12.2 % | +1.6 % | +9.1 % | -16.8 % | -8.2 % | 3.45 M | +6.7 % | -2.2 % | +2.0 % | -16.9 % | -9.5 % |
| curve c_tiger z1 | 5872 / 8036 / 6828 | 18.90 M | +10.1 % | +0.8 % | +5.2 % | -7.0 % | -3.0 % | 16.89 M | +13.1 % | +1.8 % | +6.2 % | -4.9 % | -0.4 % |
| curve c_tiger z4 | 10917 / 15480 / 13040 | 16.33 M | +15.8 % | +1.8 % | +9.5 % | -11.0 % | -3.1 % | 14.79 M | +19.1 % | +3.1 % | +11.2 % | -13.0 % | -2.5 % |
| curvehd svgenius x10 z1 | 10518 / 14607 / 12857 | 15.86 M | +18.2 % | +1.8 % | +12.0 % | -17.9 % | -8.2 % | 23.77 M | +11.1 % | -1.1 % | +3.9 % | -16.8 % | -9.6 % |
| curve svgenius x10 z1 | 4971 / 6990 / 5773 | 11.95 M | +12.3 % | +0.9 % | +5.8 % | -11.3 % | -6.3 % | 18.33 M | +7.8 % | -2.4 % | +0.5 % | -10.1 % | -3.9 % |

#### a12: cost per flattened point (points per pass from the anatomy probe)

| phase | variant | points/pass | vertices/pass | extra points vs master | extra instr per extra point | extra cycles per extra point |
|---|---|---|---|---|---|---|
| curve | master | 74312 | 349268 | +0 (+0.0 %) | - | - |
| curve | A (tol 1/16) | 102478 | 482788 | +28166 (+37.9 %) | 688 | 749 |
| curve | B (straddle) | 74312 | 349268 | +0 (+0.0 %) | same points; +23 per point | same points; -1 per point |
| curve | C (straddle + tol 1/8) | 86418 | 406279 | +12106 (+16.3 %) | 852 | 625 |
| curve | pp5 (point costs) | 74312 | 349268 | +0 (+0.0 %) | same points; -222 per point | same points; -249 per point |
| curve | pc2 (pp5 + C) | 86418 | 406279 | +12106 (+16.3 %) | -676 | -572 |
| curvehd | master | 37534 | 192464 | +0 (+0.0 %) | - | - |
| curvehd | A (tol 1/16) | 52535 | 270917 | +15001 (+40.0 %) | 698 | 629 |
| curvehd | B (straddle) | 37534 | 192464 | +0 (+0.0 %) | same points; +28 per point | same points; +6 per point |
| curvehd | C (straddle + tol 1/8) | 44941 | 231481 | +7407 (+19.7 %) | 826 | 569 |
| curvehd | pp5 (point costs) | 37534 | 192464 | +0 (+0.0 %) | same points; -247 per point | same points; -298 per point |
| curvehd | pc2 (pp5 + C) | 44941 | 231481 | +7407 (+19.7 %) | -570 | -752 |
| busey | master | 35846 | 160046 | +0 (+0.0 %) | - | - |
| busey | A (tol 1/16) | 48832 | 223478 | +12986 (+36.2 %) | 722 | 1099 |
| busey | B (straddle) | 35846 | 160046 | +0 (+0.0 %) | same points; +24 per point | same points; +257 per point |
| busey | C (straddle + tol 1/8) | 41580 | 187564 | +5734 (+16.0 %) | 461 | -751 |
| busey | pp5 (point costs) | 35846 | 160046 | +0 (+0.0 %) | same points; -161 per point | same points; -413 per point |
| busey | pc2 (pp5 + C) | 41580 | 187564 | +5734 (+16.0 %) | -824 | -2488 |
| buseyhd | master | 17685 | 87579 | +0 (+0.0 %) | - | - |
| buseyhd | A (tol 1/16) | 24265 | 122681 | +6580 (+37.2 %) | 533 | -297 |
| buseyhd | B (straddle) | 17685 | 87579 | +0 (+0.0 %) | same points; -12 per point | same points; -390 per point |
| buseyhd | C (straddle + tol 1/8) | 21144 | 106197 | +3459 (+19.6 %) | 446 | -2207 |
| buseyhd | pp5 (point costs) | 17685 | 87579 | +0 (+0.0 %) | same points; -227 per point | same points; -700 per point |
| buseyhd | pc2 (pp5 + C) | 21144 | 106197 | +3459 (+19.6 %) | -815 | -2204 |

#### a12: memory (phys_footprint sampled every 0.2 ms; BuseyBench portraits)

| variant | busey peak (max frame) | busey peak (median of per-frame peaks) | buseyhd peak (max frame) | graphics part at hd peak | lifetime max of the run | footprint after last frame |
|---|---|---|---|---|---|---|
| master | 672.1 MiB | 578.2 MiB | 786.4 MiB | 715.2 MiB | 787.0 MiB | 642.8 MiB |
| A (tol 1/16) | 673.9 MiB | 571.8 MiB | 785.4 MiB | 715.3 MiB | 785.4 MiB | 641.7 MiB |
| B (straddle) | 667.5 MiB | 578.8 MiB | 781.3 MiB | 715.2 MiB | 781.3 MiB | 637.6 MiB |
| C (straddle + tol 1/8) | 670.3 MiB | 594.7 MiB | 782.6 MiB | 715.2 MiB | 782.6 MiB | 638.9 MiB |
| pp5 (point costs) | 667.5 MiB | 592.3 MiB | 780.6 MiB | 714.8 MiB | 780.6 MiB | 637.1 MiB |
| pc2 (pp5 + C) | 669.2 MiB | 583.0 MiB | 782.6 MiB | 715.1 MiB | 782.6 MiB | 639.0 MiB |

#### a12: event mix of the render thread on the E-cores (Instruments counters-profile samples; per 1000 instructions unless noted)


**curve (460x260, z1/2/4)**

| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| master | 82 % | 0.75 | 5.5 % (0.0/2.9/2.6) | 0.0 % | 20.9 % | 13.3 % | 20.30 | 10.59 | 6.19 | 3.825 | 0.558 | 6.83 | 6.01 | 15.3 % | 19.5 % |
| A (tol 1/16) | 81 % | 0.76 | 6.2 % (0.0/3.3/2.9) | 0.0 % | 20.4 % | 12.8 % | 19.97 | 10.74 | 5.97 | 3.501 | 0.486 | 6.31 | 5.60 | 15.6 % | 20.1 % |
| B (straddle) | 87 % | 0.76 | 5.7 % (0.0/3.0/2.7) | 0.0 % | 21.0 % | 13.2 % | 20.06 | 10.44 | 6.17 | 3.673 | 0.541 | 6.73 | 5.87 | 15.6 % | 20.5 % |
| C (straddle + tol 1/8) | 79 % | 0.75 | 5.9 % (0.0/3.1/2.8) | 0.0 % | 21.0 % | 13.1 % | 19.85 | 10.71 | 6.02 | 3.822 | 0.564 | 6.67 | 5.94 | 15.8 % | 19.3 % |
| pp5 (point costs) | 88 % | 0.75 | 4.5 % (0.0/2.3/2.1) | 0.0 % | 21.1 % | 13.7 % | 20.73 | 10.07 | 6.30 | 4.029 | 0.564 | 7.94 | 6.12 | 14.6 % | 23.3 % |
| pc2 (pp5 + C) | 94 % | 0.78 | 4.9 % (0.0/2.6/2.4) | 0.0 % | 20.9 % | 13.5 % | 20.43 | 10.03 | 6.36 | 3.782 | 0.524 | 7.81 | 5.98 | 16.0 % | 21.1 % |

**curvehd (1080p)**

| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| master | 94 % | 0.81 | 6.2 % (0.0/3.3/2.9) | 0.0 % | 20.3 % | 12.5 % | 19.20 | 10.71 | 5.91 | 3.167 | 0.446 | 5.81 | 5.32 | 16.2 % | 17.5 % |
| A (tol 1/16) | 82 % | 0.76 | 7.1 % (0.0/3.8/3.2) | 0.0 % | 19.8 % | 12.0 % | 19.17 | 11.53 | 5.93 | 2.888 | 0.413 | 5.18 | 5.02 | 15.9 % | 22.0 % |
| B (straddle) | 93 % | 0.81 | 6.6 % (0.0/3.5/3.1) | 0.0 % | 20.8 % | 12.7 % | 19.20 | 10.76 | 5.90 | 3.141 | 0.459 | 5.70 | 5.29 | 17.6 % | 17.1 % |
| C (straddle + tol 1/8) | 91 % | 0.80 | 7.0 % (0.0/3.8/3.2) | 0.0 % | 20.7 % | 12.4 % | 19.01 | 11.20 | 5.79 | 3.232 | 0.463 | 5.53 | 5.19 | 17.8 % | 18.0 % |
| pp5 (point costs) | 92 % | 0.78 | 5.0 % (0.0/2.7/2.3) | 0.0 % | 20.6 % | 13.1 % | 20.05 | 10.35 | 6.10 | 3.682 | 0.510 | 7.03 | 5.66 | 16.1 % | 18.6 % |
| pc2 (pp5 + C) | 93 % | 0.80 | 5.6 % (0.0/3.0/2.6) | 0.0 % | 20.0 % | 12.6 % | 19.52 | 10.32 | 6.23 | 3.380 | 0.476 | 6.74 | 5.43 | 17.2 % | 18.9 % |

**busey (both framings)**

| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| master | 84 % | 0.67 | 2.5 % (0.0/1.0/1.5) | 0.0 % | 14.7 % | 9.6 % | 24.29 | 10.19 | 8.47 | 6.646 | 0.873 | 9.88 | 3.89 | 17.3 % | 17.2 % |
| A (tol 1/16) | 82 % | 0.66 | 2.7 % (0.0/1.1/1.6) | 0.0 % | 15.1 % | 9.7 % | 25.02 | 10.55 | 8.55 | 6.422 | 0.848 | 9.94 | 3.90 | 17.7 % | 17.7 % |
| B (straddle) | 83 % | 0.67 | 2.5 % (0.0/1.0/1.5) | 0.0 % | 15.2 % | 9.7 % | 24.48 | 10.37 | 8.26 | 6.616 | 0.892 | 9.82 | 3.90 | 17.8 % | 16.9 % |
| C (straddle + tol 1/8) | 81 % | 0.66 | 2.6 % (0.0/1.1/1.5) | 0.0 % | 15.4 % | 9.9 % | 24.87 | 10.51 | 8.45 | 6.802 | 0.904 | 9.84 | 3.93 | 18.3 % | 17.3 % |
| pp5 (point costs) | 83 % | 0.66 | 2.4 % (0.0/1.0/1.4) | 0.0 % | 14.8 % | 9.6 % | 24.99 | 10.36 | 8.45 | 6.698 | 0.829 | 10.18 | 3.77 | 17.6 % | 17.4 % |
| pc2 (pp5 + C) | 86 % | 0.67 | 2.5 % (0.0/1.0/1.5) | 0.0 % | 15.2 % | 9.8 % | 24.68 | 10.37 | 8.56 | 6.612 | 0.819 | 9.95 | 3.78 | 18.2 % | 17.6 % |

#### a12: L1D misses and SIMD instructions per frame pass, and per extra point (ratios x thread_selfcounts instructions)

| phase | variant | L1D ld misses/pass | L1D st misses/pass | SIMD instr/pass | extra L1D ld misses per extra point | extra SIMD per extra point | extra non-SIMD per extra point |
|---|---|---|---|---|---|---|---|
| curve | master | 3401 k | 1774 k | 9.29 M |  |  |  |
| curve | A (tol 1/16) | 3732 k | 2007 k | 11.58 M | 11.8 | 81.3 | 606.4 |
| curve | B (straddle) | 3396 k | 1767 k | 9.57 M |  |  |  |
| curve | C (straddle + tol 1/8) | 3530 k | 1904 k | 10.58 M | 10.7 | 105.9 | 746.0 |
| curve | pp5 (point costs) | 3130 k | 1520 k | 6.75 M |  |  |  |
| curve | pc2 (pp5 + C) | 3255 k | 1599 k | 7.88 M | -12.0 | -117.0 | -558.9 |
| curvehd | master | 1361 k | 759 k | 4.43 M |  |  |  |
| curvehd | A (tol 1/16) | 1560 k | 939 k | 5.74 M | 13.2 | 87.3 | 610.6 |
| curvehd | B (straddle) | 1381 k | 774 k | 4.72 M |  |  |  |
| curvehd | C (straddle + tol 1/8) | 1464 k | 863 k | 5.39 M | 13.9 | 130.2 | 695.4 |
| curvehd | pp5 (point costs) | 1236 k | 638 k | 3.10 M |  |  |  |
| curvehd | pc2 (pp5 + C) | 1302 k | 688 k | 3.73 M | -8.1 | -93.7 | -475.8 |

