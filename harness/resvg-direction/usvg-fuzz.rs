// scratch, not committed: random nesting of tspans with unicode-bidi/direction, x lists and Arabic/Latin text must not panic
// and must lay out the same glyphs as the same text without the bidi attributes.
struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 { self.0 ^= self.0 << 13; self.0 ^= self.0 >> 7; self.0 ^= self.0 << 17; self.0 }
    fn pick<'a, T>(&mut self, v: &'a [T]) -> &'a T { &v[(self.next() % v.len() as u64) as usize] }
}
fn build(r: &mut Rng, depth: usize, with_bidi: bool, out: &mut String) {
    let words = ["ABC", "abc def", "ابجد", "هوز ", " 123 ", "x", "(a)", "\u{200F}", "\u{202B}q\u{202C}", "שלום"];
    let n = 1 + r.next() % 3;
    for _ in 0..n {
        match r.next() % 4 {
            0 if depth < 4 => {
                let ub = *r.pick(&["normal", "embed", "bidi-override", "isolate", "isolate-override", "plaintext"]);
                let dir = *r.pick(&["ltr", "rtl"]);
                let x = if r.next() % 5 == 0 { format!(" x=\"{}\"", 20 + r.next() % 150) } else { String::new() };
                let attrs = if with_bidi { format!(" unicode-bidi=\"{ub}\" direction=\"{dir}\"") } else { String::new() };
                out.push_str(&format!("<tspan{attrs}{x} fill=\"#{:x}{:x}0\">", r.next() % 9, r.next() % 9));
                build(r, depth + 1, with_bidi, out);
                out.push_str("</tspan>");
            }
            _ => out.push_str(*r.pick(&words)),
        }
    }
}
fn main() {
    let mut opt = usvg::Options::default();
    opt.fontdb_mut().load_fonts_dir(env!("CARGO_MANIFEST_DIR").to_string() + "/../resvg/tests/fonts");
    opt.font_family = "Noto Sans".to_string();
    let n: u64 = std::env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(2000);
    let (mut bad, mut checked) = (0, 0);
    for seed in 1..=n {
        let mut body = String::new();
        let mut r = Rng(seed * 0x9E3779B97F4A7C15);
        build(&mut r, 0, true, &mut body);
        let mut r = Rng(seed * 0x9E3779B97F4A7C15);
        let mut plain = String::new();
        build(&mut r, 0, false, &mut plain);
        let dir = if seed % 2 == 0 { "rtl" } else { "ltr" };
        let anchor = ["start", "middle", "end"][(seed % 3) as usize];
        let path = if seed % 7 == 0 { r#"<defs><path id="p" d="M 10 100 Q 100 20 190 100"/></defs>"# } else { "" };
        let wrap = |b: &str, d: &str| if seed % 7 == 0 {
            format!(r##"<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200">{path}<text font-size="12" direction="{d}" text-anchor="{anchor}"><textPath xlink:href="#p">{b}</textPath></text></svg>"##)
        } else {
            format!(r##"<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><text x="100" y="100" font-size="12" direction="{d}" text-anchor="{anchor}">{b}</text></svg>"##)
        };
        let (a, b) = (wrap(&body, dir), wrap(&plain, dir));
        let res = std::panic::catch_unwind(|| {
            let t1 = usvg::Tree::from_str(&a, &{ let mut o = usvg::Options::default(); o.fontdb_mut().load_fonts_dir(env!("CARGO_MANIFEST_DIR").to_string() + "/../resvg/tests/fonts"); o.font_family = "Noto Sans".into(); o });
            let t2 = usvg::Tree::from_str(&b, &{ let mut o = usvg::Options::default(); o.fontdb_mut().load_fonts_dir(env!("CARGO_MANIFEST_DIR").to_string() + "/../resvg/tests/fonts"); o.font_family = "Noto Sans".into(); o });
            let count = |t: &Result<usvg::Tree, usvg::Error>| -> Option<(usize, bool)> {
                let t = t.as_ref().ok()?;
                let mut n = 0; let mut finite = true;
                fn walk(n: &usvg::Node, c: &mut usize, f: &mut bool) {
                    match n { usvg::Node::Group(g) => g.children().iter().for_each(|x| walk(x, c, f)),
                        usvg::Node::Text(t) => for s in t.layouted() { for g in &s.positioned_glyphs { *c += 1; let m = g.transform(); *f &= m.tx.is_finite() && m.ty.is_finite(); } },
                        _ => {} }
                }
                t.root().children().iter().for_each(|c| walk(c, &mut n, &mut finite));
                Some((n, finite))
            };
            (count(&t1), count(&t2))
        });
        checked += 1;
        match res {
            Err(_) => { bad += 1; println!("seed {seed}: PANIC\n{a}"); }
            Ok((Some((n1, f1)), Some((n2, _)))) => if !f1 || n1 != n2 { bad += 1; println!("seed {seed}: glyphs {n1} vs {n2} finite {f1}\n{a}"); },
            Ok((None, None)) => {}
            Ok(_) => { bad += 1; println!("seed {seed}: one side failed to parse"); }
        }
    }
    println!("{checked} checked, {bad} bad");
}
