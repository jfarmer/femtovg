#!/usr/bin/env python3
"""The wasm crosscheck's server: serves page/, the wasm packages and the corpus, hands the page one frame at a time,
and takes back each frame's pixels and counters.

  server.py JOBS.json [port=8737]

JOBS.json: {"run_dir": DIR, "pkg_dir": DIR, "files": FILES.json, "native": NATIVE_BUILD,
            "jobs": [{"name", "build", "backend", "framings", "env": {...}, "groups": [...] | null, "keys": FILE | null,
                      "frames": 1}]}
A job's frames are every selected file at every framing, each framing's FRAME_W/BOX/... and SWEEP_ENV set as
corpus_run/accuracy.py sets them, then the job's own env. For each frame the server writes a row to
RUN_DIR/JOB/results.jsonl: the page's timings and counters, the wasm heap, device errors, the frame's hash
(as the native harness hashes its PPM) and whether it equals the native build's hash in RUN_DIR/accuracy.jsonl; a
frame that differs, or has no native hash, is kept as RUN_DIR/JOB/png/KEY_FRAMING.png with its px > 20 against the
browser references in RUN_DIR/refs. Resumable: rows already written are not handed out again.

A page that reloads mid-frame (a crash, a hang its driver broke, a lost device) says hello again: the frame it was
on is handed out once more, and after a second death is written as failed. Process samples (driver-posted pids,
sampled through procstat.py every SAMPLE_S seconds) go to RUN_DIR/JOB/procs.jsonl."""
import hashlib, json, os, struct, sys, threading, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'corpus_run'))
sys.path.insert(0, HERE)
os.environ.setdefault('CORPUS_RUN_OUT', '/nonexistent')
from common import FRAMINGS, SWEEP_ENV  # noqa: E402
import procstat  # noqa: E402

cfg = json.load(open(sys.argv[1]))
OPTS = dict(a.split('=', 1) for a in sys.argv[2:])
PORT = int(OPTS.get('port', 8737))
# bind=0.0.0.0 tls=CERT,KEY allow=192.168.7. : serve a device on the local network over TLS (WebGPU needs a secure
# context), answering only loopback and the address prefixes listed.
BIND = OPTS.get('bind', '127.0.0.1')
TLS = OPTS.get('tls')
ALLOW = tuple(p for p in OPTS.get('allow', '').split(',') if p) + ('127.0.0.1', '::1')
RUN = cfg['run_dir']
PKG = cfg['pkg_dir']
FILES = {f['key']: f for f in json.load(open(cfg['files']))}
SAMPLE_S = float(cfg.get('sample_s', 2.0))
FONTS = cfg.get('fonts', [])
lock = threading.Lock()

# The native build's frame hashes (accuracy.jsonl rows), by (key, framing).
NATIVE_BUILDS = set(cfg['native'] if isinstance(cfg['native'], list) else [cfg['native']])
NATIVE = {}
for path in cfg.get('native_rows', [f'{RUN}/accuracy.jsonl']):
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            if r.get('build') in NATIVE_BUILDS and r.get('hash'):
                NATIVE[(r['key'], r['framing'])] = r['hash']


class Job:
    def __init__(self, spec):
        self.spec = spec
        self.name = spec['name']
        self.dir = f'{RUN}/{self.name}'
        os.makedirs(f'{self.dir}/png', exist_ok=True)
        keys = set(json.load(open(spec['keys']))) if spec.get('keys') else None
        groups = set(spec['groups']) if spec.get('groups') else None
        files = [f for f in FILES.values() if (keys is None or f['key'] in keys) and (groups is None or f['group'] in groups)]
        files.sort(key=lambda f: f['key'])
        self.tasks = [(f['key'], fr) for f in files for fr in spec['framings']]
        if spec.get('probe'):
            # A probe job: one pseudo-frame the page runs as the named probe.
            self.tasks = [(f"probe__{spec['probe']}", 'z1')]
        done = set()
        self.results = f'{self.dir}/results.jsonl'
        if os.path.exists(self.results):
            for line in open(self.results):
                try:
                    r = json.loads(line)
                    done.add((r['key'], r['framing']))
                except ValueError:
                    pass
        self.pending = [t for t in self.tasks if t not in done]
        self.inflight = {}  # task -> (started, attempts)
        self.attempts = {}
        self.last_result = time.time()
        self.pids = {}
        self.last_proc = {}
        self.hello = None
        self.out = open(self.results, 'a')
        self.procs = open(f'{self.dir}/procs.jsonl', 'a')
        self.events = open(f'{self.dir}/events.jsonl', 'a')

    def task_json(self, task):
        key, framing = task
        if self.spec.get('probe'):
            return {'key': key, 'framing': framing, 'probe': self.spec['probe']}
        env, zoom = FRAMINGS[framing]
        return {'key': key, 'framing': framing, 'scale': zoom, 'dark': False, 'frames': self.spec.get('frames', 1),
                'env': {**SWEEP_ENV, **env, **self.spec.get('env', {})}, 'svg': f'/svg?key={key}'}

    def next(self):
        if not self.pending:
            return {'done': True}
        task = self.pending.pop(0)
        self.inflight[task] = time.time()
        return self.task_json(task)

    def page_reloaded(self, hello):
        self.hello = hello
        self.event({'event': 'hello', **hello})
        for task in list(self.inflight):
            del self.inflight[task]
            n = self.attempts.get(task, 0) + 1
            self.attempts[task] = n
            if n >= 2:
                self.write({'key': task[0], 'framing': task[1], 'failed': 'the page died twice on this frame',
                            'attempts': n})
            else:
                self.pending.insert(0, task)
                self.event({'event': 'retry', 'key': task[0], 'framing': task[1]})

    def write(self, row):
        row['t'] = time.time()
        self.out.write(json.dumps(row) + '\n')
        self.out.flush()
        self.last_result = row['t']

    def event(self, ev):
        ev['t'] = time.time()
        self.events.write(json.dumps(ev) + '\n')
        self.events.flush()

    def status(self):
        return {'name': self.name, 'tasks': len(self.tasks), 'pending': len(self.pending), 'inflight': len(self.inflight),
                'since_last_result_s': round(time.time() - self.last_result, 1), 'hello': self.hello}


