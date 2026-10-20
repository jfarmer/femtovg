"""hashes.py TAG_A TAG_B FRAMES [FRAMING...]  - both harness builds over the whole corpus list (runs/pr/files.json) and
the clip-bench pages, at each framing (default hd and z1), FRAMES frames a run: the SHA-256 of the frame each
writes. Prints how many frames are identical and lists the ones that differ; rows go to hashes_A_B.jsonl."""
import glob, hashlib, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
R = '/Users/matt/src/femtovg-wt/runs/pmemo'; BIN = '/Users/matt/src/femtovg-wt/bin'
DEFAULT = {'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
HD = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0'}
FRAMINGS = {'z1': (DEFAULT, 1.0), 'z2': (DEFAULT, 2.0), 'z4': (DEFAULT, 4.0), 'hd': (HD, 1.0)}
SWEEP = {'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'LAYER_STATS': '1', 'TRANSIENT_BUDGET_MB': '1024'}
a, b, frames = sys.argv[1], sys.argv[2], sys.argv[3]
framings = sys.argv[4:] or ['hd', 'z1']
files = json.load(open('/Users/matt/src/femtovg-wt/runs/pr/files.json'))
files += [{'key': 'clip-bench__' + os.path.basename(p)[:-4], 'path': p} for p in sorted(glob.glob('/Users/matt/src/femtovg-wt/da/harness/clip-bench/*.svg'))]
def shot(build, f, framing, slot):
    env, zoom = FRAMINGS[framing]
    ppm = f'{R}/hash_{os.getpid()}_{slot}_{build}.ppm'
    try:
        r = subprocess.run([f'{BIN}/_logos_full_{build}', f'{zoom:g}', ppm, f['path']], env={**os.environ, **env, **SWEEP, 'FRAMES': frames},
                           capture_output=True, text=True, timeout=900)
        if r.returncode != 0 or not os.path.exists(ppm):
            return f'failed({r.returncode})', False
        cfgs = 'harness cfgs: clip=true turbulence=true blend=true mix_blend=true' in r.stderr
        return hashlib.sha256(open(ppm, 'rb').read()).hexdigest(), cfgs
    except subprocess.TimeoutExpired:
        return 'timeout', False
    finally:
        if os.path.exists(ppm):
            os.remove(ppm)
def job(args):
    i, f, framing = args
    (ha, ca), (hb, cb) = shot(a, f, framing, f'{i}_{framing}'), shot(b, f, framing, f'{i}_{framing}')
    return {'key': f['key'], 'framing': framing, a: ha, b: hb, 'cfgs': ca and cb}
jobs = [(i, f, framing) for framing in framings for i, f in enumerate(files)]
out = open(f'{R}/hashes_{a}_{b}.jsonl', 'w')
same = diff = failed = nocfg = 0; differing = []
with ThreadPoolExecutor(6) as ex:
    for row in ex.map(job, jobs):
        out.write(json.dumps(row) + '\n')
        if len(row[a]) != 64 or len(row[b]) != 64:
            failed += 1; differing.append(row)
        elif row[a] == row[b]:
            same += 1
        else:
            diff += 1; differing.append(row)
        nocfg += not row['cfgs']
print(f"{a} vs {b}, {frames} frames a run, framings {' '.join(framings)}: {len(jobs)} frames of {len(files)} files: {same} identical, {diff} differ, {failed} failed; {nocfg} runs without the full-cfg line")
for row in differing[:40]:
    print('  ', row['key'], row['framing'], row[a][:16], row[b][:16])
