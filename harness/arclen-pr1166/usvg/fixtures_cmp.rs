fn collect(node: &usvg::Node, out: &mut Vec<(f32, f32, f32, f32, f32, f32)>) {
    match node {
        usvg::Node::Group(g) => g.children().iter().for_each(|c| collect(c, out)),
        usvg::Node::Text(t) => {
            for s in t.layouted() {
                for g in &s.positioned_glyphs {
                    let m = g.transform();
                    out.push((m.tx, m.ty, m.sx, m.kx, m.ky, m.sy));
                }
            }
        }
        _ => {}
    }
}
fn main() {
    let mut opt = usvg::Options::default();
    opt.fontdb_mut().load_fonts_dir(env!("CARGO_MANIFEST_DIR").to_string() + "/../resvg/tests/fonts");
    opt.font_family = "Noto Sans".to_string();
    let (mut files, mut glyphs, mut worst_pos, mut worst_mat, mut worst05) = (0, 0, 0f32, 0f32, 0f32);
    for path in std::env::args().skip(1) {
        let Ok(text) = std::fs::read_to_string(&path) else { continue };
        let mut per = vec![];
        for v in [0u8, 2, 3] {
            usvg::__set_arc_variant(v);
            let Ok(tree) = usvg::Tree::from_str(&text, &opt) else { per.clear(); break };
            let mut g = vec![]; for c in tree.root().children() { collect(c, &mut g); }
            per.push(g);
        }
        if per.len() != 3 || per[0].is_empty() { continue; }
        files += 1; glyphs += per[0].len();
        let (mut p, mut m, mut p5) = (0f32, 0f32, 0f32);
        for i in 0..per[0].len() {
            let (a, b, c) = (per[0][i], per[1][i], per[2][i]);
            p = p.max((a.0 - b.0).hypot(a.1 - b.1)); p5 = p5.max((a.0 - c.0).hypot(a.1 - c.1));
            m = m.max((a.2 - b.2).abs()).max((a.3 - b.3).abs()).max((a.4 - b.4).abs()).max((a.5 - b.5).abs());
        }
        worst_pos = worst_pos.max(p); worst_mat = worst_mat.max(m); worst05 = worst05.max(p5);
        println!("{:60} {:4} glyphs  resume vs plain0.001: pos {:.5} matrix {:.6}   (plain0.5 vs plain0.001 pos {:.4})", path.rsplit('/').next().unwrap(), per[0].len(), p, m, p5);
    }
    println!("{files} files, {glyphs} glyphs: worst resume-vs-plain0.001 position {worst_pos:.5}, matrix {worst_mat:.6}; worst plain0.5-vs-plain0.001 position {worst05:.4}");
}
