#![cfg(feature = "wgpu")]
// Scratch (not for commit): what a frame of concave fills under a clip mask costs the render thread, for #403.
// HM_BENCH=hard|soft|none: 400 concave fills (L and U shapes) at 1920x1080 under a star clip (a coverage mask)
// with source-in (a hard mask), source-over (a soft mask), or no clip. Frames 0..WARM are not counted; the next
// FRAMES are, each flushed, submitted and waited for. Prints the thread's exact instructions and cycles a frame per
// CPU kind (thread_selfcounts) and the wall time a frame.

use femtovg::{renderer::WGPURenderer, Canvas, Color, CompositeOperation, FillRule, Paint, Path};

mod common;
use common::headless_device;

fn star(cx: f32, cy: f32, r0: f32, r1: f32, points: usize) -> Path {
    let mut path = Path::new();
    for i in 0..points * 2 {
        let a = i as f32 * std::f32::consts::PI / points as f32;
        let r = if i % 2 == 0 { r1 } else { r0 };
        let (x, y) = (cx + r * a.sin(), cy - r * a.cos());
        if i == 0 {
            path.move_to(x, y);
        } else {
            path.line_to(x, y);
        }
    }
    path.close();
    path
}

fn shape(x: f32, y: f32, s: f32, u: bool) -> Path {
    let mut path = Path::new();
    let pts: &[(f32, f32)] = if u {
        &[(0.0, 0.0), (0.3, 0.0), (0.3, 0.7), (0.7, 0.7), (0.7, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    } else {
        &[(0.0, 0.0), (0.3, 0.0), (0.3, 0.7), (1.0, 0.7), (1.0, 1.0), (0.0, 1.0)]
    };
    for (i, (px, py)) in pts.iter().enumerate() {
        let (px, py) = (x + px * s, y + py * s);
        if i == 0 {
            path.move_to(px, py);
        } else {
            path.line_to(px, py);
        }
    }
    path.close();
    path
}

fn draw(canvas: &mut Canvas<WGPURenderer>, mode: &str, clip: &Path, shapes: &[(Path, Paint)]) {
    canvas.save();
    match mode {
        "hard" => {
            canvas.clip_path(clip, FillRule::NonZero);
            canvas.global_composite_operation(CompositeOperation::SourceIn);
        }
        "soft" => canvas.clip_path(clip, FillRule::NonZero),
        _ => {}
    }
    for (path, paint) in shapes {
        canvas.fill_path(path, paint);
    }
    canvas.restore();
}

#[test]
fn zz_hm_bench() {
    let Ok(mode) = std::env::var("HM_BENCH") else {
        return;
    };
    let Some((device, queue)) = headless_device() else {
        return;
    };
    let warm: usize = std::env::var("WARM").ok().and_then(|v| v.parse().ok()).unwrap_or(50);
    let frames: usize = std::env::var("FRAMES").ok().and_then(|v| v.parse().ok()).unwrap_or(200);
    let (w, h) = (1920u32, 1080u32);
    let target = device.create_texture(&wgpu::TextureDescriptor {
        label: None,
        size: wgpu::Extent3d { width: w, height: h, depth_or_array_layers: 1 },
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8Unorm,
        usage: wgpu::TextureUsages::RENDER_ATTACHMENT | wgpu::TextureUsages::COPY_SRC,
        view_formats: &[],
    });
    let mut canvas = Canvas::new(WGPURenderer::new(device.clone(), queue.clone())).unwrap();
    canvas.set_size(w, h, 1.0);
    let clip = star(960.0, 540.0, 260.0, 600.0, 7);
    let shapes: Vec<(Path, Paint)> = (0..400)
        .map(|i| {
            let (col, row) = (i % 25, i / 25);
            let c = Color::rgb((i * 37 % 256) as u8, (i * 91 % 256) as u8, (i * 53 % 256) as u8);
            (shape(20.0 + col as f32 * 76.0, 20.0 + row as f32 * 66.0, 60.0, i % 2 == 0), Paint::color(c))
        })
        .collect();

    extern "C" {
        fn dlsym(handle: *mut std::ffi::c_void, symbol: *const std::ffi::c_char) -> *mut std::ffi::c_void;
    }
    type Thsc = unsafe extern "C" fn(i32, *mut std::ffi::c_void, usize) -> i32;
    let thsc = unsafe { dlsym(-2isize as *mut _, c"thread_selfcounts".as_ptr()) };
    let counts = || -> [[u64; 4]; 4] {
        let mut buf = [[0u64; 4]; 4];
        if !thsc.is_null() {
            let f: Thsc = unsafe { std::mem::transmute(thsc) };
            unsafe { f(4, buf.as_mut_ptr() as *mut _, std::mem::size_of_val(&buf)) };
        }
        buf
    };
    let mut frame = |canvas: &mut Canvas<WGPURenderer>| {
        canvas.clear_rect(0, 0, w, h, Color::white());
        draw(canvas, &mode, &clip, &shapes);
        let commands = canvas.flush_to_output(&target).unwrap();
        queue.submit([commands]);
        device.poll(wgpu::PollType::wait_indefinitely()).unwrap();
    };
    for _ in 0..warm {
        frame(&mut canvas);
    }
    let c0 = counts();
    let started = std::time::Instant::now();
    for _ in 0..frames {
        frame(&mut canvas);
    }
    let ms = started.elapsed().as_secs_f64() * 1e3 / frames as f64;
    let c1 = counts();
    let per = |kind: usize, i: usize| (c1[kind][i] - c0[kind][i]) as f64 / frames as f64 / 1e6;
    eprintln!(
        "HM_BENCH {mode}: E {:.4} M instr {:.4} M cycles, P {:.4} M instr {:.4} M cycles a frame; {ms:.3} ms a frame",
        per(1, 0),
        per(1, 1),
        per(0, 0),
        per(0, 1)
    );
}
