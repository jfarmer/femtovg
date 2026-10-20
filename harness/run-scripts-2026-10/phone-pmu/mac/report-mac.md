### mac: arm64 iOS 27.2 (26B5101f)

| perf level | name | cores | L1I | L1D | L2 (shared by) |
|---|---|---|---|---|---|
| 0 | Performance | 12 | 192 KiB | 128 KiB | 16384 KiB (6 cores) |
| 1 | Efficiency | 4 | 128 KiB | 64 KiB | 4096 KiB (4 cores) |

cache line 128 B, page 16384 B, RAM 128.0 GiB

#### mac: render-thread counts per pass (thread_selfcounts, E-cores; median frame of passes 1..n, summed over files x zooms)

| phase | variant | instructions/pass | vs master | cycles/pass | vs master | IPC | P-core share | encode share | wall ms/pass | runs spread (instr / cyc) | thermal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| curve | master | 190.5 M | +0.0 % | 130.0 M | +0.0 % | 1.46 | 0.0 % | 92 % | 116 | 2.0 / 26.4 % | ?,?,?,?,?,? |
| curve | A (tol 1/16) | 206.8 M | +8.5 % | 131.9 M | +1.4 % | 1.57 | 0.0 % | 93 % | 128 | 4.0 / 22.3 % | ?,?,?,?,?,? |
| curve | B (straddle) | 191.8 M | +0.7 % | 126.5 M | -2.7 % | 1.52 | 0.0 % | 93 % | 131 | 3.3 / 28.1 % | ?,?,?,?,?,? |
| curve | C (straddle + tol 1/8) | 200.0 M | +5.0 % | 130.9 M | +0.6 % | 1.53 | 0.0 % | 93 % | 131 | 5.7 / 40.0 % | ?,?,?,?,?,? |
| curve | pp5 (point costs) | 174.4 M | -8.4 % | 116.5 M | -10.4 % | 1.50 | 0.0 % | 92 % | 119 | 5.2 / 24.9 % | ?,?,?,?,?,? |
| curve | pc2 (pp5 + C) | 182.5 M | -4.2 % | 118.7 M | -8.7 % | 1.54 | 0.0 % | 92 % | 110 | 1.2 / 13.9 % | ?,?,?,?,?,? |
| curvehd | master | 75.9 M | +0.0 % | 46.8 M | +0.0 % | 1.62 | 0.0 % | 94 % | 47 | 4.0 / 22.5 % | ?,?,?,?,?,? |
| curvehd | A (tol 1/16) | 85.3 M | +12.3 % | 50.3 M | +7.4 % | 1.70 | 0.0 % | 94 % | 55 | 4.1 / 25.6 % | ?,?,?,?,?,? |
| curvehd | B (straddle) | 76.7 M | +1.0 % | 46.3 M | -1.0 % | 1.65 | 0.0 % | 94 % | 50 | 2.1 / 17.6 % | ?,?,?,?,?,? |
| curvehd | C (straddle + tol 1/8) | 82.3 M | +8.3 % | 50.4 M | +7.6 % | 1.63 | 0.0 % | 94 % | 55 | 4.0 / 30.0 % | ?,?,?,?,?,? |
| curvehd | pp5 (point costs) | 67.7 M | -10.8 % | 43.9 M | -6.3 % | 1.54 | 0.0 % | 93 % | 48 | 1.7 / 10.9 % | ?,?,?,?,?,? |
| curvehd | pc2 (pp5 + C) | 72.4 M | -4.7 % | 44.1 M | -5.7 % | 1.64 | 0.0 % | 93 % | 46 | 2.9 / 23.4 % | ?,?,?,?,?,? |
| busey | master | 858.6 M | +0.0 % | 624.1 M | +0.0 % | 1.38 | 0.0 % | 82 % | 654 | 3.3 / 36.4 % | ?,?,?,?,?,? |
| busey | A (tol 1/16) | 868.5 M | +1.2 % | 620.8 M | -0.5 % | 1.40 | 0.0 % | 82 % | 633 | 3.2 / 27.6 % | ?,?,?,?,?,? |
| busey | B (straddle) | 857.8 M | -0.1 % | 593.7 M | -4.9 % | 1.44 | 0.0 % | 82 % | 656 | 2.4 / 22.1 % | ?,?,?,?,?,? |
| busey | C (straddle + tol 1/8) | 865.9 M | +0.8 % | 627.8 M | +0.6 % | 1.38 | 0.0 % | 82 % | 697 | 3.0 / 28.3 % | ?,?,?,?,?,? |
| busey | pp5 (point costs) | 852.3 M | -0.7 % | 620.1 M | -0.6 % | 1.37 | 0.0 % | 82 % | 643 | 3.5 / 33.3 % | ?,?,?,?,?,? |
| busey | pc2 (pp5 + C) | 852.8 M | -0.7 % | 626.2 M | +0.3 % | 1.36 | 0.0 % | 82 % | 823 | 2.2 / 22.5 % | ?,?,?,?,?,? |
| buseyhd | master | 300.9 M | +0.0 % | 212.2 M | +0.0 % | 1.42 | 1.0 % | 78 % | 218 | 3.0 / 34.6 % | ?,?,?,?,?,? |
| buseyhd | A (tol 1/16) | 306.1 M | +1.7 % | 217.5 M | +2.5 % | 1.41 | 1.0 % | 78 % | 221 | 4.1 / 38.5 % | ?,?,?,?,?,? |
| buseyhd | B (straddle) | 300.7 M | -0.0 % | 208.7 M | -1.6 % | 1.44 | 0.8 % | 78 % | 225 | 2.9 / 26.2 % | ?,?,?,?,?,? |
| buseyhd | C (straddle + tol 1/8) | 303.2 M | +0.8 % | 211.7 M | -0.2 % | 1.43 | 0.8 % | 78 % | 207 | 3.3 / 28.4 % | ?,?,?,?,?,? |
| buseyhd | pp5 (point costs) | 296.2 M | -1.6 % | 205.6 M | -3.1 % | 1.44 | 0.7 % | 77 % | 212 | 4.8 / 34.1 % | ?,?,?,?,?,? |
| buseyhd | pc2 (pp5 + C) | 298.3 M | -0.8 % | 212.0 M | -0.1 % | 1.41 | 1.1 % | 78 % | 265 | 2.5 / 11.2 % | ?,?,?,?,?,? |

