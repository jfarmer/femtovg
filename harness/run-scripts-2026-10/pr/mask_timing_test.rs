
#[cfg(test)]
mod timing {
    use super::*;

    /// Not a test of anything: prints what rasterizing a mask costs.
    /// `cargo test --release --features wgpu --lib clip::mask::timing -- --ignored --nocapture`
    #[test]
    #[ignore]
    fn what_a_mask_costs() {
        let polygon = |points: usize, radius: f32, spike: f32, center: [f32; 2]| -> Vec<[f32; 2]> {
            (0..points)
                .map(|i| {
                    let angle = i as f32 / points as f32 * std::f32::consts::TAU;
                    let r = radius * if i % 2 == 0 { 1.0 } else { spike };
                    [center[0] + r * angle.cos(), center[1] + r * angle.sin()]
                })
                .collect()
        };
        let cases: [(&str, Vec<[f32; 2]>, [i32; 4]); 6] = [
            (
                "star, 10 points, 1000 px",
                polygon(10, 490.3, 0.4, [500.2, 500.7]),
                [0, 0, 1920, 1080],
            ),
            (
                "disc, 400 points, 1000 px",
                polygon(400, 490.3, 1.0, [500.2, 500.7]),
                [0, 0, 1920, 1080],
            ),
            (
                "burr, 2000 points, 1000 px",
                polygon(2000, 490.3, 0.93, [500.2, 500.7]),
                [0, 0, 1920, 1080],
            ),
            (
                "disc, 400 points, 1080p whole",
                polygon(400, 1400.0, 1.0, [960.0, 540.0]),
                [0, 0, 1920, 1080],
            ),
            (
                "star, 10 points, 200 px",
                polygon(10, 98.3, 0.4, [100.2, 100.7]),
                [0, 0, 1920, 1080],
            ),
            (
                "disc, 120 points, 64 px",
                polygon(120, 30.3, 1.0, [32.2, 32.7]),
                [0, 0, 1920, 1080],
            ),
        ];
        let mut coverage = Coverage::default();
        for (name, points, within) in cases {
            let mut outline = MaskOutline::default();
            outline.child(FillRule::NonZero, std::iter::once(points));
            let rect = outline.rect(within);
            let mut times: Vec<f64> = (0..40)
                .map(|_| {
                    let started = std::time::Instant::now();
                    let key = outline.key(rect, None);
                    let pixels = key.rasterize(&mut coverage);
                    std::hint::black_box(&pixels);
                    started.elapsed().as_secs_f64() * 1e6
                })
                .collect();
            times.sort_by(f64::total_cmp);
            let [width, height] = [rect[2] - rect[0], rect[3] - rect[1]];
            eprintln!("{name}: {width} x {height}, {:.0} us (best {:.0})", times[20], times[0]);
        }
    }
}
