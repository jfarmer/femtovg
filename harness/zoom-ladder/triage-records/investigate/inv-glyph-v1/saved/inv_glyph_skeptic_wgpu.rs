//! Skeptic experiments for the glyph atlas history bug. Writes every case's
//! last frame as a PPM to $SKEPTIC_OUT; comparisons are done in Python.
#![cfg(all(feature = "wgpu", feature = "textlayout"))]

use femtovg::{Color, Paint, PositionedGlyph};

mod common;
use common::{headless_device, render_frames};

const W: u32 = 460;
const H: u32 = 260;
const FONT: &[u8] = include_bytes!("../examples/assets/RobotoFlex-VariableFont.ttf");

const LINES: [(f32, f32, &str); 3] = [
    (-0.3, 40.0, "Offset -0.3px"),
    (-0.7, 80.0, "Offset -0.7px"),
    (-15.4, 120.0, "Offset -15.4px"),
];
// Different glyphs, used only to move atlas cells at the same scale.
const OTHER: [(f32, f32, &str); 1] = [(0.0, 40.0, "QWERTYZ bdhk 0123456789")];

#[derive(Clone, Copy)]
enum Api {
    GlyphRun,
    PathRef,
    Stroke,
}

#[derive(Clone, Copy)]
struct Step {
    s: f32,
    tx: f32,
    ty: f32,
    other: bool,
}

fn st(s: f32, tx: f32, ty: f32) -> Step {
    Step { s, tx, ty, other: false }
}

fn run(device: &wgpu::Device, queue: &wgpu::Queue, api: Api, steps: &[Step]) -> Vec<u8> {
    let mut font = None;
    let steps = steps.to_vec();
    let mut frames = render_frames(device, queue, W, H, Color::white(), steps.len(), |canvas, i| {
        let font = *font.get_or_insert_with(|| canvas.add_font_mem(FONT).unwrap());
        let c = Color::rgb(0x22, 0x22, 0x22);
        let paint = Paint::color(c).with_font(&[font]).with_font_size(20.0);
        let path_paint = Paint::linear_gradient(0.0, 0.0, 1.0, 0.0, c, c)
            .with_font(&[font])
            .with_font_size(20.0);
        let step = steps[i];
        let lines: &[(f32, f32, &str)] = if step.other { &OTHER } else { &LINES };
        let runs: Vec<Vec<PositionedGlyph>> = lines
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
                    .collect()
            })
            .collect();
        canvas.save();
        canvas.translate(step.tx, step.ty);
        canvas.scale(step.s, step.s);
        for run in &runs {
            match api {
                Api::GlyphRun => canvas.fill_glyph_run(font, &[], run.iter().cloned(), &paint).unwrap(),
                Api::PathRef => canvas.fill_glyph_run(font, &[], run.iter().cloned(), &path_paint).unwrap(),
                Api::Stroke => canvas
                    .stroke_glyph_run(font, &[], run.iter().cloned(), &paint.clone().with_line_width(1.3))
                    .unwrap(),
            }
        }
        canvas.restore();
    });
    frames.pop().unwrap()
}

fn write_ppm(path: &str, px: &[u8]) {
    let mut out = format!("P6\n{W} {H}\n255\n").into_bytes();
    for p in px.chunks_exact(4) {
        out.extend_from_slice(&p[..3]);
    }
    std::fs::write(path, out).unwrap();
}

