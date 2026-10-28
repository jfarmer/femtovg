mo -> moh: frames with both builds: 4652; bit-identical: 4617

| file | framing | px>20 before -> after | structural before -> after | max | Chromium vs Firefox |
|---|---|---:|---:|---:|---:|
| blur-drop-shadow-pipeline | z4 | 54.43 % -> 0.00 % | 52.706 % -> 0.000 % | 128 -> 0 | 0.00 % |
| morphology-edge-detection | z4 | 34.11 % -> 0.00 % | 32.756 % -> 0.000 % | 255 -> 0 | 0.00 % |
| blur-drop-shadow-pipeline | z2 | 21.41 % -> 0.00 % | 20.348 % -> 0.000 % | 128 -> 0 | 0.00 % |
| offset-composite-out | z4 | 16.30 % -> 0.00 % | 15.381 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-composite-xor | z4 | 16.30 % -> 0.00 % | 15.381 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-composite-out | z2 | 12.04 % -> 0.00 % | 11.251 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-composite-xor | z2 | 12.04 % -> 0.00 % | 11.251 % -> 0.000 % | 255 -> 0 | 0.00 % |
| morphology-edge-detection | z2 | 12.04 % -> 0.00 % | 11.251 % -> 0.000 % | 255 -> 0 | 0.00 % |
| blur-drop-shadow-pipeline | hd | 9.00 % -> 0.00 % | 8.834 % -> 0.000 % | 128 -> 0 | 0.00 % |
| blur-drop-shadow-pipeline | z1 | 5.35 % -> 0.00 % | 4.829 % -> 0.000 % | 128 -> 0 | 0.00 % |
| offset-composite-out | hd | 5.06 % -> 0.00 % | 4.938 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-composite-xor | hd | 5.06 % -> 0.00 % | 4.938 % -> 0.000 % | 255 -> 0 | 0.02 % |
| morphology-edge-detection | hd | 5.06 % -> 0.00 % | 4.938 % -> 0.000 % | 255 -> 0 | 0.03 % |
| offset-with-element-transform-rotate-90 | z4 | 3.34 % -> 0.00 % | 2.923 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-composite-out | z1 | 3.01 % -> 0.00 % | 2.622 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-composite-xor | z1 | 3.01 % -> 0.00 % | 2.622 % -> 0.000 % | 255 -> 0 | 0.00 % |
| morphology-edge-detection | z1 | 3.01 % -> 0.00 % | 2.622 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-with-parent-transform-scale | z4 | 2.26 % -> 0.00 % | 1.870 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-with-element-transform-scale | z2 | 2.17 % -> 0.00 % | 1.554 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-with-parent-transform-scale | z2 | 2.07 % -> 0.00 % | 1.483 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-with-element-transform-rotate-90 | z2 | 1.34 % -> 0.00 % | 1.084 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-triple-chain-rgb-shadow | hd | 1.27 % -> 0.00 % | 1.162 % -> 0.000 % | 255 -> 0 | 0.02 % |
| offset-with-element-transform-scale | hd | 1.27 % -> 0.00 % | 1.162 % -> 0.000 % | 255 -> 0 | 0.02 % |
| offset-triple-chain-rgb-shadow | z2 | 1.17 % -> 0.00 % | 0.883 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-with-parent-transform-scale | hd | 0.88 % -> 0.00 % | 0.787 % -> 0.000 % | 255 -> 1 | 0.04 % |
| offset-triple-chain-rgb-shadow | z1 | 0.75 % -> 0.00 % | 0.434 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-with-element-transform-scale | z1 | 0.75 % -> 0.00 % | 0.434 % -> 0.000 % | 255 -> 0 | 0.00 % |
| offset-with-element-transform-rotate-90 | hd | 0.56 % -> 0.00 % | 0.522 % -> 0.000 % | 255 -> 0 | 0.01 % |
| offset-with-parent-transform-scale | z1 | 0.55 % -> 0.00 % | 0.263 % -> 0.000 % | 255 -> 1 | 0.06 % |
| offset-with-element-transform-rotate-90 | z1 | 0.33 % -> 0.00 % | 0.214 % -> 0.000 % | 255 -> 0 | 0.00 % |

frames differing in pixels but within 0.1 points of px>20: 5
  px>20 delta median +0.000 min +0.000 max +0.000; px>8 delta median +0.000 min +0.000 max +0.000

## cost: one process per frame, frame time ms (record + flush + GPU wait) and peak footprint MiB, by the file's largest device sigma
| sigma band | frames | frame ms before median / max | after median / max | peak footprint MiB before median / max | after median / max |
|---|---:|---:|---:|---:|---:|

slowest mo frames: file framing sigma_px frame ms base -> bd, footprint MiB base -> bd
