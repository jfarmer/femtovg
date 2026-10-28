//! tiny-skia 0.12: an anti-aliased fill of a finite rect under a large but finite transform panics in AlphaRuns.
fn main() {
    let mut pixmap = tiny_skia::Pixmap::new(200, 200).unwrap();
    let rect = tiny_skia::Rect::from_xywh(-2048.0, -2048.0, 2049.0, 2049.0).unwrap();
    let path = tiny_skia::PathBuilder::from_rect(rect);
    let mut paint = tiny_skia::Paint::default();
    paint.set_color_rgba8(0, 128, 0, 255);
    paint.anti_alias = std::env::args().nth(1).map_or(true, |a| a != "noaa");
    let ts = tiny_skia::Transform::from_row(1045680.4, 77872.81, 14950.602, 1113.3856, 4.5376153, -7.8122635);
    pixmap.fill_path(&path, &paint, tiny_skia::FillRule::Winding, ts, None);
    println!("aa={} ink={}", paint.anti_alias, pixmap.pixels().iter().filter(|p| p.alpha() > 0).count());
}
