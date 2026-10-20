### mac: warm-frame cycles at a fixed E-core clock (frames binned by measured encode clock, pooled over runs)


**clock 0.95-1.1 GHz**

| group | variant | keys | frames | instr/pass | vs master | cycles/pass | vs master | IPC |
|---|---|---|---|---|---|---|---|---|
| curve-heavy (curve + curvehd) | master | 67 | 502 | 266.2 M | +0.0 % | 154.7 M | +0.0 % | 1.72 |
| curve-heavy (curve + curvehd) | A | 67 | 865 | 288.7 M | +8.5 % | 157.9 M | +2.1 % | 1.83 |
| curve-heavy (curve + curvehd) | B | 67 | 973 | 265.8 M | -0.1 % | 150.3 M | -2.8 % | 1.77 |
| curve-heavy (curve + curvehd) | C | 67 | 901 | 278.0 M | +4.4 % | 155.0 M | +0.2 % | 1.79 |
| curve-heavy (curve + curvehd) | pp5 | 67 | 894 | 239.6 M | -10.0 % | 138.7 M | -10.4 % | 1.73 |
| curve-heavy (curve + curvehd) | pc2 | 67 | 651 | 255.3 M | -4.1 % | 146.6 M | -5.2 % | 1.74 |
| BuseyBench (busey + buseyhd) | master | 4 | 10 | 167.2 M | +0.0 % | 109.2 M | +0.0 % | 1.53 |
| BuseyBench (busey + buseyhd) | A | 4 | 16 | 171.9 M | +2.8 % | 109.4 M | +0.2 % | 1.57 |
| BuseyBench (busey + buseyhd) | B | 4 | 19 | 168.5 M | +0.8 % | 112.2 M | +2.7 % | 1.50 |
| BuseyBench (busey + buseyhd) | C | 4 | 15 | 170.0 M | +1.7 % | 115.4 M | +5.7 % | 1.47 |
| BuseyBench (busey + buseyhd) | pp5 | 4 | 9 | 166.0 M | -0.7 % | 109.3 M | +0.1 % | 1.52 |
| BuseyBench (busey + buseyhd) | pc2 | 4 | 7 | 169.1 M | +1.2 % | 124.0 M | +13.6 % | 1.36 |

key files at this clock, instructions / cycles vs master (%):

| frame | A | B | C | pp5 | pc2 | min frames per variant |
|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | +12.0 / +14.6 | +1.4 / +9.2 | +7.2 / +17.6 | -9.5 / -3.9 | -4.1 / -1.8 | 3 |
| curvehd c_puzzle-fox z1 | +23.1 / +29.1 | +2.3 / +8.9 | +13.8 / +24.7 | -16.7 / -5.2 | -5.5 / +5.1 | 10 |
| curvehd c_mr-settodefault z1 | +17.4 / +7.9 | +1.8 / -2.3 | +11.3 / +10.1 | -13.7 / +9.7 | -5.6 / -4.3 | 2 |
| curve c_tiger z1 | +6.2 / +4.2 | -0.3 / +3.2 | +2.2 / +0.4 | -6.6 / -5.4 | -1.1 / +3.2 | 2 |
| curve c_tiger z4 | +10.8 / +5.0 | +1.1 / +1.0 | +6.7 / +10.4 | -9.0 / -10.7 | -1.7 / +3.0 | 6 |

**clock 2.2-2.7 GHz**

| group | variant | keys | frames | instr/pass | vs master | cycles/pass | vs master | IPC |
|---|---|---|---|---|---|---|---|---|
| curve-heavy (curve + curvehd) | master | 63 | 983 | 259.4 M | +0.0 % | 177.5 M | +0.0 % | 1.46 |
| curve-heavy (curve + curvehd) | A | 63 | 712 | 283.8 M | +9.4 % | 183.7 M | +3.5 % | 1.54 |
| curve-heavy (curve + curvehd) | B | 63 | 550 | 263.1 M | +1.4 % | 180.1 M | +1.4 % | 1.46 |
| curve-heavy (curve + curvehd) | C | 63 | 668 | 274.1 M | +5.6 % | 181.4 M | +2.2 % | 1.51 |
| curve-heavy (curve + curvehd) | pp5 | 63 | 519 | 235.9 M | -9.1 % | 166.5 M | -6.2 % | 1.42 |
| curve-heavy (curve + curvehd) | pc2 | 63 | 789 | 249.8 M | -3.7 % | 172.1 M | -3.0 % | 1.45 |

key files at this clock, instructions / cycles vs master (%):

| frame | A | B | C | pp5 | pc2 | min frames per variant |
|---|---|---|---|---|---|---|
| curvehd c_tiger z1 | +11.8 / +12.7 | +1.8 / +5.5 | +6.8 / +11.2 | -9.9 / -8.5 | -4.2 / -2.5 | 5 |
| curvehd c_puzzle-fox z1 | +22.0 / +7.8 | +2.1 / +2.9 | +12.9 / +16.2 | -17.2 / -9.9 | -7.1 / -3.1 | 10 |
| curvehd c_mr-settodefault z1 | +19.0 / +17.7 | +1.8 / +2.8 | +11.2 / +22.4 | -15.5 / -16.3 | -6.9 / -6.0 | 16 |
| curve c_tiger z1 | +7.3 / +0.6 | +2.2 / +8.6 | +4.4 / +3.6 | -5.5 / -8.5 | -1.3 / -2.5 | 9 |
| curve c_tiger z4 | +11.0 / +6.6 | +1.7 / +7.7 | +7.0 / +6.2 | -9.3 / -9.7 | -2.5 / -2.0 | 7 |
