### a14: warm-frame cycles at a fixed E-core clock (frames binned by measured encode clock, pooled over runs)


**clock 0.45-0.65 GHz**

| group | variant | keys | frames | instr/pass | vs master | cycles/pass | vs master | IPC |
|---|---|---|---|---|---|---|---|---|
| curve-heavy (curve + curvehd) | master | 68 | 3079 | 246.4 M | +0.0 % | 160.8 M | +0.0 % | 1.53 |
| curve-heavy (curve + curvehd) | A | 68 | 3591 | 275.4 M | +11.8 % | 177.7 M | +10.5 % | 1.55 |
| curve-heavy (curve + curvehd) | B | 68 | 3290 | 248.4 M | +0.8 % | 163.6 M | +1.7 % | 1.52 |
| curve-heavy (curve + curvehd) | C | 68 | 4424 | 262.8 M | +6.7 % | 169.7 M | +5.5 % | 1.55 |
| curve-heavy (curve + curvehd) | pp5 | 68 | 4874 | 219.5 M | -10.9 % | 147.9 M | -8.0 % | 1.48 |
| curve-heavy (curve + curvehd) | pc2 | 68 | 4817 | 232.3 M | -5.7 % | 154.1 M | -4.2 % | 1.51 |
| BuseyBench (busey + buseyhd) | master | 8 | 46 | 454.0 M | +0.0 % | 423.5 M | +0.0 % | 1.07 |
| BuseyBench (busey + buseyhd) | A | 8 | 37 | 458.6 M | +1.0 % | 425.7 M | +0.5 % | 1.08 |
| BuseyBench (busey + buseyhd) | B | 8 | 60 | 453.4 M | -0.1 % | 434.1 M | +2.5 % | 1.04 |
| BuseyBench (busey + buseyhd) | C | 8 | 61 | 456.9 M | +0.6 % | 459.9 M | +8.6 % | 0.99 |
| BuseyBench (busey + buseyhd) | pp5 | 8 | 38 | 448.0 M | -1.3 % | 417.3 M | -1.5 % | 1.07 |
| BuseyBench (busey + buseyhd) | pc2 | 8 | 46 | 453.0 M | -0.2 % | 433.0 M | +2.2 % | 1.05 |

key files at this clock, instructions / cycles vs master (%):

| frame | A | B | C | pp5 | pc2 | min frames per variant |
|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | +15.3 / +18.0 | +1.2 / +2.5 | +8.3 / +10.3 | -12.8 / -13.1 | -6.1 / -5.8 | 49 |
| curvehd c_puzzle-fox z1 | +24.5 / +22.9 | +1.6 / +3.9 | +14.4 / +14.5 | -20.4 / -16.3 | -9.6 / -7.3 | 48 |
| curvehd c_mr-settodefault z1 | +20.0 / +16.7 | +1.8 / +2.8 | +10.2 / +7.7 | -18.9 / -15.6 | -10.4 / -9.9 | 41 |
| curve c_tiger z1 | +9.3 / +11.6 | +0.5 / +2.7 | +5.1 / +7.1 | -7.0 / -5.6 | -3.1 / -1.6 | 46 |
| curve c_tiger z4 | +15.3 / +16.8 | +1.5 / +3.2 | +9.6 / +11.6 | -11.0 / -10.9 | -3.5 / -2.8 | 52 |

**clock 1.65-2.0 GHz**

| group | variant | keys | frames | instr/pass | vs master | cycles/pass | vs master | IPC |
|---|---|---|---|---|---|---|---|---|
| curve-heavy (curve + curvehd) | master | 52 | 1285 | 143.8 M | +0.0 % | 140.8 M | +0.0 % | 1.02 |
| curve-heavy (curve + curvehd) | A | 52 | 885 | 163.9 M | +14.0 % | 160.2 M | +13.8 % | 1.02 |
| curve-heavy (curve + curvehd) | B | 52 | 1253 | 145.9 M | +1.4 % | 140.8 M | -0.0 % | 1.04 |
| curve-heavy (curve + curvehd) | C | 52 | 549 | 154.9 M | +7.7 % | 149.3 M | +6.0 % | 1.04 |
| curve-heavy (curve + curvehd) | pp5 | 52 | 189 | 127.1 M | -11.7 % | 126.9 M | -9.9 % | 1.00 |
| curve-heavy (curve + curvehd) | pc2 | 52 | 180 | 135.6 M | -5.7 % | 135.9 M | -3.5 % | 1.00 |
| BuseyBench (busey + buseyhd) | master | 11 | 44 | 598.9 M | +0.0 % | 753.6 M | +0.0 % | 0.79 |
| BuseyBench (busey + buseyhd) | A | 11 | 114 | 600.4 M | +0.2 % | 731.3 M | -3.0 % | 0.82 |
| BuseyBench (busey + buseyhd) | B | 11 | 31 | 601.6 M | +0.4 % | 762.4 M | +1.2 % | 0.79 |
| BuseyBench (busey + buseyhd) | C | 11 | 40 | 601.7 M | +0.5 % | 735.0 M | -2.5 % | 0.82 |
| BuseyBench (busey + buseyhd) | pp5 | 11 | 90 | 590.4 M | -1.4 % | 736.9 M | -2.2 % | 0.80 |
| BuseyBench (busey + buseyhd) | pc2 | 11 | 74 | 593.6 M | -0.9 % | 727.1 M | -3.5 % | 0.82 |

key files at this clock, instructions / cycles vs master (%):

| frame | A | B | C | pp5 | pc2 | min frames per variant |
|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | +16.2 / +23.1 | +1.1 / -0.0 | +8.4 / +9.2 | -12.3 / -13.2 | -5.5 / -6.9 | 4 |
| curvehd c_puzzle-fox z1 | +24.4 / +21.8 | +2.0 / -4.6 | +13.9 / +11.4 | -20.1 / -20.0 | -8.7 / -10.1 | 3 |
| curvehd c_mr-settodefault z1 | +20.8 / +17.9 | +2.3 / -2.2 | +12.0 / +8.0 | -17.5 / -13.0 | -8.5 / -6.2 | 3 |
