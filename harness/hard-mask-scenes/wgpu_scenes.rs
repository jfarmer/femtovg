#![cfg(feature = "wgpu")]
// Scratch (not for commit): draws the scenes of SCENES (a JSON file) with femtovg on a transparent target and saves
// each, over white, as SCENES_OUT/<index>.png, for comparison with the same scenes on a Chromium canvas.

use femtovg::{renderer::WGPURenderer, Canvas, Color, CompositeOperation, FillRule, Paint, Path};

mod common;
use common::{headless_device, render_rgba};

fn polygon(points: &[serde_json::Value]) -> Path {
    let mut path = Path::new();
    for (i, p) in points.iter().enumerate() {
        let (x, y) = (p[0].as_f64().unwrap() as f32, p[1].as_f64().unwrap() as f32);
        if i == 0 {
            path.move_to(x, y);
        } else {
            path.line_to(x, y);
        }
    }
    path.close();
    path
}

/// A path of several closed contours, each a list of points.
fn contours(contours: &[serde_json::Value]) -> Path {
    let mut path = Path::new();
    for contour in contours {
        for (i, p) in contour.as_array().unwrap().iter().enumerate() {
            let (x, y) = (p[0].as_f64().unwrap() as f32, p[1].as_f64().unwrap() as f32);
            if i == 0 {
                path.move_to(x, y);
            } else {
                path.line_to(x, y);
            }
        }
        path.close();
    }
    path
}

/// The fill rule an op names, as the argument of ctx.fill() and ctx.clip(): non-zero unless "evenodd".
fn rule(name: Option<&serde_json::Value>) -> FillRule {
    match name.and_then(|rule| rule.as_str()) {
        Some("evenodd") => FillRule::EvenOdd,
        _ => FillRule::NonZero,
    }
}

fn color(hex: &str) -> Color {
    Color::hex(hex)
}

#[test]
fn zz_hm_scenes() {
    let (Ok(spec), Ok(out)) = (std::env::var("SCENES"), std::env::var("SCENES_OUT")) else {
        return;
    };
    let Some((device, queue)) = headless_device() else {
        return;
    };
    let spec: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(spec).unwrap()).unwrap();
    // SCENES_SCALE draws each scene that many device pixels a canvas pixel, as a canvas of that devicePixelRatio.
    let scale: f32 = std::env::var("SCENES_SCALE").map_or(1.0, |s| s.parse().unwrap());
    let (w, h) = (spec["width"].as_u64().unwrap() as f32, spec["height"].as_u64().unwrap() as f32);
    let (w, h) = ((w * scale).round() as u32, (h * scale).round() as u32);
    for (i, scene) in spec["scenes"].as_array().unwrap().iter().enumerate() {
        let ops = scene["ops"].as_array().unwrap().clone();
        let rgba = render_rgba(&device, &queue, w, h, Color::rgbaf(0.0, 0.0, 0.0, 0.0), |canvas: &mut Canvas<WGPURenderer>| {
            canvas.scale(scale, scale);
            for op in &ops {
                match op[0].as_str().unwrap() {
                    "save" => canvas.save(),
                    "restore" => canvas.restore(),
                    "clip" => canvas.clip_path(&polygon(op[1].as_array().unwrap()), FillRule::NonZero),
                    "composite" => canvas.global_composite_operation(match op[1].as_str().unwrap() {
                        "source-over" => CompositeOperation::SourceOver,
                        "source-in" => CompositeOperation::SourceIn,
                        "source-out" => CompositeOperation::SourceOut,
                        "source-atop" => CompositeOperation::Atop,
                        "destination-over" => CompositeOperation::DestinationOver,
                        "destination-in" => CompositeOperation::DestinationIn,
                        "destination-out" => CompositeOperation::DestinationOut,
                        "destination-atop" => CompositeOperation::DestinationAtop,
                        "lighter" => CompositeOperation::Lighter,
                        "copy" => CompositeOperation::Copy,
                        "xor" => CompositeOperation::Xor,
                        // Chromium's legacy `clear` keeps none of source or destination: for the opaque fills of the
                        // scenes that is destination-out.
                        "clear" => CompositeOperation::DestinationOut,
                        other => panic!("no composite operation {other}"),
                    }),
                    "fill" => canvas.fill_path(
                        &polygon(op[2].as_array().unwrap()),
                        &Paint::color(color(op[1].as_str().unwrap())),
                    ),
                    "fillpath" => canvas.fill_path(
                        &contours(op[2].as_array().unwrap()),
                        &Paint::color(color(op[1].as_str().unwrap())).with_fill_rule(rule(op.get(3))),
                    ),
                    "clippath" => canvas.clip_path(&contours(op[1].as_array().unwrap()), rule(op.get(2))),
                    other => panic!("unknown op {other}"),
                }
            }
        });
        // Premultiplied over white.
        let mut rgb = image::RgbImage::new(w, h);
        for (n, px) in rgb.pixels_mut().enumerate() {
            let a = rgba[n * 4 + 3] as f32 / 255.0;
            for c in 0..3 {
                px[c] = (rgba[n * 4 + c] as f32 + (1.0 - a) * 255.0).round().min(255.0) as u8;
            }
        }
        rgb.save(format!("{out}/{i}.png")).unwrap();
    }
}
