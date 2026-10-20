use femtovg::renderer::Void;
use femtovg::{Canvas, Color, Paint, Path};

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let zoom: f32 = args[1].parse().unwrap();
    let toks: Vec<&str> = args[2].split_whitespace().collect();
    let mut canvas = Canvas::new(Void).unwrap();
    canvas.set_size(460, 260, 1.0);
    if std::env::var("NO_MASKS").is_ok() { canvas.set_thin_fill_masks(false); }
    canvas.translate(230.0, 130.0);
    canvas.scale(zoom, zoom);
    canvas.translate(-230.0, -130.0);
    canvas.translate(130.0, 30.0);
    let fit = 200.0f32 / 1024.0;
    canvas.scale(fit, fit);
    let mut p = Path::new();
    let mut i = 0;
    let f = |s: &str| s.parse::<f32>().unwrap();
    while i < toks.len() {
        match toks[i] {
            "M" => { p.move_to(f(toks[i+1]), f(toks[i+2])); i += 3; }
            "L" => { p.line_to(f(toks[i+1]), f(toks[i+2])); i += 3; }
            "C" => { p.bezier_to(f(toks[i+1]), f(toks[i+2]), f(toks[i+3]), f(toks[i+4]), f(toks[i+5]), f(toks[i+6])); i += 7; }
            "Z" => { p.close(); i += 1; }
            t => panic!("token {t}"),
        }
    }
    canvas.fill_path(&p, &Paint::color(Color::black()));
    canvas.flush_to_output(());
}
