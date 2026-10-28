import sys, numpy as np
from PIL import Image
S = sys.argv[1]
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.float64) / 255
F = lambda n, t='mst2': L(f'{S}/png/{t}_t__{n}_z2.png')
R = lambda n, b='chr': L(f'{S}/refs/{b}_t__{n}_z2.png')
dec = lambda v: np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
enc = lambda v: np.where(v <= 0.0031308, v * 12.92, 1.055 * np.clip(v, 0, None) ** (1 / 2.4) - 0.055)
bg = np.array([0x1d, 0x2a, 0x35]) / 255
for src in ('chr', 'ff'):
    gb, gw, sw = R('v_glow_black', src), R('v_glow_white', src), R('v_shadow_white', src)
    a = np.clip(1 - (gw - gb), 0, 1).mean(2, keepdims=True)     # glow alpha
    pc = gb                                                      # glow premultiplied sRGB colour a*c
    s = np.clip(1 - sw, 0, 1).mean(2, keepdims=True)             # shadow alpha
    A = a + (1 - a) * s
    c = np.where(a > 0, pc / np.maximum(a, 1e-6), 0)
    srgb = pc + (1 - A) * bg
    lin = A * enc(np.where(A > 0, a * dec(np.clip(c, 0, 1)) / np.maximum(A, 1e-6), 0)) + (1 - A) * bg
    nof = R('v_nofilter', src)
    noface = np.abs(nof - (pc + (1 - a) * bg)).max(2) < 2 / 255      # no face/ear coverage here
    band = np.zeros(noface.shape, bool); band[75:125, 100:360] = True
    sel = noface & band & (a[..., 0] > 0.02) & (s[..., 0] > 0.05)
    full = R('v_full', src); srgbref = R('v_full_srgb', src); fv = F('v_full')
    d = lambda x, y: np.abs(x - y)[sel].max(1) * 255
    print(f'[{src}] {sel.sum()} temple px (glow over shadow, no face): alpha glow {a[sel].mean():.3f} shadow {s[sel].mean():.3f}')
    print(f'  linear model vs {src} full        : mean {d(lin, full).mean():5.2f} max {d(lin, full).max():5.1f}')
    print(f'  sRGB model   vs {src} full        : mean {d(srgb, full).mean():5.2f} max {d(srgb, full).max():5.1f}')
    print(f'  sRGB model   vs {src} full (sRGB) : mean {d(srgb, srgbref).mean():5.2f} max {d(srgb, srgbref).max():5.1f}')
    print(f'  sRGB model   vs femtovg full      : mean {d(srgb, fv).mean():5.2f} max {d(srgb, fv).max():5.1f}')
    print(f'  linear model vs femtovg full      : mean {d(lin, fv).mean():5.2f} max {d(lin, fv).max():5.1f}')
    print(f'  femtovg vs {src} full             : mean {d(fv, full).mean():5.2f} max {d(fv, full).max():5.1f}  >20: {(d(fv, full) > 20).sum()}')
    y, x = 105, 140
    print('  (140,105) a', a[y, x, 0].round(3), 's', s[y, x, 0].round(3), 'lin', (lin[y, x] * 255).round(1), 'srgb', (srgb[y, x] * 255).round(1), 'ref', full[y, x] * 255, 'fv', fv[y, x] * 255)
# Femtovg's own components
gb, gw = F('v_glow_black'), F('v_glow_white')
print('femtovg glow alone vs chr: max', (np.abs(gb - R('v_glow_black')).max() * 255), (np.abs(gw - R('v_glow_white')).max() * 255))
