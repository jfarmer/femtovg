//! What the wgpu backend's pipeline lookup costs a frame that rotates through many pipelines:
//! `pm_rotate PAIRS FILLS FRAMES` draws FILLS antialiased squares a frame at 1080p, the i-th under the
//! (i mod PAIRS)-th pair of blend factors - two pipelines a pair, a triangle list and a strip - and prints the
//! time a frame takes to record and encode.
use femtovg::{renderer::WGPURenderer, BlendFactor, Canvas, Color, Paint, Path};

const FACTORS: [BlendFactor; 6] = [
    BlendFactor::Zero,
    BlendFactor::One,
    BlendFactor::SrcAlpha,
    BlendFactor::OneMinusSrcAlpha,
    BlendFactor::DstAlpha,
    BlendFactor::OneMinusDstAlpha,
];

fn main() {
    let args: Vec<usize> = std::env::args().skip(1).map(|a| a.parse().unwrap()).collect();
    let (pairs, fills, frames) = (args[0], args[1], args[2]);
    assert!(pairs <= 36);
    let instance = wgpu::Instance::default();
    let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions {
        power_preference: wgpu::PowerPreference::default(),
        force_fallback_adapter: false,
        compatible_surface: None,
        ..Default::default()
    }))
    .unwrap();
    let (device, queue) = pollster::block_on(adapter.request_device(&wgpu::DeviceDescriptor {
        label: None,
        required_features: wgpu::Features::empty(),
        required_limits: wgpu::Limits::downlevel_defaults().using_resolution(adapter.limits()),
        experimental_features: wgpu::ExperimentalFeatures::disabled(),
        memory_hints: wgpu::MemoryHints::MemoryUsage,
        trace: wgpu::Trace::default(),
    }))
    .unwrap();
    let target = device.create_texture(&wgpu::TextureDescriptor {
        label: None,
        size: wgpu::Extent3d {
            width: 1920,
            height: 1080,
            depth_or_array_layers: 1,
        },
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8Unorm,
        usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
        view_formats: &[],
    });
    let mut canvas = Canvas::new(WGPURenderer::new(device.clone(), queue.clone())).unwrap();
    canvas.set_size(1920, 1080, 1.0);
    let paint = Paint::color(Color::rgba(220, 120, 30, 160));
    // CONTOURS=n joins n squares into one path, a fill of n contours: one command, a draw a contour for its fringe.
    let contours: usize = std::env::var("CONTOURS").ok().and_then(|v| v.parse().ok()).unwrap_or(1);
    let squares: Vec<Path> = (0..fills / contours)
        .map(|p| {
            let mut path = Path::new();
            for i in p * contours..(p + 1) * contours {
                path.rect(10.0 + (i % 47) as f32 * 40.0, 10.0 + ((i / 47) % 26) as f32 * 40.0, 30.0, 30.0);
            }
            path
        })
        .collect();
    let mut encoding = std::time::Duration::ZERO;
    for _ in 0..frames {
        let started = std::time::Instant::now();
        canvas.clear_rect(0, 0, 1920, 1080, Color::white());
        for (i, square) in squares.iter().enumerate() {
            let pair = i % pairs;
            canvas.global_composite_blend_func(FACTORS[pair / 6], FACTORS[pair % 6]);
            canvas.fill_path(square, &paint);
        }
        let commands = canvas.flush_to_output(&target);
        encoding += started.elapsed();
        queue.submit(commands);
        device.poll(wgpu::PollType::wait_indefinitely()).unwrap();
    }
    println!("pairs={pairs} fills={fills} encode_ms={:.4}", encoding.as_secs_f64() * 1000.0 / frames as f64);
}
