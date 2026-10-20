#!/usr/bin/env python3
"""Runs crosscheck jobs in Safari itself: on the Mac (Safari.app, the job page opened as a tab with `open -a Safari`)
or on an attached iOS device (Safari launched with the page's URL through `xcrun devicectl`). Safari cannot be
scripted without remote automation, so the page drives itself; this script only opens it, tells the server which
processes to sample (Mac: the WebContent processes that appeared with the tab, and every WebKit GPU process, the
one that works being Safari's), and opens the page again when it stops returning frames.

  drive_safari.py SERVER_URL JOB [JOB...]                   (Safari.app)
  drive_safari.py --device UDID SERVER_URL JOB [JOB...]     (Safari on an iOS device)
Environment: STALL_S (default 180)."""
import json, os, subprocess, sys, time, urllib.request

args = sys.argv[1:]
device = None
if args[0] == '--device':
    device, args = args[1], args[2:]
server, jobs = args[0], args[1:]
STALL_S = float(os.environ.get('STALL_S', 180))


def pids(name):
    out = subprocess.run(['pgrep', '-f', name], capture_output=True, text=True).stdout
    return {int(p) for p in out.split()}


def status(job):
    with urllib.request.urlopen(f'{server}/status', context=_ctx()) as r:
        return next((j for j in json.load(r) if j['name'] == job), None)


def _ctx():
    import ssl
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE  # our own self-signed certificate for the device's server
    return c


def post(path, body):
    req = urllib.request.Request(f'{server}{path}', data=json.dumps(body).encode(), method='POST')
    urllib.request.urlopen(req, context=_ctx()).read()


def open_page(job):
    url = f'{server}/?job={job}'
    if device:
        subprocess.run(['xcrun', 'devicectl', 'device', 'process', 'launch', '--device', device, '--payload-url', url,
                        'com.apple.mobilesafari'], capture_output=True, text=True)
    else:
        subprocess.run(['open', '-a', 'Safari', url])


for job in jobs:
    before = pids('com.apple.WebKit.WebContent')
    open_page(job)
    opened = time.time()
    mine = set()
    while True:
        time.sleep(5)
        s = status(job)
        if not s or (s['pending'] == 0 and s['inflight'] == 0):
            break
        if not device:
            mine |= pids('com.apple.WebKit.WebContent') - before
            procs = {str(p): f'webcontent:{p}' for p in mine}
            procs.update({str(p): f'gpu-process?:{p}' for p in pids('com.apple.WebKit.GPU')})
            post(f'/pids?job={job}', procs)
        if s['since_last_result_s'] > STALL_S and time.time() - opened > STALL_S:
            post(f'/event?job={job}', {'event': 'driver-reopen', 'stalled_s': s['since_last_result_s']})
            open_page(job)
            opened = time.time()
    print(f'{job} finished', flush=True)