#[test]
fn skeptic_cases() {
    let Some((device, queue)) = headless_device() else {
        return;
    };
    let out = std::env::var("SKEPTIC_OUT").expect("SKEPTIC_OUT");
    let other_first = |s: f32, tx: f32, ty: f32| Step { s, tx, ty, other: true };
    let mut cases: Vec<(String, Api, Vec<Step>)> = Vec::new();
    for tx in [167.0f32, 167.25, 167.5, 167.75] {
        let t = st(0.625, tx, 5.0);
        cases.push((format!("fresh_s0.625_tx{tx}"), Api::GlyphRun, vec![t]));
        cases.push((format!("ladS0.5_s0.625_tx{tx}"), Api::GlyphRun, vec![st(0.5, 180.0, 30.0), t]));
        // Same quantized scale, different glyphs first: only the cells move.
        cases.push((format!("ladOther_s0.625_tx{tx}"), Api::GlyphRun, vec![other_first(0.625, 167.0, 5.0), t]));
        cases.push((format!("path_s0.625_tx{tx}"), Api::PathRef, vec![t]));
        cases.push((format!("strokefresh_s0.625_tx{tx}"), Api::Stroke, vec![t]));
    }
    // Half pixel in y only.
    let t = st(0.625, 167.0, 5.5);
    cases.push(("fresh_s0.625_ty5.5".into(), Api::GlyphRun, vec![t]));
    cases.push(("ladS0.5_s0.625_ty5.5".into(), Api::GlyphRun, vec![st(0.5, 180.0, 30.0), t]));
    cases.push(("ladOther_s0.625_ty5.5".into(), Api::GlyphRun, vec![other_first(0.625, 167.0, 5.0), t]));
    // Atlas regime (scale 1).
    for tx in [100.0f32, 100.5] {
        let t = st(1.0, tx, 5.0);
        cases.push((format!("fresh_s1_tx{tx}"), Api::GlyphRun, vec![t]));
        cases.push((format!("ladS0.5_s1_tx{tx}"), Api::GlyphRun, vec![st(0.5, 180.0, 30.0), t]));
        cases.push((format!("ladOther_s1_tx{tx}"), Api::GlyphRun, vec![other_first(1.0, 100.0, 5.0), t]));
        cases.push((format!("path_s1_tx{tx}"), Api::PathRef, vec![t]));
        cases.push((format!("strokefresh_s1_tx{tx}"), Api::Stroke, vec![t]));
    }
    if let Ok(custom) = std::env::var("SKEPTIC_CASE") {
        // "name:s,tx,ty;s,tx,ty|name2:..." -- ladder of steps; also writes the fresh last step.
        cases.clear();
        for item in custom.split('|') {
            let (name, spec) = item.split_once(':').unwrap();
            let steps: Vec<Step> = spec
                .split(';')
                .map(|t| {
                    let v: Vec<f32> = t.split(',').map(|n| n.trim().parse().unwrap()).collect();
                    st(v[0], v[1], v[2])
                })
                .collect();
            cases.push((format!("fresh_{name}"), Api::GlyphRun, vec![*steps.last().unwrap()]));
            cases.push((format!("lad_{name}"), Api::GlyphRun, steps));
        }
    }
    if let Ok(only) = std::env::var("SKEPTIC_ONLY") {
        cases.retain(|(n, _, _)| n.contains(&only));
    }
    for (name, api, steps) in &cases {
        let px = run(&device, &queue, *api, steps);
        write_ppm(&format!("{out}/{name}.ppm"), &px);
    }
}

/// One glyph at x = 10 + k/10 under an identity transform (Atlas regime):
/// if the GPU-drawn mask ignores the subpixel key, every k draws the same
/// pixels.
#[test]
fn skeptic_subpixel() {
    let Some((device, queue)) = headless_device() else {
        return;
    };
    let out = std::env::var("SKEPTIC_OUT").expect("SKEPTIC_OUT");
    for k in 0..10 {
        let x = 10.0 + k as f32 / 10.0;
        let mut font = None;
        let px = render_frames(&device, &queue, 64, 48, Color::white(), 1, |canvas, _| {
            let font = *font.get_or_insert_with(|| canvas.add_font_mem(FONT).unwrap());
            let paint = Paint::color(Color::black()).with_font(&[font]).with_font_size(20.0);
            let g = canvas.measure_text(0.0, 30.0, "H", &paint).unwrap().glyphs[0].glyph_id;
            canvas
                .fill_glyph_run(font, &[], [PositionedGlyph { x, y: 30.0, glyph_id: g }], &paint)
                .unwrap();
        })
        .pop()
        .unwrap();
        let mut o = format!("P6\n64 48\n255\n").into_bytes();
        for p in px.chunks_exact(4) {
            o.extend_from_slice(&p[..3]);
        }
        std::fs::write(format!("{out}/sub_k{k}.ppm"), o).unwrap();
    }
}
