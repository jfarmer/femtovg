### mac: arm64 iOS 27.2 (26B5091g)

| perf level | name | cores | L1I | L1D | L2 (shared by) |
|---|---|---|---|---|---|
| 0 | Performance | 12 | 192 KiB | 128 KiB | 16384 KiB (6 cores) |
| 1 | Efficiency | 4 | 128 KiB | 64 KiB | 4096 KiB (4 cores) |

cache line 128 B, page 16384 B, RAM 128.0 GiB

#### mac: render-thread counts per pass (thread_selfcounts, E-cores; median frame of passes 1..n, summed over files x zooms)

| phase | variant | instructions/pass | vs master | cycles/pass | vs master | IPC | P-core share | encode share | wall ms/pass | runs spread (instr / cyc) | thermal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| curve | master | 720.0 M | +0.0 % | 350.8 M | +0.0 % | 2.05 | 0.0 % | 98 % | 177 | 0.2 / 3.6 % | ?,? |
| curve | A (tol 1/16) | 741.3 M | +2.9 % | 364.1 M | +3.8 % | 2.04 | 0.0 % | 98 % | 190 | 0.0 / 0.4 % | ?,? |
| curve | B (straddle) | 724.7 M | +0.6 % | 362.5 M | +3.3 % | 2.00 | 0.0 % | 98 % | 186 | 0.4 / 4.2 % | ?,? |
| curve | C (straddle + tol 1/8) | 737.9 M | +2.5 % | 394.9 M | +12.6 % | 1.87 | 0.0 % | 98 % | 289 | 0.4 / 1.3 % | ?,? |
| curvehd | master | 591.4 M | +0.0 % | 290.7 M | +0.0 % | 2.03 | 0.0 % | 99 % | 160 | 1.2 / 2.0 % | ?,? |
| curvehd | A (tol 1/16) | 598.0 M | +1.1 % | 286.0 M | -1.6 % | 2.09 | 0.0 % | 99 % | 142 | 1.0 / 5.2 % | ?,? |
| curvehd | B (straddle) | 588.1 M | -0.6 % | 285.5 M | -1.8 % | 2.06 | 0.0 % | 99 % | 142 | 0.3 / 2.2 % | ?,? |
| curvehd | C (straddle + tol 1/8) | 594.8 M | +0.6 % | 294.6 M | +1.3 % | 2.02 | 0.0 % | 99 % | 177 | 0.5 / 8.4 % | ?,? |
| busey | master | 1086.4 M | +0.0 % | 705.6 M | +0.0 % | 1.54 | 0.0 % | 86 % | 440 | 0.2 / 2.7 % | ?,? |
| busey | A (tol 1/16) | 1099.4 M | +1.2 % | 702.4 M | -0.5 % | 1.57 | 0.0 % | 86 % | 436 | 0.6 / 2.6 % | ?,? |
| busey | B (straddle) | 1098.5 M | +1.1 % | 734.6 M | +4.1 % | 1.50 | 0.1 % | 86 % | 538 | 0.5 / 4.3 % | ?,? |
| busey | C (straddle + tol 1/8) | 1118.0 M | +2.9 % | 797.9 M | +13.1 % | 1.40 | 0.0 % | 86 % | 604 | 2.1 / 11.9 % | ?,? |
| buseyhd | master | 495.8 M | +0.0 % | 305.7 M | +0.0 % | 1.62 | 0.7 % | 86 % | 189 | 0.4 / 1.5 % | ?,? |
| buseyhd | A (tol 1/16) | 499.0 M | +0.7 % | 300.1 M | -1.8 % | 1.66 | 0.3 % | 86 % | 180 | 0.4 / 3.5 % | ?,? |
| buseyhd | B (straddle) | 494.9 M | -0.2 % | 297.2 M | -2.8 % | 1.67 | 0.7 % | 86 % | 175 | 0.0 / 0.9 % | ?,? |
| buseyhd | C (straddle + tol 1/8) | 506.9 M | +2.3 % | 341.9 M | +11.9 % | 1.48 | 0.8 % | 86 % | 293 | 1.7 / 13.6 % | ?,? |

