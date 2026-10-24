//! `BlendMode::PlusLighter` on the OpenGL backend, without a visible window: the repository's GPU tests run on
//! wgpu only, so this is the run-time check of the GL blend shader's mode 16 (`ImageFilter::Blend`, SVG `feBlend`)
//! and of a plus-lighter layer, which composites with `CompositeOperation::Lighter`, on an image target and on the
//! screen. Each result is the clamped premultiplied sum. Copy to `examples/gl_plus_lighter_check.rs` of a femtovg
//! checkout with `BlendMode::PlusLighter` and `cargo run --example gl_plus_lighter_check`; prints
//! `GL PLUS-LIGHTER CHECK OK`.
use std::num::NonZeroU32;

use femtovg::{
    renderer::OpenGl, BlendMode, Canvas, Color, ImageFilter, ImageFlags, ImageId, LayerEffects, Paint, Path,
    PixelFormat, RenderTarget,
};
use glutin::{
    config::ConfigTemplateBuilder,
    context::{ContextApi, ContextAttributesBuilder},
    display::GetGlDisplay,
    prelude::*,
    surface::SurfaceAttributesBuilder,
};
use glutin_winit::DisplayBuilder;
use raw_window_handle::HasWindowHandle;
use winit::application::ApplicationHandler;
use winit::event::WindowEvent;
use winit::event_loop::{ActiveEventLoop, EventLoop};
use winit::window::Window;

const W: u32 = 16;
const H: u32 = 16;

struct App {
    done: bool,
}

/// Premultiplied test pixels: the source and backdrop vary across the image, some sums past 255.
fn source_pixel(x: u32, y: u32) -> [u8; 4] {
    let a = (64 + y * 12) as u8;
    let s = |v: u32| (v.min(255) as u8).min(a);
    [s(x * 16), s(y * 8), s(255 - x * 16), a]
}

fn backdrop_pixel(x: u32, y: u32) -> [u8; 4] {
    let a = (255 - x * 8) as u8;
    let s = |v: u32| (v.min(255) as u8).min(a);
    [s(y * 16), s(128), s(x * 4), a]
}

fn upload(canvas: &mut Canvas<OpenGl>, f: impl Fn(u32, u32) -> [u8; 4]) -> ImageId {
    let pixels: Vec<femtovg::rgb::RGBA8> = (0..W * H)
        .map(|i| {
            let [r, g, b, a] = f(i % W, i / W);
            femtovg::rgb::RGBA8::new(r, g, b, a)
        })
        .collect();
    canvas
        .create_image(femtovg::imgref::Img::new(&pixels[..], W as usize, H as usize), ImageFlags::PREMULTIPLIED)
        .unwrap()
}

/// What is drawn by `draw` on an image target cleared to `background` (or on the screen), read back top row first.
fn render(canvas: &mut Canvas<OpenGl>, screen: bool, background: Color, draw: impl FnOnce(&mut Canvas<OpenGl>)) -> Vec<[u8; 4]> {
    let out = canvas
        .create_image_empty(W as usize, H as usize, PixelFormat::Rgba8, ImageFlags::empty())
        .unwrap();
    canvas.set_render_target(if screen { RenderTarget::Screen } else { RenderTarget::Image(out) });
    canvas.clear_rect(0, 0, W, H, background);
    draw(canvas);
    canvas.flush_to_output(());
    let shot = canvas.screenshot().unwrap();
    let pixels = shot.pixels().map(|p| [p.r, p.g, p.b, p.a]).collect();
    canvas.set_render_target(RenderTarget::Screen);
    canvas.flush_to_output(());
    canvas.delete_image(out);
    pixels
}

fn fill(canvas: &mut Canvas<OpenGl>, x: f32, w: f32, color: Color) {
    let mut p = Path::new();
    p.rect(x, 0.0, w, H as f32);
    let mut paint = Paint::color(color);
    paint.set_anti_alias(false);
    canvas.fill_path(&p, &paint);
}