#### mac: cold frames (rep 0: the first frame of a file, drawn right after another file; pipelines and shaders the previous frame did not use were dropped) vs warm frames (rep >= 1)

| phase | variant | warm instr/pass | cold instr/pass | cold - warm | cold vs master cold | warm cycles/pass | cold cycles/pass | cold cycles vs master cold |
|---|---|---|---|---|---|---|---|---|
| curve | master | 190.5 M | 741.0 M | +289 % | +0.0 % | 130.0 M | 424.1 M | +0.0 % |
| curve | A (tol 1/16) | 206.8 M | 754.4 M | +265 % | +1.8 % | 131.9 M | 415.4 M | -2.0 % |
| curve | B (straddle) | 191.8 M | 739.7 M | +286 % | -0.2 % | 126.5 M | 410.2 M | -3.3 % |
| curve | C (straddle + tol 1/8) | 200.0 M | 747.6 M | +274 % | +0.9 % | 130.9 M | 417.3 M | -1.6 % |
| curve | pp5 (point costs) | 174.4 M | 722.1 M | +314 % | -2.6 % | 116.5 M | 395.9 M | -6.7 % |
| curve | pc2 (pp5 + C) | 182.5 M | 729.5 M | +300 % | -1.6 % | 118.7 M | 394.1 M | -7.1 % |
| curvehd | master | 75.9 M | 606.1 M | +698 % | +0.0 % | 46.8 M | 316.1 M | +0.0 % |
| curvehd | A (tol 1/16) | 85.3 M | 614.1 M | +620 % | +1.3 % | 50.3 M | 316.8 M | +0.2 % |
| curvehd | B (straddle) | 76.7 M | 605.7 M | +690 % | -0.1 % | 46.3 M | 310.1 M | -1.9 % |
| curvehd | C (straddle + tol 1/8) | 82.3 M | 613.7 M | +646 % | +1.3 % | 50.4 M | 323.6 M | +2.4 % |
| curvehd | pp5 (point costs) | 67.7 M | 597.7 M | +782 % | -1.4 % | 43.9 M | 311.9 M | -1.3 % |
| curvehd | pc2 (pp5 + C) | 72.4 M | 600.8 M | +730 % | -0.9 % | 44.1 M | 303.7 M | -3.9 % |
| busey | master | 858.6 M | 1112.7 M | +30 % | +0.0 % | 624.1 M | 760.9 M | +0.0 % |
| busey | A (tol 1/16) | 868.5 M | 1122.4 M | +29 % | +0.9 % | 620.8 M | 749.9 M | -1.4 % |
| busey | B (straddle) | 857.8 M | 1112.0 M | +30 % | -0.1 % | 593.7 M | 724.7 M | -4.8 % |
| busey | C (straddle + tol 1/8) | 865.9 M | 1122.7 M | +30 % | +0.9 % | 627.8 M | 769.3 M | +1.1 % |
| busey | pp5 (point costs) | 852.3 M | 1105.9 M | +30 % | -0.6 % | 620.1 M | 754.1 M | -0.9 % |
| busey | pc2 (pp5 + C) | 852.8 M | 1107.6 M | +30 % | -0.5 % | 626.2 M | 764.8 M | +0.5 % |
| buseyhd | master | 300.9 M | 504.2 M | +68 % | +0.0 % | 212.2 M | 325.4 M | +0.0 % |
| buseyhd | A (tol 1/16) | 306.1 M | 509.2 M | +66 % | +1.0 % | 217.5 M | 327.1 M | +0.5 % |
| buseyhd | B (straddle) | 300.7 M | 502.5 M | +67 % | -0.3 % | 208.7 M | 314.5 M | -3.3 % |
| buseyhd | C (straddle + tol 1/8) | 303.2 M | 507.9 M | +68 % | +0.7 % | 211.7 M | 320.9 M | -1.4 % |
| buseyhd | pp5 (point costs) | 296.2 M | 498.7 M | +68 % | -1.1 % | 205.6 M | 310.4 M | -4.6 % |
| buseyhd | pc2 (pp5 + C) | 298.3 M | 501.6 M | +68 % | -0.5 % | 212.0 M | 320.3 M | -1.6 % |

