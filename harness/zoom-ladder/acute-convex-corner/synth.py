# Synthetic triangles in device coordinates of the default framing at zoom 3:
# device X = 3x - 70, Y = 3y - 170 for SVG user units in a 200x200 viewBox.
import sys, json, numpy as np
from PIL import Image
sys.path.insert(0, '.')
from area import coverage
def svg_for(tri):
    u = [((X+70)/3, (Y+170)/3) for X, Y in tri]
    d = 'M ' + ' L '.join(f'{x:.6f} {y:.6f}' for x, y in u) + ' Z'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="#FFFFFF"/><path d="{d}" fill="#008000"/></svg>\n'
cases = {}
for dy in [0, 0.25, 0.5, 0.75]:
    cases[f'flat_dy{dy}'] = [(40, 130+dy), (420, 130+dy), (230, 133+dy)]
for dx in [0.3]:
    cases[f'flat_dx{dx}_dy0.4'] = [(40+dx, 130.4), (420+dx, 130.4), (230+dx, 133.4)]
# tilted thin triangle, tips on canvas
cases['tilt'] = [(30.2, 100.3), (430.7, 160.1), (231.1, 133.9)]
# 5 deg-ish isoceles sliver, apex left
cases['acute5'] = [(60.3, 130.2), (260.3, 121.45), (260.3, 138.95)]
# 2 deg
cases['acute2'] = [(60.3, 130.2), (300.3, 126.0), (300.3, 134.4)]
if __name__ == '__main__':
    for k, tri in cases.items():
        open(f'exp/s_{k}.svg', 'w').write(svg_for(tri))
        a = coverage(tri)
        g = np.array([0, 128, 0.]); w = np.array([255, 255, 255.])
        img = w*(1-a[..., None]) + g*a[..., None]
        Image.fromarray(np.round(img).astype(np.uint8)).save(f'exp/s_{k}_area.png')
    json.dump(cases, open('exp/synth_cases.json', 'w'))
    print(list(cases))