impl ApplicationHandler for App {
    fn resumed(&mut self, event_loop: &ActiveEventLoop) {
        if self.done {
            return;
        }
        self.done = true;
        let window_attrs = Window::default_attributes()
            .with_inner_size(winit::dpi::PhysicalSize::new(W, H))
            .with_visible(false);
        let template = ConfigTemplateBuilder::new().with_alpha_size(8).with_stencil_size(8);
        let (window, gl_config) = DisplayBuilder::new()
            .with_window_attributes(Some(window_attrs))
            .build(event_loop, template, |mut configs| configs.next().unwrap())
            .unwrap();
        let window = window.unwrap();
        let raw = window.window_handle().unwrap().as_raw();
        let gl_display = gl_config.display();
        let attributes = ContextAttributesBuilder::new().build(Some(raw));
        let fallback = ContextAttributesBuilder::new().with_context_api(ContextApi::Gles(None)).build(Some(raw));
        let context = unsafe {
            gl_display
                .create_context(&gl_config, &attributes)
                .unwrap_or_else(|_| gl_display.create_context(&gl_config, &fallback).unwrap())
        };
        let attrs = SurfaceAttributesBuilder::<glutin::surface::WindowSurface>::new().build(
            raw,
            NonZeroU32::new(W).unwrap(),
            NonZeroU32::new(H).unwrap(),
        );
        let surface = unsafe { gl_display.create_window_surface(&gl_config, &attrs).unwrap() };
        let _context = context.make_current(&surface).unwrap();
        let renderer = unsafe { OpenGl::new_from_function_cstr(|s| gl_display.get_proc_address(s).cast()) }.unwrap();
        let mut canvas = Canvas::new(renderer).unwrap();
        canvas.set_size(W, H, 1.0);

        let mut failed = false;
        let mut check = |name: &str, pixels: &[[u8; 4]], want: &dyn Fn(u32, u32) -> [u8; 4]| {
            let wrong: Vec<_> = (0..W * H)
                .filter(|i| {
                    let (got, want) = (pixels[*i as usize], want(i % W, i / W));
                    (0..4).any(|c| got[c].abs_diff(want[c]) > 1)
                })
                .collect();
            println!("{name}: {} pixels wrong", wrong.len());
            if let Some(&i) = wrong.first() {
                println!("  first at ({}, {}): got {:?}, want {:?}", i % W, i / W, pixels[i as usize], want(i % W, i / W));
            }
            failed |= !wrong.is_empty();
        };

        // feBlend: the source plus the backdrop, clamped, drawn 1:1 on transparent.
        let source = upload(&mut canvas, source_pixel);
        let backdrop = upload(&mut canvas, backdrop_pixel);
        let filtered = canvas
            .create_image_empty(W as usize, H as usize, PixelFormat::Rgba8, ImageFlags::FLIP_Y | ImageFlags::PREMULTIPLIED | ImageFlags::NEAREST)
            .unwrap();
        let blend = ImageFilter::Blend { mode: BlendMode::PlusLighter, backdrop, x: 0.0, y: 0.0, width: W as f32, height: H as f32 };
        canvas.filter_image_chain(filtered, &[blend], source).unwrap();
        let pixels = render(&mut canvas, false, Color::rgba(0, 0, 0, 0), |c| {
            let mut p = Path::new();
            p.rect(0.0, 0.0, W as f32, H as f32);
            let mut paint = Paint::image(filtered, 0.0, 0.0, W as f32, H as f32, 0.0, 1.0);
            paint.set_anti_alias(false);
            c.fill_path(&p, &paint);
        });
        check("feBlend plus-lighter", &pixels, &|x, y| {
            let (s, b) = (source_pixel(x, y), backdrop_pixel(x, y));
            [0, 1, 2, 3].map(|i| s[i].saturating_add(b[i]))
        });

        // A plus-lighter layer: red (100, 0, 0) on the left half, a layer adding half-opaque orange (200, 100, 0)
        // over the right three quarters - on an image target and on the screen.
        for screen in [false, true] {
            let pixels = render(&mut canvas, screen, Color::rgba(0, 0, 0, 0), |c| {
                fill(c, 0.0, 8.0, Color::rgb(100, 0, 0));
                assert!(c.begin_layer(&LayerEffects::new().with_blend(BlendMode::PlusLighter)));
                fill(c, 4.0, 12.0, Color::rgba(200, 100, 0, 128));
                c.end_layer();
            });
            let name = if screen { "plus-lighter layer on the screen" } else { "plus-lighter layer on an image" };
            check(name, &pixels, &|x, _| match x {
                0..4 => [100, 0, 0, 255],
                4..8 => [200, 50, 0, 255],
                _ => [100, 50, 0, 128],
            });
        }

        println!("{}", if failed { "GL PLUS-LIGHTER CHECK FAILED" } else { "GL PLUS-LIGHTER CHECK OK" });
        event_loop.exit();
    }

    fn window_event(&mut self, _: &ActiveEventLoop, _: winit::window::WindowId, _: WindowEvent) {}
}

fn main() {
    let event_loop = EventLoop::new().unwrap();
    event_loop.run_app(&mut App { done: false }).unwrap();
}