#### mac: per frame, key files (instructions on the render thread, median frame, mean of the runs)

| frame | points m / a / c | master instr | A | B | C | master cycles | A | B | C |
|---|---|---|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | 12735 / 17996 / 15079 | 68.39 M | +4.2 % | -0.2 % | +2.3 % | 31.37 M | +1.2 % | -2.5 % | +0.9 % |
| curvehd c_puzzle-fox z1 | 3983 / 5625 / 4705 | 61.98 M | +1.4 % | -0.5 % | +0.8 % | 29.32 M | -0.1 % | -0.9 % | +3.1 % |
| curvehd c_mr-settodefault z1 | 4981 / 6981 / 5794 | 7.89 M | +14.8 % | +0.9 % | +7.4 % | 5.41 M | +6.9 % | -0.1 % | +5.9 % |
| curvehd c_duckduckgo z1 | 1273 / 2095 / 1814 | 109.39 M | +0.1 % | -0.5 % | +0.1 % | 51.97 M | -1.8 % | -1.1 % | +2.3 % |
| curvehd c_nyt-crossplay z1 | 1729 / 2162 / 1993 | 111.84 M | -0.2 % | -0.7 % | -0.0 % | 52.96 M | -2.4 % | -2.1 % | +1.2 % |
| curve c_tiger z1 | 5872 / 8036 / 6828 | 63.31 M | +2.5 % | -0.2 % | +1.9 % | 27.98 M | +1.4 % | +0.2 % | +7.5 % |
| curve c_tiger z4 | 10917 / 15480 / 13040 | 19.25 M | +12.6 % | +1.1 % | +8.1 % | 7.73 M | +12.1 % | +0.0 % | +15.3 % |
| curvehd svgenius x10 z1 | 10518 / 14607 / 12857 | 33.32 M | +7.0 % | -0.1 % | +4.6 % | 20.84 M | +2.0 % | -1.2 % | +3.5 % |
| curve svgenius x10 z1 | 4971 / 6990 / 5773 | 29.21 M | +5.4 % | +1.0 % | +3.7 % | 17.62 M | +4.7 % | +3.6 % | +13.8 % |

#### mac: cost per flattened point (points per pass from the anatomy probe)

| phase | variant | points/pass | vertices/pass | extra points vs master | extra instr per extra point | extra cycles per extra point |
|---|---|---|---|---|---|---|
| curve | master | 74312 | 349268 | +0 (+0.0 %) | - | - |
| curve | A (tol 1/16) | 102478 | 482788 | +28166 (+37.9 %) | 754 | 472 |
| curve | B (straddle) | 74312 | 349268 | +0 (+0.0 %) | same points; +62 per point | same points; +157 per point |
| curve | C (straddle + tol 1/8) | 86418 | 406279 | +12106 (+16.3 %) | 1474 | 3644 |
| curvehd | master | 37534 | 192464 | +0 (+0.0 %) | - | - |
| curvehd | A (tol 1/16) | 52535 | 270917 | +15001 (+40.0 %) | 445 | -313 |
| curvehd | B (straddle) | 37534 | 192464 | +0 (+0.0 %) | same points; -87 per point | same points; -140 per point |
| curvehd | C (straddle + tol 1/8) | 44941 | 231481 | +7407 (+19.7 %) | 467 | 526 |
| busey | master | 35846 | 160046 | +0 (+0.0 %) | - | - |
| busey | A (tol 1/16) | 48832 | 223478 | +12986 (+36.2 %) | 1000 | -252 |
| busey | B (straddle) | 35846 | 160046 | +0 (+0.0 %) | same points; +337 per point | same points; +808 per point |
| busey | C (straddle + tol 1/8) | 41580 | 187564 | +5734 (+16.0 %) | 5512 | 16097 |
| buseyhd | master | 17685 | 87579 | +0 (+0.0 %) | - | - |
| buseyhd | A (tol 1/16) | 24265 | 122681 | +6580 (+37.2 %) | 495 | -844 |
| buseyhd | B (straddle) | 17685 | 87579 | +0 (+0.0 %) | same points; -50 per point | same points; -479 per point |
| buseyhd | C (straddle + tol 1/8) | 21144 | 106197 | +3459 (+19.6 %) | 3227 | 10474 |

