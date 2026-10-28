"""Experiment only, never committed: environment knobs on the PR head that change which pooled image a layer takes.
  X_RELEASE=1  end_layer returns the chain's result to the pool before the capture (the next capture pops the capture)
  X_TAG=1      the chain's result carries an extra flag bit, so it never shares a pool bucket with a capture
  X_FIFO=1     a pool bucket hands out its oldest image instead of its newest
usage: knobs_patch.py WORKTREE"""
import pathlib, sys
wt = pathlib.Path(sys.argv[1])
def edit(rel, pairs, append=''):
    f = wt / rel; s = f.read_text()
    for old, new in pairs:
        assert s.count(old) == 1, (rel, s.count(old), old)
        s = s.replace(old, new)
    f.write_text(s + append)
edit('src/layers.rs', [
    ("""        for image in record.images().chain(filtered) {
            self.release_transient_image(image);
        }""", """        if crate::transient::xknob(0) {
            for image in filtered.into_iter().chain(record.images()) {
                self.release_transient_image(image);
            }
            return;
        }
        for image in record.images().chain(filtered) {
            self.release_transient_image(image);
        }"""),
    ("""        let target = self
            .acquire_transient_image_reserving(width, height, flags, headroom)
            .ok()?;
        // The result and the chain scratches are plain render targets alike,""", """        let flags = if crate::transient::xknob(1) {
            flags | ImageFlags::from_bits_retain(1 << 8)
        } else {
            flags
        };
        let target = self
            .acquire_transient_image_reserving(width, height, flags, headroom)
            .ok()?;
        // The result and the chain scratches are plain render targets alike,"""),
])
edit('src/transient.rs', [
    ("""        let id = bucket.pop()?;""", """        let id = if xknob(2) {
            if bucket.is_empty() {
                return None;
            }
            bucket.remove(0)
        } else {
            bucket.pop()?
        };"""),
], append='''
/// Experiment only: environment knobs.
pub(crate) fn xknob(index: usize) -> bool {
    static KNOBS: std::sync::OnceLock<[bool; 4]> = std::sync::OnceLock::new();
    KNOBS.get_or_init(|| ["X_RELEASE", "X_TAG", "X_FIFO", "X_SPARE"].map(|name| std::env::var_os(name).is_some()))[index]
}
''')
print('knobs added to', wt)
