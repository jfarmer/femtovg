// scratch, not committed: text -> to_string(preserve_text) -> text must keep every glyph where it was
fn glyphs(tree: &usvg::Tree) -> Vec<[f32; 6]> {
    fn walk(n: &usvg::Node, out: &mut Vec<[f32; 6]>) {
        match n {
            usvg::Node::Group(g) => g.children().iter().for_each(|c| walk(c, out)),
            usvg::Node::Text(t) => {
                for s in t.layouted() {
                    for g in &s.positioned_glyphs {
                        let m = g.transform();
                        out.push([m.sx, m.ky, m.kx, m.sy, m.tx, m.ty]);
                    }
                }
            }
            _ => {}
        }
    }
    let mut v = vec![];
    tree.root().children().iter().for_each(|c| walk(c, &mut v));
    v
}
fn main() {
    let mut opt = usvg::Options::default();
    opt.fontdb_mut()
        .load_fonts_dir(env!("CARGO_MANIFEST_DIR").to_string() + "/../resvg/tests/fonts");
    opt.font_family = "Noto Sans".to_string();
    let mut bad = 0;
    for path in std::env::args().skip(1) {
        let text = std::fs::read_to_string(&path).unwrap();
        let t1 = usvg::Tree::from_str(&text, &opt).unwrap();
        let xml = t1.to_string(&usvg::WriteOptions {
            preserve_text: true,
            ..Default::default()
        });
        if std::env::var("PRINT").is_ok() {
            println!("{xml}");
        }
        let t2 = match usvg::Tree::from_str(&xml, &opt) {
            Ok(t) => t,
            Err(e) => {
                println!("{path}: reparse failed {e}");
                bad += 1;
                continue;
            }
        };
        let (a, b) = (glyphs(&t1), glyphs(&t2));
        let worst = a
            .iter()
            .zip(&b)
            .map(|(x, y)| (0..6).map(|i| (x[i] - y[i]).abs()).fold(0f32, f32::max))
            .fold(0f32, f32::max);
        let ok = a.len() == b.len() && worst < 1e-3;
        if !ok {
            bad += 1;
        }
        println!(
            "{} {:<70} glyphs {} -> {}, worst {:.5}",
            if ok { "ok " } else { "BAD" },
            path.rsplit("tests/").next().unwrap(),
            a.len(),
            b.len(),
            worst
        );
    }
    println!("{bad} bad");
}