#### mac: memory (phys_footprint sampled every 0.2 ms; BuseyBench portraits)

| variant | busey peak (max frame) | busey peak (median of per-frame peaks) | buseyhd peak (max frame) | graphics part at hd peak | lifetime max of the run | footprint after last frame |
|---|---|---|---|---|---|---|
| master | 1315.1 MiB | 1288.4 MiB | 1433.9 MiB | 1309.1 MiB | 1433.9 MiB | 1361.8 MiB |
| A (tol 1/16) | 1317.3 MiB | 1290.7 MiB | 1435.2 MiB | 1309.2 MiB | 1435.2 MiB | 1369.3 MiB |
| B (straddle) | 1315.2 MiB | 1288.5 MiB | 1433.6 MiB | 1309.1 MiB | 1433.6 MiB | 1365.2 MiB |
| C (straddle + tol 1/8) | 1317.2 MiB | 1290.4 MiB | 1433.0 MiB | 1307.0 MiB | 1434.6 MiB | 1362.1 MiB |

#### mac: event mix of the render thread on the E-cores (Instruments counters-profile samples; per 1000 instructions unless noted)


**curve (460x260, z1/2/4)**

| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| master | 62 % | 2.18 | 5.5 % (2.6/1.6/1.4) | nan % | nan % | nan % | 14.19 | 7.73 | 3.80 | 1.268 | nan | nan | nan | 15.1 % | nan % |
| A (tol 1/16) | 31 % | 2.03 | 6.7 % (3.3/1.8/1.6) | nan % | nan % | nan % | 14.89 | 8.77 | 4.11 | 1.712 | nan | nan | nan | 16.8 % | nan % |
| B (straddle) | 53 % | 2.18 | 5.8 % (2.7/1.7/1.4) | nan % | nan % | nan % | 14.20 | 8.04 | 3.81 | 1.331 | nan | nan | nan | 15.5 % | nan % |
| C (straddle + tol 1/8) | 14 % | 1.70 | 6.3 % (3.0/1.8/1.6) | nan % | nan % | nan % | 15.89 | 10.52 | 4.51 | 1.904 | nan | nan | nan | 23.6 % | nan % |

**curvehd (1080p)**

| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| master | 67 % | 2.21 | 5.1 % (2.3/1.5/1.3) | nan % | nan % | nan % | 14.62 | 7.71 | 3.75 | 1.218 | nan | nan | nan | 14.7 % | nan % |
| A (tol 1/16) | 60 % | 2.21 | 5.6 % (2.7/1.6/1.3) | nan % | nan % | nan % | 14.77 | 8.23 | 3.82 | 1.303 | nan | nan | nan | 15.2 % | nan % |
| B (straddle) | 54 % | 2.16 | 5.0 % (2.3/1.5/1.3) | nan % | nan % | nan % | 14.70 | 7.96 | 3.76 | 1.178 | nan | nan | nan | 15.6 % | nan % |

**busey (both framings)**

| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

#### mac: L1D misses and SIMD instructions per frame pass, and per extra point (ratios x thread_selfcounts instructions)

| phase | variant | L1D ld misses/pass | L1D st misses/pass | SIMD instr/pass | extra L1D ld misses per extra point | extra SIMD per extra point | extra non-SIMD per extra point |
|---|---|---|---|---|---|---|---|
| curve | master | 10218 k | 5563 k | 39.94 M |  |  |  |
| curve | A (tol 1/16) | 11040 k | 6499 k | 49.41 M | 29.2 | 336.2 | 417.6 |
| curve | B (straddle) | 10293 k | 5823 k | 41.84 M |  |  |  |
| curve | C (straddle + tol 1/8) | 11727 k | 7761 k | 46.66 M | 124.7 | 555.3 | 918.8 |
| curvehd | master | 8645 k | 4558 k | 29.91 M |  |  |  |
| curvehd | A (tol 1/16) | 8835 k | 4923 k | 33.72 M | 12.7 | 253.9 | 190.6 |
| curvehd | B (straddle) | 8645 k | 4682 k | 29.60 M |  |  |  |

