#!/usr/bin/env python3
"""E-core counter campaign: templates T1-T3 (tpl/, manual events, 100 us sampling, CPU Counters only) x curve-heavy
files at 1080p x variants m7 (master), m7f (A), fb (B), fc (C), each under /usr/sbin/taskpolicy -c background.
Each trace is exported, summarized to counters/<tpl>_<file>_<variant>.json and deleted at once.

Summary: per-sample counter sums over (a) every sample of the process, (b) steady-state frame samples - stacks under
render_scene / flush_to_output / Queue::submit / Device::poll, minus pipeline and shader creation - and per leaf and
inclusive function sums over (b).

usage: rec_campaign.py [T1,T2,T3] [file,...] [variant,...]
"""
import collections, json, os, re, subprocess, sys
import xml.etree.ElementTree as ET

OUT = os.path.expanduser('~/src/femtovg-wt/runs/mac-anatomy')
BIN = os.path.expanduser('~/src/femtovg-wt/bin')
XCT = '/Applications/Xcode.app/Contents/Developer/usr/bin/xctrace'
ENV = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SINGLE_SHADOW_LAYER': '1',
       'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024'}
FILES = {
    'tiger': ('/Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg', 200),
    'puzzle-fox': ('/Users/matt/src/femtovg-wt/da/corpus/firefox/puzzle-fox.svg', 800),
    'mr-settodefault': ('/Users/matt/src/femtovg-wt/da/mr-settodefault.svg', 400),
    'svgenius-icon32': (f'{OUT}/files/svgenius_icon32.svg', 1200),
    'svgenius-icon5': (f'{OUT}/files/svgenius_icon5_line.svg', 1200),
}
FRAME_ROOTS = ('_logos_full::render_scene', 'femtovg::Canvas$LT$T$GT$::flush_to_output', 'wgpu::api::queue::Queue::submit',
               'wgpu::api::device::Device::poll')
STARTUP = ('create_render_pipeline', 'load_shader', 'naga::', 'create_shader_module', 'MTLCompiler', 'create_compute_pipeline')


def short(name):
    return re.sub(r'::h[0-9a-f]{16}$', '', name or '?')


def summarize(xml_path):
    ids = {}
    n = None
    tot_all = None
    tot_frame = None
    leaf = collections.defaultdict(lambda: None)
    incl = collections.defaultdict(lambda: None)
    samples = collections.Counter()
    pair = collections.defaultdict(lambda: None)

    def add(d, k, v):
        cur = d[k]
        d[k] = list(v) if cur is None else [a + b for a, b in zip(cur, v)]

    for ev, el in ET.iterparse(xml_path, events=('end',)):
        if el.get('id') is not None:
            ids[el.get('id')] = el
        if el.tag != 'row':
            continue
        proc, core, pmc, stack = '', '', None, []
        for c in el:
            if c.get('ref') is not None:
                c = ids[c.get('ref')]
            if c.tag == 'process':
                proc = c.get('fmt') or ''
            elif c.tag == 'core':
                core = c.get('fmt') or ''
            elif c.tag == 'pmc-events':
                pmc = [int(x) for x in (c.text or '').split()]
            elif c.tag in ('tagged-backtrace', 'backtrace'):
                for f in c.iter('frame'):
                    if f.get('ref') is not None:
                        f = ids[f.get('ref')]
                    stack.append(short(f.get('name')))
        if 'taskpolicy' not in proc or not pmc:
            continue
        if n is None:
            n = len(pmc)
            tot_all = [0] * n
            tot_frame = [0] * n
        ct = 'E' if 'E Core' in core else ('P' if 'P Core' in core else '?')
        samples['all_' + ct] += 1
        tot_all = [a + b for a, b in zip(tot_all, pmc)]
        joined = '\n'.join(stack)
        if ct != 'E' or not any(r in joined for r in FRAME_ROOTS) or any(s in joined for s in STARTUP):
            continue
        samples['frame'] += 1
        tot_frame = [a + b for a, b in zip(tot_frame, pmc)]
        add(leaf, stack[0] if stack else '?', pmc)
        if len(stack) > 1:
            # leaf and its nearest caller outside the allocator/memmove/std plumbing
            parent = next((f for f in stack[1:] if not re.match(r'(_?xzm|_malloc|_free|_realloc|_platform|alloc::|core::ptr|std::|_\$LT\$alloc)', f)), stack[1])
            add(pair, stack[0] + ' <- ' + parent, pmc)
        for f in set(stack):
            add(incl, f, pmc)
    top = lambda d, k: dict(sorted(d.items(), key=lambda kv: -kv[1][1])[:k])
    return {'samples': dict(samples), 'all': tot_all, 'frame': tot_frame, 'leaf': top(leaf, 250), 'incl': top(incl, 400),
            'pair': top(pair, 300)}


def events_of(tpl):
    out = subprocess.run(['plutil', '-p', f'{OUT}/tpl/{tpl}.tracetemplate'], capture_output=True, text=True).stdout
    return None


def main():
    tpls = (sys.argv[1] if len(sys.argv) > 1 else 'T1,T2,T3').split(',')
    files = (sys.argv[2] if len(sys.argv) > 2 else ','.join(FILES)).split(',')
    variants = (sys.argv[3] if len(sys.argv) > 3 else 'm7,m7f,fb,fc').split(',')
    os.makedirs(f'{OUT}/counters', exist_ok=True)
    for tpl in tpls:
        for fk in files:
            path, frames = FILES[fk]
            for v in variants:
                dst = f'{OUT}/counters/{tpl}_{fk}_{v}.json'
                if os.path.exists(dst):
                    continue
                trace = f'{OUT}/traces/{tpl}_{fk}_{v}.trace'
                envs = []
                for k, val in {**ENV, 'FRAMES': str(frames)}.items():
                    envs += ['--env', f'{k}={val}']
                r = subprocess.run(['python3', f'{OUT}/guard_record.py', f'{OUT}/tpl/{tpl}.tracetemplate', trace,
                                    '--limit-mb', '1200', *envs, '--', '/usr/sbin/taskpolicy', '-c', 'background',
                                    f'{BIN}/_logos_full_{v.split("#")[0]}', '1', f'{OUT}/tmp/rec_{v.split("#")[0]}.ppm', path],
                                   capture_output=True, text=True)
                print(tpl, fk, v, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:], flush=True)
                if 'KILLED' in r.stdout or not os.path.exists(trace):
                    subprocess.run(['rm', '-rf', trace])
                    continue
                toc = subprocess.run([XCT, 'export', '--input', trace, '--toc'], capture_output=True, text=True).stdout
                m = re.search(r'<table[^>]*schema="counters-profile"[^>]*>', toc)
                names = re.findall(r'(?:&quot;|")([A-Z][A-Z0-9_]+)(?:&quot;|")', m.group(0).split('pmc-events=')[1]) if m else []
                names = [x for x in names if x not in ('SINGLE',)][:10]
                xml = f'{OUT}/tmp/{tpl}_{fk}_{v}.xml'
                with open(xml, 'w') as fo:
                    subprocess.run([XCT, 'export', '--input', trace, '--xpath',
                                    '/trace-toc/run[@number="1"]/data/table[@schema="counters-profile"]'], stdout=fo)
                subprocess.run(['rm', '-rf', trace])
                s = summarize(xml)
                os.remove(xml)
                s.update({'events': names, 'frames': frames, 'variant': v, 'file': fk, 'template': tpl})
                json.dump(s, open(dst, 'w'))


main()
