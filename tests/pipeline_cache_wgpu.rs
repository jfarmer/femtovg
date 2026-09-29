//! The WGPU backend keeps its render pipelines across flushes. A flush that
//! binds only some of them, such as a lone clear, must leave the rest cached,
//! or the next flush that draws builds them again. Past a retention target the
//! cache evicts the pipelines used longest ago, but never one the flush bound.
#![cfg(feature = "wgpu")]

use femtovg::{
    renderer::WGPURenderer, BlendFactor, Canvas, Color, DrawCommand, FillRule, GlyphDrawCommands, ImageFilter,
    ImageFlags, LayerEffects, Paint, Path, PixelFormat, Quad,
};

mod common;
use common::headless_device;
use common::pipelines::{live_pipelines_after_flush, rect, target, SIZE};

/// The WGPU renderer's retention target: past it, a flush evicts pipelines it did not bind.
const CAPACITY: usize = 64;

/// Each round flushes `states - 1` fills in distinct blend states, then a
/// clear-only flush. Up to [`CAPACITY`] states every pipeline stays alive, so
/// nothing can be evicted and an unchanged count means the second round built
/// none. One past it, the clear-only flush trims the cache to [`CAPACITY`] and
/// a drawing flush keeps every pipeline it binds.
#[test]
fn pipelines_stay_alive_up_to_capacity() {
    let Some((device, queue)) = headless_device() else {
        return;
    };
    let target = target(&device);
    let factors = [
        BlendFactor::One,
        BlendFactor::OneMinusSrcAlpha,
        BlendFactor::Zero,
        BlendFactor::SrcColor,
        BlendFactor::OneMinusSrcColor,
        BlendFactor::DstColor,
        BlendFactor::OneMinusDstColor,
        BlendFactor::SrcAlpha,
        BlendFactor::DstAlpha,
        BlendFactor::OneMinusDstAlpha,
    ];
    // No anti-aliasing: each fill's blend state needs one pipeline, and the clear one more.
    let red = Paint::color(Color::rgb(255, 0, 0)).with_anti_alias(false);
    for states in [CAPACITY - 1, CAPACITY, CAPACITY + 1] {
        let mut canvas = Canvas::new(WGPURenderer::new(device.clone(), queue.clone())).expect("canvas");
        canvas.set_size(SIZE, SIZE, 1.0);
        for round in 0..2 {
            canvas.save();
            for i in 0..states - 1 {
                canvas.global_composite_blend_func_separate(
                    factors[i % 10],
                    factors[i / 10],
                    BlendFactor::One,
                    BlendFactor::OneMinusSrcAlpha,
                );
                canvas.fill_path(&rect(), &red);
            }
            canvas.restore();
            let drawn = live_pipelines_after_flush(&device, &queue, &mut canvas, &target);
            canvas.clear_rect(0, 0, SIZE, SIZE, Color::black());
            let cleared = live_pipelines_after_flush(&device, &queue, &mut canvas, &target);

            let expected_drawn = if round == 0 || states > CAPACITY {
                states - 1
            } else {
                states
            };
            assert_eq!(
                drawn, expected_drawn as isize,
                "{states} states, round {round}: pipelines alive after the drawing flush"
            );
            assert_eq!(
                cleared,
                states.min(CAPACITY) as isize,
                "{states} states, round {round}: pipelines alive after the clear-only flush"
            );
        }
        drop(canvas);
        device
            .poll(wgpu::PollType::wait_indefinitely())
            .expect("device poll failed");
    }
}

/// Glyph, clipped-layer, filter, screen and clear-only flushes in turn. Their
/// pipelines stay far below [`CAPACITY`], so nothing can be evicted, and every
/// flush after the first round leaving the count unchanged means none built a
/// pipeline.
#[test]
fn alternating_flushes_reuse_their_pipelines_after_the_first_round() {
    let Some((device, queue)) = headless_device() else {
        return;
    };
    let target = target(&device);
    let mut canvas = Canvas::new(WGPURenderer::new(device.clone(), queue.clone())).expect("canvas");
    canvas.set_size(SIZE, SIZE, 1.0);
    let atlas = canvas
        .create_image_empty(8, 8, PixelFormat::Gray8, ImageFlags::empty())
        .expect("glyph atlas");
    let red = Paint::color(Color::rgb(255, 0, 0));
    let mut circle = Path::new();
    circle.circle(32.0, 32.0, 24.0);
    let mut concave = Path::new();
    concave.move_to(0.0, 0.0);
    concave.line_to(60.0, 10.0);
    concave.line_to(10.0, 60.0);
    concave.line_to(50.0, 50.0);
    concave.close();

    let mut rounds = Vec::new();
    for _ in 0..2 {
        let mut alive = Vec::new();

        let glyph = Quad {
            x0: 8.0,
            y0: 8.0,
            s0: 0.0,
            t0: 0.0,
            x1: 16.0,
            y1: 16.0,
            s1: 1.0,
            t1: 1.0,
        };
        canvas.draw_glyph_commands(
            GlyphDrawCommands {
                alpha_glyphs: vec![DrawCommand {
                    image_id: atlas,
                    quads: vec![glyph],
                }],
                color_glyphs: Vec::new(),
            },
            &red,
        );
        alive.push(live_pipelines_after_flush(&device, &queue, &mut canvas, &target));

        canvas.save();
        canvas.clip_path(&circle, FillRule::NonZero);
        assert!(canvas.begin_layer(&LayerEffects::new().with_opacity(0.5)));
        canvas.fill_path(&rect(), &red);
        canvas.end_layer();
        canvas.restore();
        alive.push(live_pipelines_after_flush(&device, &queue, &mut canvas, &target));

        assert!(canvas.begin_layer(&LayerEffects::new().with_filters(&[ImageFilter::GaussianBlur { sigma: 3.0 }])));
        canvas.fill_path(&rect(), &red);
        canvas.end_layer();
        alive.push(live_pipelines_after_flush(&device, &queue, &mut canvas, &target));

        canvas.fill_path(&rect(), &red);
        canvas.fill_path(
            &circle,
            &Paint::linear_gradient(0.0, 0.0, 64.0, 64.0, Color::black(), Color::white()),
        );
        canvas.stroke_path(&circle, &Paint::color(Color::rgb(0, 0, 255)).with_line_width(3.0));
        canvas.save();
        canvas.scissor(0.0, 0.0, 30.0, 30.0);
        canvas.fill_path(&concave, &red);
        canvas.restore();
        alive.push(live_pipelines_after_flush(&device, &queue, &mut canvas, &target));

        canvas.clear_rect(0, 0, SIZE, SIZE, Color::black());
        alive.push(live_pipelines_after_flush(&device, &queue, &mut canvas, &target));

        rounds.push(alive);
    }

    let settled = rounds[0][rounds[0].len() - 1];
    assert!(
        rounds[1].iter().all(|&alive| alive == settled),
        "{settled} pipelines were alive after the first round, but the second round's flushes left {:?}",
        rounds[1]
    );
}
