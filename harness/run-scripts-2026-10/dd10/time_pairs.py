"""time_pairs.py: paired frame_ms/encode_ms medians, m10 vs dc10 alternating, for the cases where the degenerate fix removes work."""
import json, os, re, statistics, subprocess
f = {x['key']: x['path'] for x in json.load(open('/Users/matt/src/femtovg-wt/runs/dd10/files.json'))}
HD = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0'}
base = {**os.environ, 'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024', 'SINGLE_SHADOW_LAYER': '1', 'MEM_PEAKS': '1', 'FRAMES': '200'}
cases = [('emoji icon (svgenius page_72), 1080p', f['svgenius__page_72_32位像素风emoji_39823_icon_13'], '1'),
         ('ember logo, 1080p', f['corpus__ember'], '1'),
         ('line icon (svgenius page_679), 1080p', f['svgenius__page_679_一组常见线性ICON_1599_icon_78'], '1'),
         ('Ghostscript tiger at scale 0 (first frame of a scale-in)', f['tiger__Ghostscript_Tiger'], '0'),
         ('300 tabs rounded on top (rounded_rect_varying shape)', '/Users/matt/src/femtovg-wt/runs/dc/tabs_300.svg', '1')]
out = []
for name, path, z in cases:
    res = {'m10': [], 'dc10': []}
    for rnd in range(9):
        for b in (('m10', 'dc10') if rnd % 2 == 0 else ('dc10', 'm10')):
            r = subprocess.run([f'/Users/matt/src/femtovg-wt/bin/_logos_full_{b}', z, f'/Users/matt/src/femtovg-wt/runs/dd10/tmp/tp_{b}.ppm', path], env={**base, **HD}, capture_output=True, text=True)
            m = re.search(r'frame_ms=([\d.]+).*encode_ms=([\d.]+)', r.stderr)
            res[b].append((float(m.group(1)), float(m.group(2))))
    md = {b: (statistics.median(x[0] for x in v), statistics.median(x[1] for x in v)) for b, v in res.items()}
    row = {'case': name, 'frame': [md['m10'][0], md['dc10'][0]], 'encode': [md['m10'][1], md['dc10'][1]]}
    out.append(row)
    print(f"{name:58s} encode {md['m10'][1]:7.3f} -> {md['dc10'][1]:7.3f} ms   frame {md['m10'][0]:7.3f} -> {md['dc10'][0]:7.3f} ms", flush=True)
json.dump(out, open('/Users/matt/src/femtovg-wt/runs/dd10/time_pairs.json', 'w'))
