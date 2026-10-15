#!/usr/bin/env python3
"""Repeat #389's atlas experiment with the existing demo-assets harness.

Run stages explicitly: setup, smoke, build-swash, tests, refs, accuracy,
pixels, perf, instructions, memory, soak, counters, comparisons.
POC_RUN_DIR holds src/{master,p389,poc2389}, bin, target and results.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent
CHECKOUT = HARNESS.parent
RUN = Path(os.environ.get('POC_RUN_DIR', CHECKOUT.parent))
OUT = RUN / 'results'
BIN = RUN / 'bin'
CORPUS = HARNESS / 'corpus_run'
LOGS = OUT / 'logs'
ENV = {
    **os.environ,
    'HARNESS_BIN': str(BIN),
    'CORPUS_RUN_OUT': str(OUT),
    'CARGO_TARGET_DIR': str(RUN / 'target'),
    'CARGO_PROFILE_RELEASE_DEBUG': '0',
    'CARGO_NET_OFFLINE': 'true',
    'FIREFOX': '/Applications/Firefox.app/Contents/MacOS/firefox',
}
BUILDS = ['m15', 'p15', 'a15', 'm15sw', 'p15sw', 'a15sw']
PAIRS = [('m15', 'p15'), ('p15', 'a15'), ('m15sw', 'p15sw'), ('p15sw', 'a15sw')]
for p in (OUT, OUT / 'tmp', LOGS, BIN):
    p.mkdir(parents=True, exist_ok=True)


def call(label, args, extra=None, cwd=None):
    print(datetime.datetime.now().isoformat(timespec='seconds'), label, flush=True)
    with (LOGS / f'{label}.log').open('a') as log:
        for cmd in [('uptime',), ('ps', '-Ao', 'pid,pcpu,comm')]:
            log.write(subprocess.check_output(cmd, text=True))
        log.write('\nCOMMAND ' + repr(list(map(str, args))) + '\n')
        log.flush()
        r = subprocess.run(list(map(str, args)), cwd=cwd or CHECKOUT,
                           env={**ENV, **(extra or {})}, stdout=log, stderr=subprocess.STDOUT)
    if r.returncode:
        print((LOGS / f'{label}.log').read_text()[-5000:], flush=True)
        raise SystemExit(f'{label}: exit {r.returncode}')


def py(label, script, *args, extra=None):
    call(label, [sys.executable, CORPUS / script, *args], extra)


def setup():
    py('files', 'files.py')
    fs = json.loads((OUT / 'files.json').read_text())
    text = [f['key'] for f in fs if re.search(r'<text\b', Path(f['path']).read_text(errors='replace'))]
    gradient = [k for k in text if 'gradient' in k or k.endswith('__native-canvas')]
    controls = [f['key'] for f in fs if f['key'].endswith(('__Ghostscript_Tiger', '__gui-input-test', '__fill-opacity-overlap'))]
    for name, keys in [('text_keys', text), ('gradient_keys', gradient), ('perf_keys', sorted(set(gradient + controls)))]:
        (OUT / f'{name}.json').write_text(json.dumps(keys, indent=2) + '\n')
    (OUT / 'text_frames.txt').write_text(''.join(f'{k} {fr}\n' for k in text for fr in ('z1', 'z2', 'z4', 'hd')))
    jobs = [
        'corpus__babylon__gui-gradient-linear:hd',
        'corpus__babylon__gui-gradient-linear:z2',
        'corpus__babylon__native-canvas:z2',
        'corpus__text-probes__gradient-across-runs:z2',
        'corpus__text-probes__gradient-bbox-units:z2',
        'corpus__text-probes__gradient-in-layers:z2',
        'corpus__text-probes__gradient-radial:z05',
        'corpus__text-probes__gradient-fade:z05',
        'corpus__text-probes__gradient-stroke:z05',
        'corpus__text-probes__gradient-size-threshold:z05',
        'corpus__text-probes__gradient-transformed-groups:z2',
        'corpus__babylon__gui-input-test:z2',
        'corpus__text-probes__fill-opacity-overlap:z1',
        'tiger__Ghostscript_Tiger:z1',
    ]
    known = {f['key'] for f in fs}
    assert all(j.rsplit(':', 1)[0] in known for j in jobs)
    (OUT / 'instruction_jobs.json').write_text(json.dumps(jobs, indent=2) + '\n')
    # Reuse the previous paired instruction counter; only relocate its imports
    # and temporary output. The measurement and pairing are unchanged.
    old = Path('/Users/jesse/github/femtovg-demo-assets/harness/fill-fringe-spikes-2026-10-12/text-atlas-poc/perf/check')
    read_tool = lambda name: ((old / name) if (old / name).exists() else (HERE / 'tools' / name)).read_text()
    s = read_tool('interleaved.py')
    s = s.replace("sys.path.insert(0, '/Users/jesse/github/femtovg-demo-assets/harness/corpus_run')",
                  "sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'corpus_run'))")
    s = s.replace("ppm = f'{HERE}/tmp_{os.getpid()}.ppm'", "ppm = f'{os.environ[\"CORPUS_RUN_OUT\"]}/tmp/instr_{os.getpid()}.ppm'")
    (HERE / 'tools/interleaved.py').write_text(s)
    s = read_tool('pair.py')
    s = re.sub(r"S = '[^']+'", "BEFORE, AFTER = os.environ['POC_BEFORE'], os.environ['POC_AFTER']", s)
    s = s.replace("f'{S}/poc/changed_frames.json'", "os.environ['POC_CHANGED']")
    s = s.replace("(key, framing, 'mbase')", '(key, framing, BEFORE)')
    s = s.replace("(key, framing, 'poc')", '(key, framing, AFTER)')
    s = s.replace("if b == 'mbase'", 'if b == BEFORE')
    s = s.replace("f'{os.path.dirname(os.path.abspath(__file__))}/paired_{name}.json'",
                  "f'{os.environ[\"CORPUS_RUN_OUT\"]}/paired_{name}.json'")
    (HERE / 'tools/pair.py').write_text(s)
    s = read_tool('short_runs.py')
    s = s.replace("sys.path.insert(0, '/Users/jesse/github/femtovg-demo-assets/harness/corpus_run')",
                  "sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'corpus_run'))")
    s = s.replace("BUILD_NAMES = ('mbase', 'poc')", "BUILD_NAMES = tuple(os.environ['POC_BUILDS'].split(','))")
    s = s.replace("ppm = f'{HERE}/tmp_{os.getpid()}.ppm'", "ppm = f'{os.environ[\"CORPUS_RUN_OUT\"]}/tmp/cold_{os.getpid()}.ppm'")
    (HERE / 'tools/short_runs.py').write_text(s)
    meta = {'date': datetime.datetime.now().isoformat(), 'builds': {}, 'harness': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=CHECKOUT, text=True).strip()}
    for name, src in [('master', 'master'), ('p389', 'p389'), ('poc2389', 'poc2389')]:
        path = RUN / 'src' / src
        meta['builds'][name] = {
            'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=path, text=True).strip(),
            'diff': subprocess.check_output(['git', 'diff'], cwd=path, text=True),
        }
    for cmd in [('rustc', '-Vv'), ('sw_vers',), ('sysctl', '-n', 'machdep.cpu.brand_string'), ('sysctl', '-n', 'hw.memsize')]:
        meta[' '.join(cmd)] = subprocess.check_output(cmd, text=True).strip()
    (OUT / 'manifest.json').write_text(json.dumps(meta, indent=2) + '\n')


def build_swash():
    specs = [f'{b}:{RUN}/src/{s}' for b, s in zip(BUILDS[3:], ['master', 'p389', 'poc2389'])]
    call('build_swash', ['bash', HARNESS / 'build.sh', *specs], {'HARNESS_FEATURES': 'wgpu,swash'})


def smoke():
    fs = json.loads((OUT / 'files.json').read_text())
    scene = next(f['path'] for f in fs if f['key'].endswith('__gui-gradient-linear'))
    for b in BUILDS:
        if not (BIN / f'_logos_full_{b}').exists():
            continue
        call('smoke_' + b, [BIN / f'_logos_full_{b}', '1', OUT / 'tmp' / f'{b}.ppm', scene],
             {'LAYER_STATS': '1', 'SINGLE_SHADOW_LAYER': '1'})
        assert 'text=true' in (LOGS / f'smoke_{b}.log').read_text()
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in BIN.glob('_logos_full_*') if p.is_file()}
    (OUT / 'binary-sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')


def tests():
    src = RUN / 'src/poc2389'
    call('format', ['cargo', 'fmt', '--check'], cwd=src)
    call('tests_wgpu', ['cargo', 'test', '--release', '--features', 'wgpu', '--no-fail-fast'], cwd=src)
    call('tests_swash', ['cargo', 'test', '--release', '--lib', '--features', 'wgpu,swash'], cwd=src)


def refs():
    for browser in ['chromium', 'firefox']:
        py('refs_' + browser, 'refs.py', browser, 'keys=' + str(OUT / 'text_keys.json'),
           'framings=z01,z025,z05,z1,z2,z4,zt2,zt4,hd')


def accuracy():
    for b in BUILDS:
        py('accuracy_' + b, 'accuracy.py', b, 'keys=' + str(OUT / 'text_keys.json'),
           'framings=z01,z025,z05,z1,z2,z4,zt2,zt4,hd', 'png=' + str(OUT / 'png'))


def pixels():
    py('pixels_all', 'run.py', 'pixels', ','.join(BUILDS))


def perf():
    for a, b in PAIRS:
        for mode, frames, keys, reps in [
            ('text', 50, 'text_keys', 3),
            ('cold', 1, 'perf_keys', 5),
            ('short', 20, 'perf_keys', 5),
            ('long', 220, 'perf_keys', 5),
            ('drift_short', 20, 'perf_keys', 5),
            ('drift_long', 60, 'perf_keys', 5),
        ]:
            name = f'timing_{a}_{b}_{mode}'
            args = ['pass_time.py', a, b, f'frames={frames}', f'repeats={reps}',
                    'keys=' + str(OUT / f'{keys}.json'), 'framings=z1,z2,z4,hd', f'out={name}']
            if mode.startswith('drift'):
                args.append('env=FRAME_DRIFT=0.37')
            py(name, *args)


def instructions():
    jobs = json.loads((OUT / 'instruction_jobs.json').read_text())
    for a, b in PAIRS + [('p15', 'p15'), ('p15sw', 'p15sw')]:
        chosen = jobs if a != b else [jobs[1], jobs[3], jobs[11]]
        label = f'instructions_{a}_{b}'
        call(label, [sys.executable, HERE / 'tools/interleaved.py', OUT / f'{label}.json', '3', a, b, '--', *chosen])
    call('cold_instructions', [sys.executable, HERE / 'tools/short_runs.py', OUT / 'cold_instructions.json', '3',
                              *[jobs[i] for i in (0, 1, 2, 3, 4, 6, 12)]],
         {'POC_BUILDS': ','.join(BUILDS)})


def memory():
    for rep in range(3):
        dest = OUT / f'memory-r{rep}'
        dest.mkdir(exist_ok=True)
        shutil.copyfile(OUT / 'files.json', dest / 'files.json')
        if not (dest / 'refs').exists():
            (dest / 'refs').symlink_to(OUT / 'refs', target_is_directory=True)
        py(f'memory_r{rep}', 'run.py', 'memory', ','.join(BUILDS), OUT / 'text_frames.txt',
           extra={'CORPUS_RUN_OUT': str(dest)})


def soak():
    for b in BUILDS:
        py('soak_' + b, 'soak.py', 'run', b, 'hd')
    py('soak_summary', 'soak.py', 'report')


def counters():
    for b, src in zip(BUILDS, ['master', 'p389', 'poc2389'] * 2):
        tree = RUN / 'src' / src
        call('instrument_' + b, [sys.executable, CORPUS / 'pass_count.py', tree, 'apply'])
        try:
            call('counter_build_' + b, ['bash', HARNESS / 'build.sh', f'count_{b}:{tree}'],
                 {'HARNESS_FEATURES': 'wgpu,swash' if b.endswith('sw') else 'wgpu',
                  'EXTRA_CFGS': '--cfg harness_pass_count --cfg harness_alloc_count'})
        finally:
            call('uninstrument_' + b, [sys.executable, CORPUS / 'pass_count.py', tree, 'revert'])
    # run.py already records pass counts, memory and frame hashes. Its optional
    # ALLOC fields now preserve the existing harness allocator diagnostics too.
    py('counter_samples', 'run.py', 'memory', ','.join('count_' + b for b in BUILDS),
       OUT / 'text_frames.txt', extra={'FRAMES': '6'})


def comparisons():
    rows = [json.loads(l) for l in (OUT / 'accuracy.jsonl').open()]
    by = {(r['build'], r['key'], r['framing']): r for r in rows}
    for a, b in PAIRS:
        py(f'accuracy_compare_{a}_{b}', 'ab_refs.py', a, b, 'refs=chr,ff', 'worst=20')
        changed = [{'key': k, 'framing': f} for bb, k, f in by if bb == a
                   and (b, k, f) in by and by[(a, k, f)].get('hash') != by[(b, k, f)].get('hash')]
        (OUT / f'changed_{a}_{b}.json').write_text(json.dumps(changed, indent=2) + '\n')


def gl_checks():
    specs = [f'{b}:{RUN}/src/{s}' for b, s in zip(BUILDS[:3], ['master', 'p389', 'poc2389'])]
    call('gl_builds', ['bash', HARNESS / 'build.sh', '--gl', *specs],
         {'GL_EXAMPLES': 'gl_svg_dump gl_clip_check'})
    for b in BUILDS[:3]:
        call('gl_clip_' + b, [BIN / f'gl_clip_check_{b}'])
    wanted = set(json.loads((OUT / 'text_keys.json').read_text()))
    scenes = [f['path'] for f in json.loads((OUT / 'files.json').read_text()) if f['key'] in wanted]
    for a, b in PAIRS[:2]:
        call(f'gl_text_{a}_{b}', [sys.executable, HARNESS / 'clip-bench/gl_dump_ab.py', a, b,
                                '0.1953125,1,2,3', *scenes])


def timing_summary():
    for a, b in PAIRS:
        call(f'paired_{a}_{b}_text', [sys.executable, HERE / 'tools/pair.py',
             OUT / f'timing_{a}_{b}_text.jsonl'],
             {'POC_BEFORE': a, 'POC_AFTER': b, 'POC_CHANGED': str(OUT / f'changed_{a}_{b}.json')})
        for short, long in [('short', 'long'), ('drift_short', 'drift_long')]:
            call(f'paired_{a}_{b}_{short}', [sys.executable, HERE / 'tools/pair.py',
                 OUT / f'timing_{a}_{b}_{short}.jsonl', OUT / f'timing_{a}_{b}_{long}.jsonl'],
                 {'POC_BEFORE': a, 'POC_AFTER': b, 'POC_CHANGED': str(OUT / f'changed_{a}_{b}.json')})


def figures():
    rows = [
        'gui-gradient-linear:hd:box=910,284,104,30:zoom=3;Click Me',
        'gui-gradient-linear:hd:box=895,494,130,34:zoom=3;Some Text',
        'native-canvas:z2:size=150x46:zoom=3',
        'native-canvas:z1:size=150x46:zoom=3',
        'gradient-bbox-units:z2:size=150x46:zoom=2',
        'native-canvas:z05:size=150x46:zoom=4',
    ]
    labels = {'m15': 'master', 'p15': '#389', 'a15': '#389 + atlas',
              'm15sw': 'master, swash', 'p15sw': '#389, swash', 'a15sw': '#389 + atlas, swash'}
    for a, b in PAIRS:
        py(f'figure_{a}_{b}', 'sheet.py', OUT / f'{a}-{b}.png', f'{a}={labels[a]}', f'{b}={labels[b]}',
           '--refs=chr,ff', *rows)


def history_check():
    # The six-frame instrumented snapshots differed from the first-frame
    # snapshots in this one corpus file on all three variants. Check whether
    # the same difference occurs without instrumentation, using run.py again.
    dest = OUT / 'history-check'
    dest.mkdir(exist_ok=True)
    fs = json.loads((OUT / 'files.json').read_text())
    fs = [f for f in fs if f['key'].endswith('__loading-gltf-model-with-ktx2-textures')]
    assert len(fs) == 1
    (dest / 'files.json').write_text(json.dumps(fs, indent=2) + '\n')
    py('history_check', 'run.py', 'pixels', ','.join(BUILDS),
       extra={'CORPUS_RUN_OUT': str(dest), 'FRAMES': '6'})


def timing_noise():
    # One unchanged Tiger control moved by 15% in wall time. Measure the same
    # binary against an alias using pass_time.py, retaining its paired rows.
    fs = json.loads((OUT / 'files.json').read_text())
    names = ['__gui-gradient-linear', '__gradient-bbox-units', '__gui-input-test', '__Ghostscript_Tiger']
    keys = [f['key'] for f in fs if any(f['key'].endswith(n) for n in names)]
    assert len(keys) == 4
    (OUT / 'noise_keys.json').write_text(json.dumps(keys, indent=2) + '\n')
    (OUT / 'noise_changed.json').write_text('[]\n')
    for b, alias in [('p15', 'noise15'), ('p15sw', 'noise15sw')]:
        p = BIN / f'_logos_full_{alias}'
        if not p.exists():
            p.symlink_to(f'_logos_full_{b}')
        assert hashlib.sha256(p.read_bytes()).digest() == hashlib.sha256((BIN / f'_logos_full_{b}').read_bytes()).digest()
        name = f'timing_noise_{b}'
        py(name, 'pass_time.py', b, alias, 'frames=220', 'repeats=7',
           'keys=' + str(OUT / 'noise_keys.json'), 'framings=z2,hd', f'out={name}')
        call('paired_noise_' + b, [sys.executable, HERE / 'tools/pair.py', OUT / f'{name}.jsonl'],
             {'POC_BEFORE': b, 'POC_AFTER': alias, 'POC_CHANGED': str(OUT / 'noise_changed.json')})
    # A light Swash control had a 12% instruction-count change in two of
    # three pairs. Repeat just that case and compare each binary with itself.
    control = 'corpus__text-probes__fill-opacity-overlap:z1'
    for a, b, job in [('p15sw', 'a15sw', control), ('p15sw', 'p15sw', control),
                      ('a15sw', 'a15sw', control),
                      ('m15sw', 'p15sw', 'corpus__babylon__gui-gradient-linear:z2')]:
        label = f'instruction_check_{a}_{b}'
        call(label, [sys.executable, HERE / 'tools/interleaved.py', OUT / f'{label}.json', '7', a, b, '--', job])


def soak_repeats():
    # The first default atlas soak peaked about 1 GiB above #389. Repeat
    # the existing complete soak rather than attributing a single peak.
    for rep in (1, 2):
        dest = OUT / f'soak-r{rep}'
        dest.mkdir(exist_ok=True)
        shutil.copyfile(OUT / 'files.json', dest / 'files.json')
        for b in BUILDS:
            py(f'soak_r{rep}_{b}', 'soak.py', 'run', b, 'hd', extra={'CORPUS_RUN_OUT': str(dest)})
        py(f'soak_r{rep}_summary', 'soak.py', 'report', extra={'CORPUS_RUN_OUT': str(dest)})


if __name__ == '__main__':
    for stage in sys.argv[1:]:
        globals()[stage.replace('-', '_')]()
