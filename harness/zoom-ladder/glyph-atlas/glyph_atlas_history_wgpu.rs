//! Investigation: a glyph drawn at one transform must not depend on what the
//! canvas drew before. Two frames on one canvas (transform A, then B) against a
//! fresh canvas drawing only B.
#![cfg(all(feature = "wgpu", feature = "textlayout"))]

use femtovg::{renderer::WGPURenderer, Canvas, Color, Paint, PositionedGlyph};

mod common;
use common::headless_device;

const W: u32 = 460;
const H: u32 = 260;
const FONT: &[u8] = include_bytes!("../examples/assets/RobotoFlex-VariableFont.ttf");

const LINES: [(f32, f32, &str); 3] = [
    (-0.3, 40.0, "Offset -0.3px"),
    (-0.7, 80.0, "Offset -0.7px"),
    (-15.4, 120.0, "Offset -15.4px"),
];

#[derive(Clone, Copy, Debug, PartialEq)]
enum Api {
    GlyphRun,
    FillText,
    /// fill_glyph_run with a one-colour gradient: the outline (path) regime at the exact transform.
    PathRef,
}

fn target(device: &wgpu::Device) -> wgpu::Texture {
    device.create_texture(&wgpu::TextureDescriptor {
        label: None,
        size: wgpu::Extent3d {
            width: W,
            height: H,
            depth_or_array_layers: 1,
        },
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8Unorm,
        usage: wgpu::TextureUsages::RENDER_ATTACHMENT | wgpu::TextureUsages::COPY_SRC,
        view_formats: &[],
    })
}

fn read_back(device: &wgpu::Device, queue: &wgpu::Queue, target: &wgpu::Texture) -> Vec<u8> {
    let unpadded = W * 4;
    let padded = unpadded.div_ceil(wgpu::COPY_BYTES_PER_ROW_ALIGNMENT) * wgpu::COPY_BYTES_PER_ROW_ALIGNMENT;
    let rb = device.create_buffer(&wgpu::BufferDescriptor {
        label: None,
        size: (padded * H) as u64,
        usage: wgpu::BufferUsages::COPY_DST | wgpu::BufferUsages::MAP_READ,
        mapped_at_creation: false,
    });
    let mut enc = device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: None });
    enc.copy_texture_to_buffer(
        wgpu::TexelCopyTextureInfo {
            texture: target,
            mip_level: 0,
            origin: wgpu::Origin3d::ZERO,
            aspect: wgpu::TextureAspect::All,
        },
        wgpu::TexelCopyBufferInfo {
            buffer: &rb,
            layout: wgpu::TexelCopyBufferLayout {
                offset: 0,
                bytes_per_row: Some(padded),
                rows_per_image: Some(H),
            },
        },
        wgpu::Extent3d {
            width: W,
            height: H,
            depth_or_array_layers: 1,
        },
    );
    queue.submit(Some(enc.finish()));
    let sl = rb.slice(..);
    sl.map_async(wgpu::MapMode::Read, |_| {});
    device.poll(wgpu::PollType::wait_indefinitely()).unwrap();
    let m = sl.get_mapped_range().expect("readback");
    let mut px = vec![0u8; (unpadded * H) as usize];
    for row in 0..H as usize {
        let s = row * padded as usize;
        let d = row * unpadded as usize;
        px[d..d + unpadded as usize].copy_from_slice(&m[s..s + unpadded as usize]);
    }
    drop(m);
    rb.unmap();
    px
}

/// One frame per (scale, tx, ty) on one canvas; returns the last frame's pixels.
fn frames(device: &wgpu::Device, queue: &wgpu::Queue, api: Api, steps: &[(f32, f32, f32)]) -> Vec<u8> {
    let target = target(device);
    let renderer = WGPURenderer::new(device.clone(), queue.clone());
    let mut canvas = Canvas::new(renderer).expect("canvas");
    canvas.set_size(W, H, 1.0);
    let font = canvas.add_font_mem(FONT).unwrap();
    let paint = Paint::color(Color::rgb(0x22, 0x22, 0x22))
        .with_font(&[font])
        .with_font_size(20.0);
    let c = Color::rgb(0x22, 0x22, 0x22);
    let path_paint = Paint::linear_gradient(0.0, 0.0, 1.0, 0.0, c, c)
        .with_font(&[font])
        .with_font_size(20.0);
    // Glyph positions in user space, shaped once at identity.
    let runs: Vec<Vec<PositionedGlyph>> = LINES
        .iter()
        .map(|&(x, y, text)| {
            canvas
                .measure_text(x, y, text, &paint)
                .unwrap()
                .glyphs
                .iter()
                .map(|g| PositionedGlyph {
                    x: g.x,
                    y: g.y,
                    glyph_id: g.glyph_id,
                })
                .enumerate()
                .filter(|(i, _)| {
                    std::env::var("GLYPH_ONLY")
                        .ok()
                        .map_or(true, |n| n.split(',').any(|n| n.parse::<usize>().unwrap() == *i))
                })
                .map(|(_, g)| g)
                .collect()
        })
        .collect();
    let mut last = Vec::new();
    for &(s, tx, ty) in steps {
        canvas.clear_rect(0, 0, W, H, Color::white());
        canvas.save();
        canvas.translate(tx, ty);
        canvas.scale(s, s);
        for (i, &(x, y, text)) in LINES.iter().enumerate() {
            match api {
                Api::FillText => {
                    canvas.fill_text(x, y, text, &paint).unwrap();
                }
                Api::GlyphRun => canvas.fill_glyph_run(font, &[], runs[i].iter().cloned(), &paint).unwrap(),
                Api::PathRef => canvas
                    .fill_glyph_run(font, &[], runs[i].iter().cloned(), &path_paint)
                    .unwrap(),
            }
        }
        canvas.restore();
        let commands = canvas.flush_to_output(&target);
        queue.submit(commands);
        last = read_back(device, queue, &target);
    }
    last
}

