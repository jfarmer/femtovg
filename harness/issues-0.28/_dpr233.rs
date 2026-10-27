//! femtovg#233: UI text at a fractional device pixel ratio (1.566667, the reporter's Wayland scale).
//! dpr233.html draws the same lines with Canvas 2D.
//!
//!   _dpr233 <out.ppm> <font dir> [dpr] [mode]
//!
//! mode `dpr` (default): set_size(.., dpr) and fill_text in logical units.
//! mode `slint`: what Slint 1.18's FemtoVG renderer does - set_size(.., ceil(dpr)), physical coordinates and
//! font sizes, glyphs placed by the caller through fill_glyph_run.
#![cfg(feature = "wgpu")]
#![allow(non_snake_case)]

use femtovg::{renderer::WGPURenderer, Canvas, Color, FontId, Paint, PositionedGlyph};

const LW: f32 = 320.0;
const LH: f32 = 150.0;
const LINES: [(f32, &str); 5] = [
    (12.0, "Keyboard backlight brightness"),
    (13.0, "Keyboard  Battery  Display"),
    (14.0, "Keyboard settings and shortcuts"),
    (16.0, "Keyboard layout: English (US)"),
    (20.0, "Keyboard Brightness 75%"),
];

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (out, fonts) = (&args[1], &args[2]);
    let dpr: f32 = args.get(3).map(|s| s.parse().unwrap()).unwrap_or(1.566667);
    let (W, H) = ((LW * dpr).ceil() as u32, (LH * dpr).ceil() as u32);

    let instance = wgpu::Instance::default();
    let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions::default())).unwrap();
    let (device, queue) = pollster::block_on(adapter.request_device(&wgpu::DeviceDescriptor::default())).unwrap();
    let renderer = WGPURenderer::new(device.clone(), queue.clone());
    let mut canvas = Canvas::new(renderer).unwrap();
    let slint = args.get(4).is_some_and(|m| m == "slint");
    // An optional fifth argument overrides the ratio passed to set_size in `dpr` mode, to compare rasterizing at
    // the ratio with rasterizing at 1:1 (the drawn size is the same: femtovg draws in device pixels either way).
    let raster: f32 = args.get(5).map(|s| s.parse().unwrap()).unwrap_or(dpr);
    canvas.set_size(W, H, if slint { dpr.ceil() } else { raster });
    let roboto = canvas.add_font(format!("{fonts}/RobotoFlex-VariableFont.ttf")).unwrap();

    canvas.clear_rect(0, 0, W, H, Color::rgb(250, 250, 250));
    let mut y = 6.0;
    for (size, text) in LINES {
        y += size * 1.35;
        let paint = Paint::color(Color::rgb(30, 30, 30)).with_font(&[roboto]);
        if slint {
            let paint = paint.with_font_size(size * dpr);
            glyph_run(&mut canvas, roboto, 8.0 * dpr, (y * dpr).round(), text, &paint);
        } else {
            canvas.fill_text(8.0, y, text, &paint.with_font_size(size)).unwrap();
        }
    }

    let target = device.create_texture(&wgpu::TextureDescriptor {
        label: None,
        size: wgpu::Extent3d { width: W, height: H, depth_or_array_layers: 1 },
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8Unorm,
        usage: wgpu::TextureUsages::RENDER_ATTACHMENT | wgpu::TextureUsages::COPY_SRC,
        view_formats: &[],
    });
    queue.submit(canvas.flush_to_output(&target));

    let padded = (W * 4).div_ceil(wgpu::COPY_BYTES_PER_ROW_ALIGNMENT) * wgpu::COPY_BYTES_PER_ROW_ALIGNMENT;
    let readback = device.create_buffer(&wgpu::BufferDescriptor {
        label: None,
        size: (padded * H) as u64,
        usage: wgpu::BufferUsages::COPY_DST | wgpu::BufferUsages::MAP_READ,
        mapped_at_creation: false,
    });
    let mut encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: None });
    encoder.copy_texture_to_buffer(
        wgpu::TexelCopyTextureInfo {
            texture: &target,
            mip_level: 0,
            origin: wgpu::Origin3d::ZERO,
            aspect: wgpu::TextureAspect::All,
        },
        wgpu::TexelCopyBufferInfo {
            buffer: &readback,
            layout: wgpu::TexelCopyBufferLayout {
                offset: 0,
                bytes_per_row: Some(padded),
                rows_per_image: Some(H),
            },
        },
        wgpu::Extent3d { width: W, height: H, depth_or_array_layers: 1 },
    );
    queue.submit(Some(encoder.finish()));
    let slice = readback.slice(..);
    slice.map_async(wgpu::MapMode::Read, |_| {});
    device.poll(wgpu::PollType::wait_indefinitely()).unwrap();
    let mapped = slice.get_mapped_range().unwrap();
    let mut ppm = format!("P6\n{W} {H}\n255\n").into_bytes();
    for row in 0..H as usize {
        for px in 0..W as usize {
            let i = row * padded as usize + px * 4;
            ppm.extend_from_slice(&mapped[i..i + 3]);
        }
    }
    std::fs::write(out, ppm).unwrap();
}


/// Shapes `text` with femtovg and draws the glyphs with fill_glyph_run at (x, y).
fn glyph_run(canvas: &mut Canvas<WGPURenderer>, font: FontId, x: f32, y: f32, text: &str, paint: &Paint) {
    let metrics = canvas.measure_text(x, y, text, paint).unwrap();
    let glyphs = metrics.glyphs.iter().map(|g| PositionedGlyph {
        x: g.x,
        y: g.y,
        glyph_id: g.glyph_id,
    });
    canvas.fill_glyph_run(font, &[], glyphs, paint).unwrap();
}
