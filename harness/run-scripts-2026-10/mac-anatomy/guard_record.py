#!/usr/bin/env python3
"""Run `xcrun xctrace record` under a disk guard.

usage: guard_record.py TEMPLATE OUT.trace [--limit-mb N] [--env K=V ...] -- CMD...

Waits for >= 2500 MB free before starting. While recording, polls free space and
the size of xctrace's scratch (…/C/com.apple.dt.InstrumentsCLI/path_manager):
below 1200 MB free, or scratch above --limit-mb (default 1500), it sends SIGINT,
then SIGKILL after 15 s, and deletes the scratch directories of that xctrace pid.
Prints the peak scratch size, the trace size and the wall time.
"""
import glob, os, shutil, signal, subprocess, sys, time

PM = '/private/var/folders/_c/krb2zmbx2ss6b1xhpydpxcr80000gn/C/com.apple.dt.InstrumentsCLI/path_manager'


def free_mb():
    st = os.statvfs('/')
    return st.f_bavail * st.f_frsize // (1 << 20)


def du_mb(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.lstat(os.path.join(root, f)).st_blocks * 512
            except OSError:
                pass
    return total // (1 << 20)


def main():
    args = sys.argv[1:]
    tpl, out = args.pop(0), args.pop(0)
    limit = 1500
    envs = []
    while args and args[0] != '--':
        a = args.pop(0)
        if a == '--limit-mb':
            limit = int(args.pop(0))
        elif a == '--env':
            envs += ['--env', args.pop(0)]
    args.pop(0)
    waited = 0
    while free_mb() < 2500:
        if waited > 900:
            sys.exit(f'gave up: {free_mb()} MB free')
        time.sleep(15)
        waited += 15
    for attempt in range(40):
        others = subprocess.run(['pgrep', '-f', 'xctrace record'], capture_output=True, text=True).stdout.split()
        if not others:
            break
        time.sleep(10)
    for attempt in range(20):
        rc, log = record(tpl, out, envs, args, limit)
        if 'could not lock kperf' not in log:
            break
        print('guard: kperf busy, retrying', flush=True)
        time.sleep(20)
        while subprocess.run(['pgrep', '-f', 'xctrace record'], capture_output=True, text=True).stdout.split():
            time.sleep(10)


def record(tpl, out, envs, args, limit):
    shutil.rmtree(out, ignore_errors=True)
    cmd = ['/Applications/Xcode.app/Contents/Developer/usr/bin/xctrace', 'record', '--template', tpl, '--output', out, '--no-prompt', *envs, '--launch', '--', *args]
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    peak = 0
    killed = None
    while p.poll() is None:
        time.sleep(0.5)
        scratch = sum(du_mb(d) for d in glob.glob(f'{PM}/xrtmp__{p.pid}.*'))
        peak = max(peak, scratch)
        f = free_mb()
        if killed is None and (f < 1200 or scratch > limit):
            killed = time.time()
            print(f'guard: free {f} MB, scratch {scratch} MB: SIGINT', flush=True)
            # xcrun execs xctrace; signal the whole child.
            p.send_signal(signal.SIGINT)
        elif killed and time.time() - killed > 15:
            print('guard: SIGKILL', flush=True)
            p.kill()
            break
    p.wait()
    log = p.stdout.read()
    if killed:
        for d in glob.glob(f'{PM}/xrtmp__{p.pid}.*'):
            shutil.rmtree(d, ignore_errors=True)
    size = du_mb(out) if os.path.exists(out) else 0
    print(log.strip().splitlines()[-3:] if log.strip() else '')
    print(f'guard: wall {time.time() - t0:.1f} s, peak scratch {peak} MB, trace {size} MB, free {free_mb()} MB, '
          f'{"KILLED" if killed else "ok"}', flush=True)
    return p.returncode, log


main()
