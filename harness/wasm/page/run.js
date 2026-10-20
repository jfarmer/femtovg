// The crosscheck page: ?job=NAME. Loads the job's build, makes one device and canvas, then asks the server for one
// frame at a time and posts back its pixels, timings, counters, wasm heap and device errors. A frame that throws is
// reported and the page reloads itself (a panicked wasm instance is not reused); the server hands the frame out
// once more and writes it as failed after a second death.
const params = new URLSearchParams(location.search);
const jobName = params.get('job');
const log = (...a) => { document.getElementById('log').textContent = a.join(' '); };

const channel = new MessageChannel();
const waiters = [];
channel.port1.onmessage = () => waiters.shift()?.();
// One turn of the event loop, without setTimeout's 4 ms clamp: map and work-done callbacks resolve in between.
const tick = () => new Promise(r => { waiters.push(r); channel.port2.postMessage(0); });

async function post(path, body) {
  const r = await fetch(`${path}?job=${encodeURIComponent(jobName)}`, { method: 'POST', body: JSON.stringify(body) });
  return r.json();
}

async function postResult(header, rgba) {
  // One byte array, not a Blob: Chromium keeps every Blob in its browser process until it is collected, and a run of
  // 1080p frames fills the blob quota (ERR_BLOB_OUT_OF_MEMORY).
  const h = new TextEncoder().encode(JSON.stringify(header));
  const body = new Uint8Array(4 + h.length + (rgba ? rgba.length : 0));
  new DataView(body.buffer).setUint32(0, h.length, true);
  body.set(h, 4);
  if (rgba) body.set(rgba, 4 + h.length);
  await fetch(`/result?job=${encodeURIComponent(jobName)}`, { method: 'POST', body });
}

async function waitFor(pred, what, limitMs) {
  const t0 = performance.now();
  while (!pred()) {
    await tick();
    if (performance.now() - t0 > limitMs) throw new Error(`timed out waiting for ${what} after ${limitMs} ms`);
  }
  return performance.now() - t0;
}

async function main() {
  const job = await (await fetch(`/job?job=${encodeURIComponent(jobName)}`)).json();
  const mod = await import(`/pkg/${job.build}/logos_wasm.js`);
  const wasm = await mod.default();
  const memory = () => wasm.memory.buffer.byteLength;
  let h;
  try {
    h = await mod.create_harness(job.backend);
  } catch (e) {
    await post('/hello', { ua: navigator.userAgent, gpu: !!navigator.gpu, error: String(e) });
    log('no harness:', String(e));
    return;
  }
  for (const url of await (await fetch('/fonts.json')).json()) {
    h.add_font(new Uint8Array(await (await fetch(url)).arrayBuffer()));
  }
  let adapter = null;
  try {
    const a = navigator.gpu && await navigator.gpu.requestAdapter({ powerPreference: 'high-performance' });
    if (a) adapter = { vendor: a.info.vendor, architecture: a.info.architecture, device: a.info.device,
                       description: a.info.description, features: [...a.features].sort() };
  } catch (e) { adapter = { error: String(e) }; }
  await post('/hello', { ua: navigator.userAgent, gpu: !!navigator.gpu, info: h.info(), adapter, faces: h.font_faces(),
                         wasm_bytes: memory(), isolated: self.crossOriginIsolated });
  let n = 0;
  for (;;) {
    const task = await (await fetch(`/next?job=${encodeURIComponent(jobName)}`)).json();
    if (task.done) { log('done', n, 'frames'); await post('/event', { event: 'done', frames: n }); return; }
    if (task.probe === 'element-upload') {
      const header = { key: task.key, framing: task.framing };
      try {
        const el = document.createElement('canvas');
        el.width = 4; el.height = 4;
        const ctx = el.getContext('2d');
        ctx.fillStyle = 'rgb(0, 0, 255)';
        ctx.fillRect(0, 0, 4, 4);
        h.probe_element_upload(el);
        header.probe = {};
        for (const [i, name] of [[0, 'A'], [1, 'B']]) {
          h.select_probe_target(i);
          h.request_pixels();
          let px;
          await waitFor(() => (px = h.pixels()) !== undefined, 'the readback', 30000);
          const o = (8 * 16 + 8) * 4;
          header.probe[name] = [px[o], px[o + 1], px[o + 2], px[o + 3]];
        }
      } catch (e) { header.error = String(e && e.stack ? e.stack : e); }
      header.device_errors = h.take_errors();
      await postResult(header, null);
      n++;
      continue;
    }
    const header = { key: task.key, framing: task.framing, wasm_before: memory() };
    const t0 = performance.now();
    let rgba = null;
    try {
      h.clear_env();
      for (const [k, v] of Object.entries(task.env)) h.set_env(k, v);
      h.reset_counters();
      const svg = await (await fetch(task.svg)).text();
      header.parse_ms = h.load(svg);
      header.encode_ms = [];
      header.gpu_wait_ms = [];
      for (let i = 0; i < task.frames; i++) {
        header.encode_ms.push(h.render(task.scale, task.dark));
        header.gpu_wait_ms.push(await waitFor(() => h.frame_done(), 'the queue', 120000));
      }
      const [w, hh] = [Number(task.env.FRAME_W), Number(task.env.FRAME_H)];
      header.w = w; header.h = hh;
      // NO_READBACK: measure the frames alone, without the readback buffer each one otherwise costs.
      if (!task.env.NO_READBACK) {
        const tr = performance.now();
        h.request_pixels();
        let px;
        await waitFor(() => (px = h.pixels()) !== undefined, 'the readback', 120000);
        header.readback_ms = performance.now() - tr;
        rgba = px;
        if (rgba.length !== w * hh * 4) throw new Error(`readback ${rgba.length} bytes for ${w}x${hh}`);
      }
      header.stats = JSON.parse(h.stats());
    } catch (e) {
      header.error = String(e && e.stack ? e.stack : e);
      rgba = null;
    }
    header.total_ms = performance.now() - t0;
    header.wasm_after = memory();
    if (performance.memory) header.js_heap = performance.memory.usedJSHeapSize;
    try { header.device_errors = h.take_errors(); header.lost = h.lost() ?? null; } catch (e) { header.device_errors = [String(e)]; }
    // NO_POST_PIXELS: read back but send only the header (isolates the upload from the readback in memory probes).
    await postResult(header, task.env.NO_POST_PIXELS ? null : rgba);
    n++;
    // Chromium holds every mapped readback (about twice the frame) until a collection it does not schedule for them:
    // with --js-flags=--expose-gc the page collects every 20 frames (GC_EVERY), so a run of 1080p frames does not
    // take the renderer to an out-of-memory crash. Runs without readback (NO_READBACK) keep the browser's own GC.
    if (self.gc && !task.env.NO_READBACK && n % Number(task.env.GC_EVERY || 20) === 0) self.gc();
    log(n, task.key, task.framing, header.error ? 'ERROR' : '');
    if (header.error || header.lost) {
      // A thrown frame may have left the wasm instance poisoned (a panic), and a lost device stays lost.
      await post('/event', { event: 'reload', key: task.key, framing: task.framing, error: header.error, lost: header.lost });
      location.reload();
      return;
    }
  }
}

main().catch(async e => {
  try { await post('/event', { event: 'fatal', error: String(e && e.stack ? e.stack : e) }); } catch (_) {}
  log('fatal', String(e));
  // Start over: the server hands the frame that was in flight out once more.
  setTimeout(() => location.reload(), 2000);
});