JOBS = {j['name']: Job(j) for j in cfg['jobs']}


def px20(a, path):
    if not os.path.exists(path):
        return None
    b = np.asarray(Image.open(path).convert('RGB'), dtype=np.int16)
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    return round(100 * float((np.abs(a[:h, :w] - b[:h, :w]).max(axis=2) > 20).mean()), 3)


NATIVE_PNG = cfg.get('native_png', [])  # [[dir, prefix], ...]: the native build's frames, PREFIX + KEY_FRAMING.png


def native_png(key, framing):
    for d, prefix in NATIVE_PNG:
        p = f'{d}/{prefix}{key}_{framing}.png'
        if os.path.exists(p):
            return p
    return None


def proc_deltas(job):
    """The browser processes' counters now, and what each spent since the previous frame's result."""
    out = {}
    for pid, role in job.pids.items():
        s = procstat.sample(pid)
        if not s:
            continue
        last = job.last_proc.get(pid)
        out[role] = {'footprint': s['phys_footprint'], 'lifetime_max': s['lifetime_max_phys_footprint']}
        if last:
            out[role].update({'cpu_ms': round(s['cpu_ms'] - last['cpu_ms'], 3),
                              'instructions': s['instructions'] - last['instructions'],
                              'cycles': s['cycles'] - last['cycles']})
        job.last_proc[pid] = s
    return out


def take_result(job, header, rgba):
    key, framing = header['key'], header['framing']
    task = (key, framing)
    row = {k: v for k, v in header.items()}
    job.inflight.pop(task, None)
    with lock:
        row['procs'] = proc_deltas(job)
    if rgba is not None:
        w, h = header['w'], header['h']
        a = np.frombuffer(rgba, dtype=np.uint8).reshape(h, w, 4)
        rgb = np.ascontiguousarray(a[:, :, :3])
        ppm = f'P6\n{w} {h}\n255\n'.encode() + rgb.tobytes()
        row['hash'] = hashlib.sha1(ppm).hexdigest()
        native = NATIVE.get(task)
        row['native_hash'] = native
        row['same_as_native'] = native == row['hash'] if native else None
        rgb16 = rgb.astype(np.int16)
        material = True
        npng = native_png(key, framing)
        if npng:
            b = np.asarray(Image.open(npng).convert('RGB'), dtype=np.int16)
            if b.shape == rgb16.shape:
                d = np.abs(rgb16 - b).max(axis=2)
                row['vs_native'] = {'px0': int((d > 0).sum()), 'px2': int((d > 2).sum()), 'px8': int((d > 8).sum()),
                                    'px20': int((d > 20).sum()), 'max': int(d.max())}
                material = row['vs_native']['px8'] > 0
            else:
                row['vs_native'] = {'shape': [list(rgb16.shape), list(b.shape)]}
        if material:
            Image.fromarray(rgb).save(f'{job.dir}/png/{key}_{framing}.png')
            row['vs'] = {b: px20(rgb16, f'{RUN}/refs/{b}_{key}_{framing}.png') for b in ('chr', 'ff', 'wk')}
    with lock:
        job.write(row)