fn diff(a: &[u8], b: &[u8]) -> (usize, u8) {
    let mut n = 0;
    let mut m = 0;
    for (p, q) in a.chunks_exact(4).zip(b.chunks_exact(4)) {
        let d = (0..3).map(|i| p[i].abs_diff(q[i])).max().unwrap();
        if d > 0 {
            n += 1;
            m = m.max(d);
        }
    }
    (n, m)
}

fn write_ppm(path: &str, px: &[u8]) {
    let mut out = format!("P6\n{W} {H}\n255\n").into_bytes();
    for p in px.chunks_exact(4) {
        out.extend_from_slice(&p[..3]);
    }
    std::fs::write(path, out).unwrap();
}

/// The harness's frame for an SVG of width 400 fit into a 200 px box at
/// (130, 30), zoomed by `zoom` about (230, 130), with the SVG's own
/// translate(100, 0): device scale 0.5 * zoom.
fn harness(zoom: f32) -> (f32, f32, f32) {
    let s = 0.5 * zoom;
    (s, 230.0 + zoom * (130.0 - 230.0) + 100.0 * s, 130.0 + zoom * (30.0 - 130.0))
}

#[test]
fn glyph_atlas_history() {
    let Some((device, queue)) = headless_device() else {
        return;
    };
    let out = std::env::var("GLYPH_HISTORY_OUT").ok();
    let mut cases: Vec<(String, Vec<(f32, f32, f32)>)> = vec![
        ("harness z1 -> z1.25".into(), vec![harness(1.0), harness(1.25)]),
        ("harness z1.2 -> z1.25".into(), vec![harness(1.2), harness(1.25)]),
        // Pure scale-then-translation: second frame at scale 0.625 with tx = 167.5.
        ("s0.5 tx180 -> s0.625 tx167.5".into(), vec![(0.5, 180.0, 30.0), (0.625, 167.5, 5.0)]),
        // Same, but the second frame's translation integral or a quarter.
        ("s0.5 -> s0.625 tx167".into(), vec![(0.5, 180.0, 30.0), (0.625, 167.0, 5.0)]),
        ("s0.5 -> s0.625 tx167.25".into(), vec![(0.5, 180.0, 30.0), (0.625, 167.25, 5.0)]),
        ("s0.5 -> s0.625 tx167.75".into(), vec![(0.5, 180.0, 30.0), (0.625, 167.75, 5.0)]),
        // Atlas regime (scale 1) with a half-pixel translation.
        ("s0.5 -> s1 tx100.5".into(), vec![(0.5, 180.0, 30.0), (1.0, 100.5, 5.0)]),
        // Atlas regime: a different glyph set first at scale 1, then the same.
        ("s1 tx100 -> s1 tx100.5".into(), vec![(1.0, 100.0, 5.0), (1.0, 100.5, 5.0)]),
    ];
    if let Ok(extra) = std::env::var("GLYPH_HISTORY_CASE") {
        // "s,tx,ty;s,tx,ty;..."
        let steps = extra
            .split(';')
            .map(|t| {
                let v: Vec<f32> = t.split(',').map(|x| x.trim().parse().unwrap()).collect();
                (v[0], v[1], v[2])
            })
            .collect();
        cases = vec![(format!("custom {extra}"), steps)];
    }
    for api in [Api::GlyphRun, Api::FillText, Api::PathRef] {
        for (name, steps) in &cases {
            let ladder = frames(&device, &queue, api, steps);
            let fresh = frames(&device, &queue, api, &steps[steps.len() - 1..]);
            let (n, m) = diff(&ladder, &fresh);
            eprintln!("{api:?} {name}: ladder vs fresh {n} px, max {m}");
            if let Some(dir) = &out {
                let tag = format!("{api:?}_{}", name.replace([' ', '>', '.'], "_"));
                write_ppm(&format!("{dir}/{tag}_ladder.ppm"), &ladder);
                write_ppm(&format!("{dir}/{tag}_fresh.ppm"), &fresh);
            }
        }
    }
}
