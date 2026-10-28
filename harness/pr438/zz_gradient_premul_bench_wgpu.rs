//! Cost of #438's premultiplied interpolation for fading two-stop gradients (not part of the PR).
//! GB_MODE = analytic | premul, GB_ANIM = 0|1 (end alpha changes every frame), GB_N gradients, GB_FRAMES.
//! Prints per-frame render-thread instructions/cycles (thread_selfcounts), CPU energy, GPU time and footprint.
#![cfg(feature = "wgpu")]

use femtovg::{renderer::WGPURenderer, Canvas, Color, Paint, Path};
use std::ffi::{c_char, c_void, CString};

mod common;
use common::headless_device;

type ThscFn = unsafe extern "C" fn(i32, *mut c_void, usize) -> i32;
unsafe extern "C" {
    fn dlsym(handle: *mut c_void, symbol: *const c_char) -> *mut c_void;
    fn proc_pid_rusage(pid: i32, flavor: i32, buffer: *mut c_void) -> i32;
    fn getpid() -> i32;
    fn mach_task_self() -> u32;
    fn task_info(task: u32, flavor: i32, info: *mut c_void, count: *mut u32) -> i32;
}

fn thread_counts() -> (u64, u64) {
    let c = CString::new("thread_selfcounts").unwrap();
    let p = unsafe { dlsym(-2isize as *mut c_void, c.as_ptr()) };
    if p.is_null() {
        return (0, 0);
    }
    let f: ThscFn = unsafe { std::mem::transmute_copy(&p) };
    let mut buf = [[0u64; 4]; 4];
    unsafe { f(4, buf.as_mut_ptr() as *mut c_void, std::mem::size_of_val(&buf)) };
    (buf[0][0] + buf[1][0], buf[0][1] + buf[1][1])
}

/// (phys_footprint, lifetime max footprint, CPU energy nJ) from rusage_info_v6.
fn rusage() -> (u64, u64, u64) {
    let mut ri = [0u64; 64];
    unsafe { proc_pid_rusage(getpid(), 6, ri.as_mut_ptr() as *mut c_void) };
    (ri[9], ri[30], ri[42])
}

/// GPU time in ns attributed to the task (task_power_info_v2.gpu_energy.task_gpu_utilisation).
fn gpu_ns() -> u64 {
    let mut info = [0u64; 13];
    let mut count = (std::mem::size_of_val(&info) / 4) as u32;
    unsafe { task_info(mach_task_self(), 26, info.as_mut_ptr() as *mut c_void, &mut count) };
    info[6]
}

#[test]
#[ignore]
fn zz_gradient_premul_bench() {
    let Some((device, queue)) = headless_device() else { return };
    let premul = std::env::var("GB_MODE").as_deref() == Ok("premul");
    let anim = std::env::var("GB_ANIM").as_deref() == Ok("1");
    let n: usize = std::env::var("GB_N").ok().and_then(|v| v.parse().ok()).unwrap_or(500);
    let frames: usize = std::env::var("GB_FRAMES").ok().and_then(|v| v.parse().ok()).unwrap_or(200);
    let (w, h) = (1000u32, 1000u32);
    let target = device.create_texture(&wgpu::TextureDescriptor {
        label: None,
        size: wgpu::Extent3d { width: w, height: h, depth_or_array_layers: 1 },
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8Unorm,
        usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
        view_formats: &[],
    });
    let mut canvas = Canvas::new(WGPURenderer::new(device.clone(), queue.clone())).unwrap();
    canvas.set_size(w, h, 1.0);
    let cols = (n as f32).sqrt().ceil() as usize;
    let cell = w as f32 / cols as f32;
    let (mut instr, mut cycles) = (Vec::new(), Vec::new());
    let (mut e0, mut g0, mut f_after_warmup) = (0, 0, 0);
    for frame in 0..frames {
        if frame == 10 {
            e0 = rusage().2;
            g0 = gpu_ns();
            f_after_warmup = rusage().0;
        }
        let (i0, c0) = thread_counts();
        canvas.clear_rect(0, 0, w, h, Color::black());
        for i in 0..n {
            let (x, y) = ((i % cols) as f32 * cell, (i / cols) as f32 * cell);
            let start = Color::hsl(i as f32 / n as f32, 0.8, 0.5);
            let alpha = if anim { ((frame * 7 + i) % 200) as u8 } else { 0 };
            let mut end = start;
            end.set_alpha(alpha);
            let mut path = Path::new();
            path.rect(x, y, cell - 2.0, cell - 2.0);
            let paint = Paint::linear_gradient(x, y, x + cell, y, start, end).with_premultiplied_interpolation(premul);
            canvas.fill_path(&path, &paint);
        }
        let commands = canvas.flush_to_output(&target).unwrap();
        queue.submit([commands]);
        let (i1, c1) = thread_counts();
        let _ = device.poll(wgpu::PollType::wait_indefinitely());
        if frame >= 10 {
            instr.push(i1 - i0);
            cycles.push(c1 - c0);
        }
    }
    let (fp, fp_max, e1) = rusage();
    let g1 = gpu_ns();
    instr.sort_unstable();
    cycles.sort_unstable();
    let med = |v: &Vec<u64>| v[v.len() / 2];
    let measured = (frames - 10) as f64;
    println!(
        "GB mode={} anim={} n={n}: per frame instr {:.2} M cycles {:.2} M | CPU energy {:.3} mJ/frame | GPU {:.1} us/frame | footprint {:.1} MB (after warmup {:.1}, peak {:.1})",
        if premul { "premul" } else { "analytic" },
        anim as u8,
        med(&instr) as f64 / 1e6,
        med(&cycles) as f64 / 1e6,
        (e1 - e0) as f64 / 1e6 / measured,
        (g1 - g0) as f64 / 1e3 / measured,
        fp as f64 / 1048576.0,
        f_after_warmup as f64 / 1048576.0,
        fp_max as f64 / 1048576.0
    );
}

/// The PR's LUT path against the exact premultiplied ramp: white -> transparent over black, 1024 px.
#[test]
#[ignore]
fn zz_gradient_premul_accuracy() {
    let Some((device, queue)) = headless_device() else { return };
    let w = 1024u32;
    for premul in [false, true] {
        let out = common::render_rgba(&device, &queue, w, 1, Color::black(), |c| {
            let mut p = Path::new();
            p.rect(0.0, 0.0, w as f32, 1.0);
            let paint = Paint::linear_gradient(0.0, 0.0, w as f32, 0.0, Color::white(), Color::rgba(255, 255, 255, 0))
                .with_premultiplied_interpolation(premul);
            c.fill_path(&p, &paint);
        });
        // Exact: straight mixes white and transparent white (still white), alpha 1 - t either way, so over black
        // both interpolations give (1 - t) * 255 for a white-to-transparent-white fade.
        let (mut worst, mut at, mut sum) = (0i32, 0u32, 0i64);
        for x in 0..w {
            let t = (x as f64 + 0.5) / w as f64;
            let want = ((1.0 - t) * 255.0).round() as i32;
            let got = out[(x * 4) as usize] as i32;
            let d = (got - want).abs();
            sum += d as i64;
            if d > worst {
                worst = d;
                at = x;
            }
        }
        println!("ACC premul={premul}: max |err| {worst}/255 at x={at}, mean {:.2}/255", sum as f64 / w as f64);
    }
}