class Handler(BaseHTTPRequestHandler):
    # Keep-alive, and no Nagle: headers and body go out as two writes, and on macOS Nagle's wait for the delayed ACK
    # of the first held every response about 200 ms (Chromium's frame round trip went from ~6 ms to ~220).
    protocol_version = 'HTTP/1.1'

    def setup(self):
        super().setup()
        import socket
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def log_message(self, *args):
        pass

    def parse_request(self):
        if not super().parse_request():
            return False
        if not self.client_address[0].startswith(ALLOW):
            self.send_error(403)
            return False
        return True

    def send(self, code, body, ctype='application/json'):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        # Cross-origin isolation: precise timers and performance.measureUserAgentSpecificMemory where offered.
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.end_headers()
        self.wfile.write(body)

    def file(self, path, ctype):
        if not os.path.isfile(path):
            return self.send(404, {'error': 'not found'})
        self.send(200, open(path, 'rb').read(), ctype)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        p = u.path
        if p in ('/', '/index.html'):
            return self.file(f'{HERE}/page/index.html', 'text/html')
        if p == '/run.js':
            return self.file(f'{HERE}/page/run.js', 'text/javascript')
        if p.startswith('/pkg/'):
            rel = os.path.normpath(p[len('/pkg/'):])
            if rel.startswith('..'):
                return self.send(403, {'error': 'path'})
            ctype = 'application/wasm' if rel.endswith('.wasm') else 'text/javascript'
            return self.file(f'{PKG}/{rel}', ctype)
        if p == '/fonts.json':
            return self.send(200, [f'/font?i={i}' for i in range(len(FONTS))])
        if p == '/font':
            return self.file(FONTS[int(q['i'])], 'application/octet-stream')
        if p == '/svg':
            f = FILES.get(q.get('key'))
            return self.file(f['path'], 'image/svg+xml') if f else self.send(404, {'error': 'key'})
        if p == '/job':
            job = JOBS.get(q.get('job'))
            return self.send(200, job.spec) if job else self.send(404, {'error': 'job'})
        if p == '/next':
            job = JOBS[q['job']]
            with lock:
                return self.send(200, job.next())
        if p == '/status':
            return self.send(200, [j.status() for j in JOBS.values()])
        return self.send(404, {'error': 'no route'})

    def do_POST(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        n = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(n)
        job = JOBS.get(q.get('job'))
        if job is None:
            return self.send(404, {'error': 'job'})
        if u.path == '/hello':
            with lock:
                job.page_reloaded(json.loads(body))
            return self.send(200, {'ok': True})
        if u.path == '/event':
            with lock:
                job.event(json.loads(body))
            return self.send(200, {'ok': True})
        if u.path == '/pids':
            with lock:
                job.pids = {int(k): v for k, v in json.loads(body).items()}
            return self.send(200, {'ok': True})
        if u.path == '/result':
            (hlen,) = struct.unpack('<I', body[:4])
            header = json.loads(body[4:4 + hlen])
            rgba = body[4 + hlen:] if len(body) > 4 + hlen else None
            take_result(job, header, rgba)
            return self.send(200, {'ok': True})
        return self.send(404, {'error': 'no route'})


def gpu_stats():
    """The GPU's PerformanceStatistics (IOAccelerator): utilisation and the memory its driver has in use, system-wide."""
    import re, subprocess
    try:
        out = subprocess.run(['ioreg', '-r', '-d', '1', '-c', 'IOAccelerator'], capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return None
    m = re.search(r'"PerformanceStatistics" = \{([^}]*)\}', out)
    if not m:
        return None
    stats = dict(re.findall(r'"([^"]+)"=(\d+)', m.group(1)))
    keep = ('Device Utilization %', 'Renderer Utilization %', 'Tiler Utilization %', 'In use system memory', 'Alloc system memory')
    return {k: int(stats[k]) for k in keep if k in stats}


def sampler():
    while True:
        time.sleep(SAMPLE_S)
        gpu = gpu_stats()
        for job in JOBS.values():
            if not job.pids:
                continue
            row = {'t': time.time(), 'pending': len(job.pending), 'gpu': gpu, 'procs': {}}
            for pid, role in job.pids.items():
                s = procstat.sample(pid)
                if s:
                    row['procs'][role] = {k: s[k] for k in ('phys_footprint', 'lifetime_max_phys_footprint',
                                                            'interval_max_phys_footprint', 'cpu_ms', 'instructions',
                                                            'cycles', 'resident_size')}
            with lock:
                job.procs.write(json.dumps(row) + '\n')
                job.procs.flush()


threading.Thread(target=sampler, daemon=True).start()
httpd = ThreadingHTTPServer((BIND, PORT), Handler)
if TLS:
    import ssl
    cert, key = TLS.split(',')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
print(f'serving on {"https" if TLS else "http"}://{BIND}:{PORT}/ ({len(JOBS)} jobs, '
      f'{sum(len(j.pending) for j in JOBS.values())} frames pending, {len(NATIVE)} native hashes)', flush=True)
httpd.serve_forever()