#### mac: per frame, key files (instructions on the render thread, median frame, mean of the runs)

| frame | points m / a / c | master instr | A | B | C | pp5 | pc2 | master cycles | A | B | C | pp5 | pc2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | 12735 / 17996 / 15079 | 27.46 M | +12.2 % | +1.3 % | +7.5 % | -10.0 % | -4.2 % | 11.48 M | +11.3 % | +0.9 % | +10.2 % | -9.7 % | -4.5 % |
| curvehd c_puzzle-fox z1 | 3983 / 5625 / 4705 | 4.74 M | +22.3 % | +1.4 % | +13.7 % | -17.5 % | -6.6 % | 2.73 M | +15.9 % | +3.3 % | +17.7 % | -10.5 % | -1.4 % |
| curvehd c_mr-settodefault z1 | 4981 / 6981 / 5794 | 6.73 M | +18.1 % | +1.1 % | +9.9 % | -15.5 % | -6.6 % | 4.28 M | +12.6 % | -0.5 % | +9.4 % | -11.8 % | -5.5 % |
| curvehd c_duckduckgo z1 | 1273 / 2095 / 1814 | 2.50 M | +20.6 % | +2.4 % | +17.0 % | -11.2 % | +0.6 % | 2.13 M | +12.2 % | +3.4 % | +11.0 % | +1.0 % | +2.4 % |
| curvehd c_nyt-crossplay z1 | 1729 / 2162 / 1993 | 2.74 M | +8.6 % | +1.1 % | +8.3 % | -14.2 % | -7.9 % | 2.01 M | +1.2 % | -5.4 % | +1.0 % | -10.0 % | -10.2 % |
| curve c_tiger z1 | 5872 / 8036 / 6828 | 22.83 M | +6.8 % | +0.2 % | +3.5 % | -6.0 % | -2.7 % | 9.90 M | +2.1 % | -1.0 % | +3.2 % | -10.2 % | -5.6 % |
| curve c_tiger z4 | 10917 / 15480 / 13040 | 19.63 M | +11.7 % | +0.9 % | +7.3 % | -9.0 % | -2.1 % | 8.76 M | +8.3 % | -1.0 % | +6.2 % | -12.7 % | -6.4 % |
| curvehd svgenius x10 z1 | 10518 / 14607 / 12857 | 16.95 M | +15.0 % | +1.3 % | +11.8 % | -14.2 % | -6.5 % | 12.95 M | +6.7 % | -3.0 % | +8.7 % | -4.4 % | -7.8 % |
| curve svgenius x10 z1 | 4971 / 6990 / 5773 | 13.50 M | +9.0 % | +0.2 % | +5.2 % | -10.6 % | -6.6 % | 12.52 M | -1.1 % | -5.6 % | -2.7 % | -14.9 % | -15.2 % |

#### mac: cost per flattened point (points per pass from the anatomy probe)

