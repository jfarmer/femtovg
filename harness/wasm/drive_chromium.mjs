// Runs crosscheck jobs in Chromium through Playwright: one browser per job, the page at SERVER/?job=NAME, the
// browser's processes (GPU process, renderer, browser) posted to the server for sampling, and a watchdog that
// reloads a page that crashed or stopped returning frames.
//
//   PLAYWRIGHT=<playwright package dir> CHROMIUM=<executable> node drive_chromium.mjs SERVER JOB [JOB...]
//   (HEADLESS=1 for the new headless mode; the default is a window, which WebGPU gets the real GPU in.)
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT);
const [server, ...jobs] = process.argv.slice(2);
const STALL_S = Number(process.env.STALL_S || 150);

async function status(job) {
  const all = await (await fetch(`${server}/status`)).json();
  return all.find(j => j.name === job);
}

function processesOf(rootPid) {
  // Every descendant of the browser, with its --type.
  const out = execFileSync('ps', ['-axo', 'pid=,ppid=,command=']).toString().trim().split('\n');
  const rows = out.map(l => { const m = l.trim().match(/^(\d+)\s+(\d+)\s+(.*)$/); return m && { pid: +m[1], ppid: +m[2], cmd: m[3] }; }).filter(Boolean);
  const keep = new Map([[rootPid, 'browser']]);
  let grew = true;
  while (grew) {
    grew = false;
    for (const r of rows) {
      if (!keep.has(r.pid) && keep.has(r.ppid)) {
        const t = (r.cmd.match(/--type=([a-z-]+)/) || [])[1] || 'other';
        const sub = (r.cmd.match(/--utility-sub-type=([\w.]+)/) || [])[1];
        keep.set(r.pid, sub ? `${t}:${sub.split('.').pop()}` : t);
        grew = true;
      }
    }
  }
  return keep;
}

for (const job of jobs) {
  const userDir = fs.mkdtempSync(`${process.env.TMPDIR || '/tmp'}/xcheck-chromium-`);
  const ctx = await chromium.launchPersistentContext(userDir, {
    executablePath: process.env.CHROMIUM,
    headless: !!process.env.HEADLESS,
    viewport: { width: 480, height: 160 },
    args: [
      '--enable-unsafe-webgpu',
      '--js-flags=--expose-gc',
      '--disable-background-timer-throttling',
      '--disable-renderer-backgrounding',
      '--disable-backgrounding-occluded-windows',
      '--no-first-run',
      '--no-default-browser-check',
    ],
  });
  const consoleLog = fs.createWriteStream(`${process.env.RUN_DIR}/${job}/console.log`, { flags: 'a' });
  let crashed = false;
  let page;
  // A crashed page cannot be reloaded: the next one is a new page in the same browser.
  const openPage = async () => {
    page = await ctx.newPage();
    page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') consoleLog.write(`${Date.now()} ${m.type()} ${m.text()}\n`); });
    page.on('crash', () => { crashed = true; consoleLog.write(`${Date.now()} PAGE CRASH\n`); });
    await page.goto(`${server}/?job=${encodeURIComponent(job)}`);
  };
  for (const p of ctx.pages()) await p.close().catch(() => {});
  await openPage();
  // The browser process: the one started with this job's own profile directory.
  const browserPid = (() => {
    const out = execFileSync('ps', ['-axo', 'pid=,command=']).toString().split('\n');
    const row = out.find(l => l.includes(`--user-data-dir=${userDir}`) && !l.includes('--type='));
    return row ? Number(row.trim().split(/\s+/)[0]) : null;
  })();
  consoleLog.write(`${Date.now()} browser pid ${browserPid}\n`);
  const postPids = async () => {
    if (!browserPid) return;
    const procs = Object.fromEntries([...processesOf(browserPid)].map(([pid, role]) => [pid, `${role}:${pid}`]));
    await fetch(`${server}/pids?job=${encodeURIComponent(job)}`, { method: 'POST', body: JSON.stringify(procs) });
  };
  await postPids();
  // Chromium's renderer keeps the body of every POST the page makes (the frames' pixels, about 8 MB at 1080p) out of
  // the garbage collector's reach: a page that has posted RECYCLE frames is replaced by a new one, in a new renderer.
  const RECYCLE = Number(process.env.RECYCLE || 600);
  let doneAtOpen = (await status(job))?.tasks - (await status(job))?.pending;
  for (;;) {
    await new Promise(r => setTimeout(r, 5000));
    const s = await status(job);
    if (!s) break;
    if (s.pending === 0 && s.inflight === 0) break;
    if (s.tasks - s.pending - doneAtOpen >= RECYCLE) {
      await fetch(`${server}/event?job=${encodeURIComponent(job)}`, { method: 'POST', body: JSON.stringify({ event: 'recycle-page' }) });
      await page.close().catch(() => {});
      await openPage();
      doneAtOpen = s.tasks - s.pending;
    }
    await postPids();
    if (crashed || ((s.inflight > 0 || s.pending > 0) && s.since_last_result_s > STALL_S)) {
      consoleLog.write(`${Date.now()} RELOAD (crashed=${crashed}, stalled ${s.since_last_result_s}s)\n`);
      await fetch(`${server}/event?job=${encodeURIComponent(job)}`, { method: 'POST', body: JSON.stringify({ event: crashed ? 'renderer-crash' : 'driver-reload', stalled_s: s.since_last_result_s }) });
      const wasCrash = crashed;
      crashed = false;
      try {
        if (wasCrash) { await page.close().catch(() => {}); await openPage(); }
        else await page.reload({ timeout: 30000 });
      } catch (e) {
        consoleLog.write(`${Date.now()} reload failed: ${e}\n`);
        try { await page.close().catch(() => {}); await openPage(); } catch (_) {}
      }
    }
  }
  await ctx.close();
  fs.rmSync(userDir, { recursive: true, force: true });
  console.log(`${job} finished`);
}
