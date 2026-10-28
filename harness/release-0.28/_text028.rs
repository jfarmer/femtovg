//! 0.28 release-notes text scene: right-aligned RTL text at a translated
//! anchor (so every glyph sits at x < 0) with a fading gradient and a glow
//! shadow. The Arabic lines go through fill_glyph_run, as text shaped by
//! parley or cosmic-text does. text028.html draws the same scene with
//! Canvas 2D.
//!
//!   _text028 <out.ppm> <font dir>
#![cfg(feature = "wgpu")]

use femtovg::{renderer::WGPURenderer, Align, Canvas, Color, FontId, Paint, Path, PositionedGlyph};

const W: u32 = 600;
const H: u32 = 400;
const ANCHOR_X: f32 = 560.0;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (out, fonts) = (&args[1], &args[2]);

    let instance = wgpu::Instance::default();
    let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions::default())).unwrap();
    let (device, queue) = pollster::block_on(adapter.request_device(&wgpu::DeviceDescriptor::default())).unwrap();
    let renderer = WGPURenderer::new(device.clone(), queue.clone());
    let mut canvas = Canvas::new(renderer).unwrap();
    canvas.set_size(W, H, 1.0);
    let amiri = canvas.add_font(format!("{fonts}/amiri-regular.ttf")).unwrap();
    let roboto = canvas.add_font(format!("{fonts}/RobotoFlex-VariableFont.ttf")).unwrap();

    canvas.clear_rect(0, 0, W, H, Color::rgb(20, 24, 43));

    // Headline: 128 px, so drawn as outlines; one gradient across the line,
    // fading out toward its end, and a glow cast from what is drawn.
    canvas.save();
    canvas.translate(ANCHOR_X, 150.0);
    canvas.set_shadow_color(Color::rgbaf(0.25, 0.6, 1.0, 0.9));
    canvas.set_shadow_blur(20.0);
    canvas.set_shadow_offset(8.0, 10.0);
    let headline = Paint::linear_gradient_stops(
        -440.0,
        0.0,
        0.0,
        0.0,
        [
            (0.0, Color::rgbaf(1.0, 0.35, 0.55, 0.1)),
            (0.5, Color::rgbaf(1.0, 0.65, 0.25, 0.7)),
            (1.0, Color::rgbaf(1.0, 0.9, 0.5, 1.0)),
        ],
    )
    .with_font(&[amiri])
    .with_font_size(112.0)
    .with_text_align(Align::Right);
    glyph_run(&mut canvas, amiri, "مرحبا بالعالم", &headline);

    // Body text from the glyph atlas, also right-aligned at the anchor,
    // under the same glow.
    canvas.translate(0.0, 90.0);
    let body = Paint::color(Color::rgb(235, 238, 250))
        .with_font(&[amiri])
        .with_font_size(40.0)
        .with_text_align(Align::Right);
    glyph_run(&mut canvas, amiri, "النص من اليمين إلى اليسار", &body);
    canvas.set_shadow_color(Color::rgbaf(0.0, 0.0, 0.0, 0.0));
    canvas.set_shadow_blur(0.0);
    canvas.set_shadow_offset(0.0, 0.0);
    canvas.translate(0.0, 80.0);
    let ruler = Paint::color(Color::rgb(160, 170, 200))
        .with_font(&[roboto])
        .with_font_size(22.0)
        .with_text_align(Align::Right);
    let _ = canvas.fill_text(0.0, 0.0, &"l".repeat(78), &ruler);
    canvas.restore();

    // A thin rule at the anchor.
    let mut rule = Path::new();
    rule.rect(ANCHOR_X + 14.0, 40.0, 2.0, 320.0);
    canvas.fill_path(&rule, &Paint::color(Color::rgba(255, 255, 255, 60)));

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

/// Shapes `text` with femtovg and draws the glyphs with fill_glyph_run.
fn glyph_run(canvas: &mut Canvas<WGPURenderer>, font: FontId, text: &str, paint: &Paint) {
    let metrics = canvas.measure_text(0.0, 0.0, text, paint).unwrap();
    let glyphs = metrics.glyphs.iter().map(|g| PositionedGlyph {
        x: g.x,
        y: g.y,
        glyph_id: g.glyph_id,
    });
    canvas.fill_glyph_run(font, &[], glyphs, paint).unwrap();
}
