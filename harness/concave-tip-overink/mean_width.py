#!/usr/bin/env python3
"""The mean width #408's gate takes - twice the area over the perimeter, in device pixels (src/path/cache.rs
mean_width, src/clip/fill.rs is_thin: under 2 px for a concave fill) - and the bounds it checks against
THIN_FILL_SPAN (65,536 px), for the crescents of the issue, at z1 (0.1953125 px a unit), z2 (0.390625) and hd
(1.0546875)."""
import re
import numpy as np

PATHS = {
    'wedge.svg': 'M 280 725 L 512 841 L 744 725 L 512 811 Z',
    'lip.svg; gemini-3-1-pro-preview.svg line 293 (lower lip)':
        'M 280 725 C 344 880, 680 880, 744 725 C 680 840, 344 840, 280 725 Z',
    'gemini-3-7-flash.svg line 562 (lip crescent)':
        'M 345 645 C 380 710 430 762 512 762 C 594 762 644 710 679 645 C 654 715 594 772 512 772 C 430 772 370 715 345 645 Z',
    'grok-4-5.svg line 153 (lower hair spike)': 'M220 400 Q130 340 80 260 Q120 330 180 390 Q210 410 220 400Z',
    'gemini-3-1-pro-preview-custom-tools.svg line 279 (eye-top shadow)': 'M 350 475 Q 410 430 465 480 Q 410 450 350 475 Z',
    'gemini-3-1-pro-preview-custom-tools.svg line 411 (upper lip)': 'M 355 760 Q 512 705 675 730 Q 512 725 355 760 Z',
    'gemini-3-1-pro-preview-custom-tools.svg line 416 (lower lip)': 'M 355 760 Q 512 890 675 730 Q 512 860 355 760 Z',
}


def outline(d, n=256):
    t = re.findall(r'[MLCQZ]|-?[\d.]+', d)
    pts, i, cur, cmd = [], 0, None, None
    num = lambda k: np.array([float(t[i + k]), float(t[i + k + 1])])
    while i < len(t):
        if t[i] in 'MLCQZ':
            cmd = t[i]; i += 1
            if cmd == 'Z':
                continue
        if cmd == 'M':
            cur = num(0); pts.append(cur); i += 2; cmd = 'L'
        elif cmd == 'L':
            cur = num(0); pts.append(cur); i += 2
        elif cmd == 'Q':
            a, p = num(0), num(2)
            s = np.linspace(0, 1, n + 1)[1:, None]
            pts += list((1 - s) ** 2 * cur + 2 * (1 - s) * s * a + s * s * p); cur = p; i += 4
        elif cmd == 'C':
            a, b, p = num(0), num(2), num(4)
            s = np.linspace(0, 1, n + 1)[1:, None]
            pts += list((1 - s) ** 3 * cur + 3 * (1 - s) ** 2 * s * a + 3 * (1 - s) * s * s * b + s ** 3 * p); cur = p; i += 6
    return np.array(pts)


for name, d in PATHS.items():
    p = outline(d)
    q = np.roll(p, -1, 0)
    twice_area = abs((p[:, 0] * q[:, 1] - q[:, 0] * p[:, 1]).sum())
    perimeter = np.hypot(*(q - p).T).sum()
    for framing, scale in (('z1', 0.1953125), ('z2', 0.390625), ('hd', 1.0546875)):
        w, h = (p.max(0) - p.min(0)) * scale
        print(f'{name:68s} {framing}: mean width {twice_area / perimeter * scale:5.2f} px, bounds {w * h:7.0f} px')
