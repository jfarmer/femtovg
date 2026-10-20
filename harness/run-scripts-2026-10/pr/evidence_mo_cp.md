mo -> cp: frames with both builds: 4652; bit-identical: 4600

| file | framing | px>20 before -> after | structural before -> after | max | Chromium vs Firefox |
|---|---|---:|---:|---:|---:|
| qwen3-8-2-4t-a95b | hd | 1.79 % -> 1.58 % | 1.200 % -> 1.026 % | 161 -> 161 | nan % |
| gpt-5-2-pro | hd | 3.43 % -> 3.23 % | 2.833 % -> 2.660 % | 146 -> 102 | 0.08 % |
| gpt-5-6-sol-pro | z4 | 3.09 % -> 3.24 % | 0.531 % -> 0.589 % | 95 -> 95 | 1.50 % |

frames differing in pixels but within 0.1 points of px>20: 49
  px>20 delta median +0.000 min -0.013 max +0.075; px>8 delta median +0.000 min -0.081 max +0.328

## cost: one process per frame, frame time ms (record + flush + GPU wait) and peak footprint MiB, by the file's largest device sigma
| sigma band | frames | frame ms before median / max | after median / max | peak footprint MiB before median / max | after median / max |
|---|---:|---:|---:|---:|---:|

slowest mo frames: file framing sigma_px frame ms base -> bd, footprint MiB base -> bd
