//! femtovg#132: Canvas::realloc_image on an image render target, OpenGL backend, hidden window.
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
const H: u32 = 48;

struct App {
    done: bool,
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


        // femtovg#132: an Rgb8 image target filled with "stars", drawn, then realloc'ed to a new size and filled
        // again. Each round reads the image back through a second target and counts pixels that are not what was
        // drawn into it.
        let mut stars = canvas
            .create_image_empty(40, 30, PixelFormat::Rgb8, ImageFlags::empty())
            .unwrap();
        let mut failed = false;
        for (round, (w, h)) in [(40u32, 30u32), (64, 48), (24, 20), (64, 48)].into_iter().enumerate() {
            for mode in ["realloc", "delete+create"] {
                if round > 0 {
                    if mode == "realloc" {
                        canvas.realloc_image(stars, w as usize, h as usize, PixelFormat::Rgb8, ImageFlags::empty()).unwrap();
                    } else {
                        canvas.delete_image(stars);
                        stars = canvas.create_image_empty(w as usize, h as usize, PixelFormat::Rgb8, ImageFlags::empty()).unwrap();
                    }
                }
                canvas.set_render_target(RenderTarget::Image(stars));
                canvas.clear_rect(0, 0, w, h, Color::black());
                let star = |i: u32| ((i * 7 + round as u32 * 3) % w, (i * 13 + 5) % h);
                let skip = std::env::var("SKIP_DRAW").is_ok() && round > 0;
                for i in 0..if skip { 0 } else { 40 } {
                    let (x, y) = star(i);
                    let mut p = Path::new();
                    p.rect(x as f32, y as f32, 1.0, 1.0);
                    canvas.fill_path(&p, &Paint::color(Color::white()));
                }
                canvas.set_render_target(RenderTarget::Screen);
                // Read the image back through another target, as the issue draws it to the screen.
                let out = canvas.create_image_empty(w as usize, h as usize, PixelFormat::Rgba8, ImageFlags::empty()).unwrap();
                canvas.set_render_target(RenderTarget::Image(out));
                canvas.clear_rect(0, 0, w, h, Color::rgb(255, 0, 255));
                let mut all = Path::new();
                all.rect(0.0, 0.0, w as f32, h as f32);
                canvas.fill_path(&all, &Paint::image(stars, 0.0, 0.0, w as f32, h as f32, 0.0, 1.0));
                canvas.flush_to_output(());
                let shot = canvas.screenshot().unwrap();
                let lit: std::collections::HashSet<(u32, u32)> = (0..40).map(star).collect();
                let white = shot.pixels().filter(|p| p.r == 255 && p.g == 255).count();
                // Count against both row orders and keep the better one: screenshot()'s order has varied.
                let mut wrong = [0, 0];
                for (i, p) in shot.pixels().enumerate() {
                    let (x, y) = (i as u32 % w, i as u32 / w);
                    for (k, yy) in [y, h - 1 - y].into_iter().enumerate() {
                        let want = if lit.contains(&(x, yy)) { 255 } else { 0 };
                        if !(p.r == want && p.g == want && p.b == want) {
                            wrong[k] += 1;
                        }
                    }
                }
                let wrong = wrong[0].min(wrong[1]);
                canvas.set_render_target(RenderTarget::Screen);
                canvas.flush_to_output(());
                canvas.delete_image(out);
                println!("round {round} {w}x{h} {mode}: {wrong} of {} pixels wrong ({white} white, {} stars drawn)", w * h, lit.len());
                failed |= wrong > 0;
                if round == 0 { break; }
            }
        }
        println!("{}", if failed { "GL REALLOC CHECK FAILED" } else { "GL REALLOC CHECK OK" });
        event_loop.exit();
    }

    fn window_event(&mut self, _: &ActiveEventLoop, _: winit::window::WindowId, _: WindowEvent) {}
}

fn main() {
    let event_loop = EventLoop::new().unwrap();
    event_loop.run_app(&mut App { done: false }).unwrap();
}
