#![cfg(feature = "wgpu")]
// Scratch probe (not for commit): does a concave fill under a hard coverage mask leave
// winding bits in the stencil where the mask discards its cover draw?

use femtovg::{renderer::WGPURenderer, Canvas, Color, CompositeOperation, FillRule, Paint, Path};

mod common;
use common::{headless_device, render_rgba};

const W: u32 = 120;
const H: u32 = 120;

fn px(buf: &[u8], x: u32, y: u32) -> [u8; 3] {
    let i = ((y * W + x) * 4) as usize;
    [buf[i], buf[i + 1], buf[i + 2]]
}

fn polygon(points: &[(f32, f32)]) -> Path {
    let mut path = Path::new();
    path.move_to(points[0].0, points[0].1);
    for &(x, y) in &points[1..] {
        path.line_to(x, y);
    }
    path.close();
    path
}

fn frame(op: CompositeOperation, then_second: bool) -> Option<Vec<u8>> {
    let (device, queue) = headless_device()?;
    Some(render_rgba(&device, &queue, W, H, Color::white(), |canvas: &mut Canvas<WGPURenderer>| {
        // A triangle: no box or ellipse, so the clip is a coverage mask.
        canvas.save();
        canvas.clip_path(&polygon(&[(0.0, 0.0), (60.0, 0.0), (0.0, 60.0)]), FillRule::NonZero);
        canvas.global_composite_operation(op);
        // A concave L reaching well outside the clip.
        let l = polygon(&[
            (10.0, 10.0),
            (110.0, 10.0),
            (110.0, 40.0),
            (40.0, 40.0),
            (40.0, 110.0),
            (10.0, 110.0),
        ]);
        canvas.fill_path(&l, &Paint::color(Color::rgb(255, 0, 0)));
        canvas.restore();
        if then_second {
            // A concave U whose bounds take in (87, 35), a point of the L outside the
            // clip, while its shape leaves that point out (the U's gap).
            let u = polygon(&[
                (35.0, 15.0),
                (58.0, 15.0),
                (58.0, 58.0),
                (53.0, 58.0),
                (53.0, 25.0),
                (45.0, 25.0),
                (45.0, 58.0),
                (35.0, 58.0),
            ]);
            canvas.fill_path(&u, &Paint::color(Color::rgb(0, 0, 255)));
        }
    }))
}

#[test]
fn probe_hard_mask_concave_fill_stencil() {
    for (name, op) in [
        ("source-over (soft mask)", CompositeOperation::SourceOver),
        ("copy (hard mask)", CompositeOperation::Copy),
        ("source-in (hard mask)", CompositeOperation::SourceIn),
        ("destination-in (hard mask)", CompositeOperation::DestinationIn),
    ] {
        let Some(only_l) = frame(op, false) else {
            eprintln!("skipping: no wgpu adapter");
            return;
        };
        let both = frame(op, true).unwrap();
        println!(
            "{name:28}: after L only (50,30)={:?} (20,20)={:?} | after L then U: gap (50,30)={:?} U bar (50,20)={:?}",
            px(&only_l, 50, 30),
            px(&only_l, 20, 20),
            px(&both, 50, 30),
            px(&both, 50, 20)
        );
    }
}