| phase | variant | points/pass | vertices/pass | extra points vs master | extra instr per extra point | extra cycles per extra point |
|---|---|---|---|---|---|---|
| curve | master | 74312 | 349268 | +0 (+0.0 %) | - | - |
| curve | A (tol 1/16) | 102478 | 482788 | +28166 (+37.9 %) | 578 | 66 |
| curve | B (straddle) | 74312 | 349268 | +0 (+0.0 %) | same points; +18 per point | same points; -47 per point |
| curve | C (straddle + tol 1/8) | 86418 | 406279 | +12106 (+16.3 %) | 787 | 68 |
| curve | pp5 (point costs) | 74312 | 349268 | +0 (+0.0 %) | same points; -216 per point | same points; -183 per point |
| curve | pc2 (pp5 + C) | 86418 | 406279 | +12106 (+16.3 %) | -656 | -937 |
| curvehd | master | 37534 | 192464 | +0 (+0.0 %) | - | - |
| curvehd | A (tol 1/16) | 52535 | 270917 | +15001 (+40.0 %) | 623 | 231 |
| curvehd | B (straddle) | 37534 | 192464 | +0 (+0.0 %) | same points; +20 per point | same points; -13 per point |
| curvehd | C (straddle + tol 1/8) | 44941 | 231481 | +7407 (+19.7 %) | 855 | 483 |
| curvehd | pp5 (point costs) | 37534 | 192464 | +0 (+0.0 %) | same points; -218 per point | same points; -78 per point |
| curvehd | pc2 (pp5 + C) | 44941 | 231481 | +7407 (+19.7 %) | -482 | -363 |
| busey | master | 35846 | 160046 | +0 (+0.0 %) | - | - |
| busey | A (tol 1/16) | 48832 | 223478 | +12986 (+36.2 %) | 760 | -251 |
| busey | B (straddle) | 35846 | 160046 | +0 (+0.0 %) | same points; -23 per point | same points; -848 per point |
| busey | C (straddle + tol 1/8) | 41580 | 187564 | +5734 (+16.0 %) | 1270 | 654 |
| busey | pp5 (point costs) | 35846 | 160046 | +0 (+0.0 %) | same points; -178 per point | same points; -109 per point |
| busey | pc2 (pp5 + C) | 41580 | 187564 | +5734 (+16.0 %) | -1015 | 368 |
| buseyhd | master | 17685 | 87579 | +0 (+0.0 %) | - | - |
| buseyhd | A (tol 1/16) | 24265 | 122681 | +6580 (+37.2 %) | 792 | 801 |
| buseyhd | B (straddle) | 17685 | 87579 | +0 (+0.0 %) | same points; -7 per point | same points; -194 per point |
| buseyhd | C (straddle + tol 1/8) | 21144 | 106197 | +3459 (+19.6 %) | 662 | -137 |
| buseyhd | pp5 (point costs) | 17685 | 87579 | +0 (+0.0 %) | same points; -264 per point | same points; -372 per point |
| buseyhd | pc2 (pp5 + C) | 21144 | 106197 | +3459 (+19.6 %) | -737 | -52 |

#### mac: memory (phys_footprint sampled every 0.2 ms; BuseyBench portraits)

| variant | busey peak (max frame) | busey peak (median of per-frame peaks) | buseyhd peak (max frame) | graphics part at hd peak | lifetime max of the run | footprint after last frame |
|---|---|---|---|---|---|---|
| master | 1326.1 MiB | 1288.9 MiB | 1441.0 MiB | 1312.8 MiB | 1441.0 MiB | 1366.5 MiB |
| A (tol 1/16) | 1327.2 MiB | 1293.9 MiB | 1441.2 MiB | 1312.9 MiB | 1441.2 MiB | 1369.9 MiB |
| B (straddle) | 1327.1 MiB | 1289.6 MiB | 1441.8 MiB | 1312.8 MiB | 1441.8 MiB | 1371.6 MiB |
| C (straddle + tol 1/8) | 1326.2 MiB | 1291.9 MiB | 1440.3 MiB | 1312.8 MiB | 1443.2 MiB | 1367.2 MiB |
| pp5 (point costs) | 1325.3 MiB | 1289.1 MiB | 1439.5 MiB | 1312.4 MiB | 1439.5 MiB | 1368.2 MiB |
| pc2 (pp5 + C) | 1322.6 MiB | 1272.7 MiB | 1438.8 MiB | 1312.7 MiB | 1441.3 MiB | 1366.7 MiB |

