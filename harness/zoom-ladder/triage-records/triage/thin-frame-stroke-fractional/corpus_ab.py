# Corpus A/B of the thin-stroke profile: every compared file at every framing, patch off and on, n8 per browser.
import json, os, subprocess, sys, numpy as np, io
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
H = os.path.expanduser('~'); R = f'{H}/src/femtovg-wt/runs/zoom'; D = f'{R}/triage/thin-frame-stroke-fractional'
B = f'{D}/bin/_logos_full_thin'
ENV = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30', 'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024'}
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
paths = {f['key']: f['path'] for f in json.load(open(f'{R}/fresh/files.json'))}
keys = [json.loads(l)['key'] for l in open(f'{R}/zoomcmp_zm_svg.jsonl')]
OUT = f'{D}/corpus_ab.jsonl'
done = set()
if os.path.exists(OUT):
    done = {(r['key'], r['framing']) for r in map(json.loads, open(OUT))}
TMP = f'{D}/tmp'; os.makedirs(TMP, exist_ok=True)
def render(key, z, on):
    ppm = f'{TMP}/{os.getpid()}_{abs(hash((key, z, on)))}.ppm'
    env = {**ENV, **({'FEMTOVG_THIN_STROKE_EXACT': '1'} if on else {})}
    try:
        subprocess.run([B, f'{z:g}', ppm, paths[key]], env=env, capture_output=True, timeout=300)
        a = np.asarray(Image.open(ppm).convert('RGB'), dtype=np.int16)
    except Exception:
        return None
    finally:
        if os.path.exists(ppm): os.remove(ppm)
    return a
def job(arg):
    key, z = arg
    fr = FR[z]
    off = render(key, z, False); on = render(key, z, True)
    row = {'key': key, 'framing': fr}
    if off is None or on is None:
        row['error'] = True; return row
    row['same'] = bool((off == on).all())
    if not row['same']:
        row['moved'] = int((np.abs(off - on).max(axis=2) > 0).sum())
    for b in ['chr', 'ff', 'wk']:
        p = f'{R}/fresh/refs/{b}_{key}_{fr}.png'
        if os.path.exists(p):
            r = np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
            h, w = min(r.shape[0], off.shape[0]), min(r.shape[1], off.shape[1])
            row[f'off_{b}'] = int((np.abs(off[:h, :w] - r[:h, :w]).max(axis=2) > 8).sum())
            row[f'on_{b}'] = row[f'off_{b}'] if row['same'] else int((np.abs(on[:h, :w] - r[:h, :w]).max(axis=2) > 8).sum())
    return row
jobs = [(k, z) for k in keys for z in FR if (k, FR[z]) not in done]
with open(OUT, 'a') as out, ThreadPoolExecutor(int(os.environ.get('J', '6'))) as ex:
    for i, row in enumerate(ex.map(job, jobs)):
        out.write(json.dumps(row) + '\n'); out.flush()
        if i % 500 == 0: print(i, len(jobs), flush=True)
print('done', flush=True)
