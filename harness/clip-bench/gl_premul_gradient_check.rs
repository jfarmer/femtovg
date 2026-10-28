//! femtovg#438's premultiplied two-stop gradients on the OpenGL backend, without a visible window: a linear and a
//! box gradient from red to transparent blue, straight and premultiplied, on a transparent image target, against
//! the expected mix. Copy to `examples/gl_premul_gradient_check.rs` of a checkout with
//! `Paint::with_premultiplied_interpolation` and `cargo run --example gl_premul_gradient_check`; prints
//! `GL PREMUL GRADIENT CHECK OK`.
use std::num::NonZeroU32;

use femtovg::{renderer::OpenGl, Canvas, Color, ImageFlags, Paint, Path, PixelFormat, RenderTarget};
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

const W: u32 = 64;
const H: u32 = 16;

struct App {
    done: bool,
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
        let (red, blue0) = (Color::rgb(255, 0, 0), Color::rgba(0, 0, 255, 0));
        for premul in [false, true] {
            for boxed in [false, true] {
                let pixels = render(&mut canvas, false, Color::rgba(0, 0, 0, 0), |c| {
                    let mut p = Path::new();
                    p.rect(0.0, 0.0, W as f32, H as f32);
                    let paint = if boxed {
                        // A box gradient with a feather spanning the width: t runs 0..1 left to right.
                        Paint::box_gradient(-(W as f32), -1000.0, W as f32, 2000.0, 0.0, 2.0 * W as f32, red, blue0)
                    } else {
                        Paint::linear_gradient(0.0, 0.0, W as f32, 0.0, red, blue0)
                    }
                    .with_premultiplied_interpolation(premul);
                    c.fill_path(&p, &paint);
                });
                // Compare the row's ramp shape with the expected mix at the t each pixel's alpha implies.
                let mut worst = 0i32;
                for x in 0..W {
                    let [r, g, b, a] = pixels[(H / 2 * W + x) as usize];
                    let t = 1.0 - a as f32 / 255.0;
                    let want = if premul {
                        [(1.0 - t) * 255.0, 0.0, 0.0]
                    } else {
                        [(1.0 - t) * (1.0 - t) * 255.0, 0.0, t * (1.0 - t) * 255.0]
                    };
                    for (got, want) in [r, g, b].iter().zip(want) {
                        worst = worst.max((*got as i32 - want.round() as i32).abs());
                    }
                }
                let ok = worst <= 3;
                println!("{} {}: worst {worst}/255 {}", if boxed { "box" } else { "linear" }, if premul { "premultiplied" } else { "straight" }, if ok { "ok" } else { "WRONG" });
                failed |= !ok;
            }
        }
        println!("{}", if failed { "GL PREMUL GRADIENT CHECK FAILED" } else { "GL PREMUL GRADIENT CHECK OK" });
        event_loop.exit();
    }

    fn window_event(&mut self, _: &ActiveEventLoop, _: winit::window::WindowId, _: WindowEvent) {}
}

fn main() {
    let event_loop = EventLoop::new().unwrap();
    event_loop.run_app(&mut App { done: false }).unwrap();
}
