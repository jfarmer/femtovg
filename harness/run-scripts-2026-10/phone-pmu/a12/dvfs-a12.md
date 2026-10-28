### a12: warm-frame cycles at a fixed E-core clock (frames binned by measured encode clock, pooled over runs)


**clock 0.45-0.65 GHz**

| group | variant | keys | frames | instr/pass | vs master | cycles/pass | vs master | IPC |
|---|---|---|---|---|---|---|---|---|
| curve-heavy (curve + curvehd) | master | 66 | 4180 | 217.0 M | +0.0 % | 263.1 M | +0.0 % | 0.82 |
| curve-heavy (curve + curvehd) | A | 66 | 4297 | 245.9 M | +13.4 % | 293.4 M | +11.5 % | 0.84 |
| curve-heavy (curve + curvehd) | B | 66 | 4858 | 219.8 M | +1.3 % | 267.9 M | +1.9 % | 0.82 |
| curve-heavy (curve + curvehd) | C | 66 | 4851 | 233.0 M | +7.4 % | 276.6 M | +5.1 % | 0.84 |
| curve-heavy (curve + curvehd) | pp5 | 66 | 4947 | 191.3 M | -11.8 % | 235.7 M | -10.4 % | 0.81 |
| curve-heavy (curve + curvehd) | pc2 | 66 | 4551 | 205.0 M | -5.5 % | 257.4 M | -2.1 % | 0.80 |
| BuseyBench (busey + buseyhd) | master | 5 | 85 | 285.7 M | +0.0 % | 436.6 M | +0.0 % | 0.65 |
| BuseyBench (busey + buseyhd) | A | 5 | 92 | 289.7 M | +1.4 % | 441.7 M | +1.2 % | 0.66 |
| BuseyBench (busey + buseyhd) | B | 5 | 95 | 286.1 M | +0.2 % | 437.1 M | +0.1 % | 0.65 |
| BuseyBench (busey + buseyhd) | C | 5 | 104 | 287.4 M | +0.6 % | 438.8 M | +0.5 % | 0.65 |
| BuseyBench (busey + buseyhd) | pp5 | 5 | 95 | 282.3 M | -1.2 % | 435.3 M | -0.3 % | 0.65 |
| BuseyBench (busey + buseyhd) | pc2 | 5 | 89 | 283.3 M | -0.8 % | 435.9 M | -0.2 % | 0.65 |

key files at this clock, instructions / cycles vs master (%):

| frame | A | B | C | pp5 | pc2 | min frames per variant |
|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | +15.3 / +15.5 | +1.6 / +2.6 | +8.3 / +8.8 | -13.0 / -12.3 | -5.7 / -4.3 | 71 |
| curvehd c_puzzle-fox z1 | +24.8 / +22.5 | +2.8 / +4.0 | +13.6 / +12.8 | -20.2 / -18.7 | -8.9 / -8.6 | 71 |
| curvehd c_mr-settodefault z1 | +20.4 / +16.7 | +2.5 / +3.5 | +11.0 / +10.3 | -17.1 / -12.9 | -8.8 / -7.3 | 72 |
| curve c_tiger z1 | +9.6 / +12.2 | +0.7 / +2.1 | +5.1 / +6.3 | -7.1 / -4.9 | -3.1 / -0.7 | 66 |
| curve c_tiger z4 | +15.4 / +17.7 | +1.8 / +3.4 | +9.5 / +11.4 | -11.0 / -12.5 | -3.1 / -4.0 | 65 |

**clock 1.45-1.7 GHz**

| group | variant | keys | frames | instr/pass | vs master | cycles/pass | vs master | IPC |
|---|---|---|---|---|---|---|---|---|
| curve-heavy (curve + curvehd) | master | 8 | 60 | 13.9 M | +0.0 % | 22.5 M | +0.0 % | 0.62 |
| curve-heavy (curve + curvehd) | A | 8 | 26 | 16.2 M | +16.4 % | 26.0 M | +15.5 % | 0.62 |
| curve-heavy (curve + curvehd) | B | 8 | 14 | 14.2 M | +2.5 % | 23.8 M | +5.8 % | 0.60 |
| curve-heavy (curve + curvehd) | C | 8 | 18 | 15.0 M | +8.3 % | 23.5 M | +4.4 % | 0.64 |
| curve-heavy (curve + curvehd) | pp5 | 8 | 12 | 11.8 M | -14.9 % | 19.7 M | -12.4 % | 0.60 |
| curve-heavy (curve + curvehd) | pc2 | 8 | 28 | 12.6 M | -9.0 % | 21.3 M | -5.5 % | 0.59 |
| BuseyBench (busey + buseyhd) | master | 5 | 34 | 229.4 M | +0.0 % | 416.3 M | +0.0 % | 0.55 |
| BuseyBench (busey + buseyhd) | A | 5 | 26 | 232.7 M | +1.4 % | 428.0 M | +2.8 % | 0.54 |
| BuseyBench (busey + buseyhd) | B | 5 | 38 | 230.0 M | +0.2 % | 418.5 M | +0.5 % | 0.55 |
| BuseyBench (busey + buseyhd) | C | 5 | 29 | 232.1 M | +1.2 % | 421.6 M | +1.3 % | 0.55 |
| BuseyBench (busey + buseyhd) | pp5 | 5 | 38 | 228.9 M | -0.2 % | 423.4 M | +1.7 % | 0.54 |
| BuseyBench (busey + buseyhd) | pc2 | 5 | 29 | 229.2 M | -0.1 % | 423.7 M | +1.8 % | 0.54 |
