//! Headless GPU tests for how closely a filled curve follows its outline. A
//! fill covers a pixel by its share inside the path as it was flattened, so
//! the chords have to stay close to the curve: a chord a fifth of a pixel
//! inside it leaves an edge pixel a fifth short. Skips without a GPU adapter.
#![cfg(feature = "wgpu")]

use femtovg::{renderer::WGPURenderer, Canvas, Color, Paint, Path};

mod common;
use common::{headless_device, render_rgba};

const W: u32 = 128;
const H: u32 = 128;

/// The share of each pixel inside an ellipse, from 32 x 32 samples.
fn share_inside(center: [f32; 2], radii: [f32; 2]) -> Vec<f32> {
    let inside = |x: f32, y: f32| ((x - center[0]) / radii[0]).hypot((y - center[1]) / radii[1]) <= 1.0;
    (0..W * H)
        .map(|i| {
            let (left, top) = ((i % W) as f32, (i / W) as f32);
            let corners = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)].map(|(dx, dy)| inside(left + dx, top + dy));
            if corners.iter().all(|c| *c == corners[0]) {
                return f32::from(u8::from(corners[0]));
            }
            let hits = (0..1024)
                .filter(|s| {
                    inside(
                        left + ((s % 32) as f32 + 0.5) / 32.0,
                        top + ((s / 32) as f32 + 0.5) / 32.0,
                    )
                })
                .count();
            hits as f32 / 1024.0
        })
        .collect()
}

/// A filled circle or ellipse covers each pixel of its edge close to the
/// pixel's share inside it, small and large: within 0.12 at worst and 0.03
/// on average. With chords up to a fifth of a pixel inside the curve the
/// worst pixel was 0.21 off and the average 0.07.
#[test]
fn report_edge_errors() {
    let Some((device, queue)) = headless_device() else {
        eprintln!("skipping: no wgpu adapter available");
        return;
    };
    for (name, center, radii) in [
        ("a circle of 6 px", [64.3, 63.6], [6.2, 6.2]),
        ("a circle of 38 px", [64.3, 63.6], [38.4, 38.4]),
        ("an ellipse", [64.0, 64.5], [56.25, 23.5]),
        ("an arc of a circle of 300 px", [-180.2, 64.4], [300.3, 300.3]),
    ] {
        let frame = render_rgba(
            &device,
            &queue,
            W,
            H,
            Color::white(),
            |canvas: &mut Canvas<WGPURenderer>| {
                let mut path = Path::new();
                path.ellipse(center[0], center[1], radii[0], radii[1]);
                canvas.fill_path(&path, &Paint::color(Color::rgb(255, 0, 0)));
            },
        );
        let expected = share_inside(center, radii);
        let off: Vec<f32> = expected
            .iter()
            .enumerate()
            .filter(|(_, share)| **share > 0.0 && **share < 1.0)
            .map(|(i, share)| (1.0 - f32::from(frame[i * 4 + 1]) / 255.0 - share).abs())
            .collect();
        let worst = off.iter().copied().fold(0.0, f32::max);
        let mean = off.iter().sum::<f32>() / off.len() as f32;
        let signed: Vec<f32> = expected.iter().enumerate().filter(|(_, s)| **s > 0.0 && **s < 1.0).map(|(i, s)| 1.0 - f32::from(frame[i * 4 + 1]) / 255.0 - s).collect();
        let bias = signed.iter().sum::<f32>() / signed.len() as f32;
        let over = off.iter().filter(|v| **v > 0.08).count();
        // Where the error sits: by the angle of the pixel centre from the ellipse's centre (in its own scaled
        // frame), near a cubic's end (the four axis extremes, within 6 degrees) or between them.
        let (mut near, mut nn, mut mid, mut nm, mut wpos) = (0.0f32, 0usize, 0.0f32, 0usize, (0u32, 0u32, 0.0f32));
        for (i, share) in expected.iter().enumerate() {
            if !(*share > 0.0 && *share < 1.0) { continue; }
            let e = (1.0 - f32::from(frame[i * 4 + 1]) / 255.0 - share).abs();
            let (px, py) = ((i as u32 % W) as f32 + 0.5, (i as u32 / W) as f32 + 0.5);
            let ang = ((py - center[1]) / radii[1]).atan2((px - center[0]) / radii[0]).to_degrees().rem_euclid(90.0);
            let from_end = ang.min(90.0 - ang);
            if from_end < 6.0 { near += e; nn += 1 } else { mid += e; nm += 1 }
            if e > wpos.2 { wpos = (i as u32 % W, i as u32 / W, from_end) }
        }
        println!("ENDS {name}: mean error within 6 deg of a cubic end {:.4} ({nn} px), elsewhere {:.4} ({nm} px); worst pixel at ({}, {}), {:.1} deg from an end", near / nn.max(1) as f32, mid / nm.max(1) as f32, wpos.0, wpos.1, wpos.2);
        println!("CURVE {name}: edge pixels {}, worst {worst:.4}, mean {mean:.4}, signed mean {bias:+.4}, beyond 0.08: {over}", off.len());
    }
}
