import sys, numpy as np
from PIL import Image
S = sys.argv[1]
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.float64)
F = lambda n, t='mst2': L(f'{S}/png/{t}_t__{n}_z2.png')
R = lambda n, b='chr': L(f'{S}/refs/{b}_t__{n}_z2.png')
def off(a, b, t=20): return (np.abs(a - b).max(2) > t)
names = ['v_full', 'v_full_mask', 'v_full_srgb', 'v_nofilter', 'v_noglow', 'v_glow_black', 'v_glow_white', 'v_shadow_white']
for n in names:
    print(f'{n:16s} femtovg vs chr px>20: {off(F(n), R(n)).sum():5d}  px>8: {off(F(n), R(n), 8).sum():5d}')
print('femtovg v_full vs chr v_full_srgb px>20:', off(F('v_full'), R('v_full_srgb')).sum(), ' px>8:', off(F('v_full'), R('v_full_srgb'), 8).sum())
for p in [(105, 140), (100, 135), (110, 145), (105, 320), (95, 140)]:
    y, x = p
    print(p, 'fv full', F('v_full')[y, x], 'chr full', R('v_full')[y, x], 'chr srgb', R('v_full_srgb')[y, x], 'fv srgbfile', F('v_full_srgb')[y, x])
