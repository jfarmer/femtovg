#!/bin/zsh
# build_x.sh TAG:WORKTREE ... - like runs/pr/build_harness.sh, for this investigation's experiment worktrees:
# its own target directory, and the harness asks the device for timestamp queries when the adapter has them.
B=/Users/matt/src/femtovg-wt/bin; H=/Users/matt/src/femtovg-wt/da/harness/_logos_full.rs; R=/Users/matt/src/femtovg-wt/runs/x375
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-/Users/matt/src/femtovg-wt/target-pm}
export CARGO_PROFILE_RELEASE_DEBUG=0
for spec in "$@"; do
  tag=${spec%%:*}; wt=/Users/matt/src/femtovg-wt/${spec##*:}
  cd $wt || exit 1
  python3 - $H examples/_logos_full.rs <<'EOF'
import sys
s = open(sys.argv[1]).read()
old = "        required_limits: device_limits(&adapter),\n"
assert s.count(old) == 2, s.count(old)
s = s.replace(old, old + "        required_features: adapter.features() & wgpu::Features::TIMESTAMP_QUERY,\n")
# XFAULTS=1: the process's minor page faults per frame, split by phase.
def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old)
    s = s.replace(old, new)
sub("""        let frame_started = std::time::Instant::now();
        render_scene(&mut canvas, &tree, scale, bg);""", """        let frame_started = std::time::Instant::now();
        let xf0 = xfaults();
        render_scene(&mut canvas, &tree, scale, bg);
        let xf1 = xfaults();""")
sub("""        encoding += frame_started.elapsed();
        queue.submit(commands);""", """        encoding += frame_started.elapsed();
        let xf2 = xfaults();
        queue.submit(commands);
        let xf3 = xfaults();""")
sub("""        device.poll(wgpu::PollType::wait_indefinitely()).unwrap();
    }
    // What the clips' coverage masks hold after the last frame, and their budget.""", """        device.poll(wgpu::PollType::wait_indefinitely()).unwrap();
        if std::env::var_os("XFAULTS").is_some() {
            let xf4 = xfaults();
            eprintln!(
                "XF frame={frame} scene={} encode={} submit={} wait={} ms={:.2}",
                xf1 - xf0,
                xf2 - xf1,
                xf3 - xf2,
                xf4 - xf3,
                frame_started.elapsed().as_secs_f64() * 1000.0
            );
        }
    }
    // What the clips' coverage masks hold after the last frame, and their budget.""")
s += '''
fn xfaults() -> i64 {
    let mut r = Rusage {
        ru_utime: Timeval { tv_sec: 0, tv_usec: 0 },
        ru_stime: Timeval { tv_sec: 0, tv_usec: 0 },
        ru_maxrss: 0,
        rest: [0; 13],
    };
    unsafe { getrusage(0, &mut r) };
    r.rest[3]
}
'''
open(sys.argv[2], 'w').write(s)
EOF
  find src -name '*.rs' -exec touch {} +
  cfgs=(); has() { grep -rqF -- "$1" src; }
  has 'pub fn clip_path(' && cfgs+=(--cfg harness_clip); has 'TurbulenceKind' && cfgs+=(--cfg harness_turbulence)
  has 'Blend {' && cfgs+=(--cfg harness_blend); has 'fn with_blend(' && cfgs+=(--cfg harness_mix_blend)
  has 'sigma_x' && cfgs+=(--cfg harness_blur_xy); has 'Morphology {' && cfgs+=(--cfg harness_morph)
  has 'Crop {' && cfgs+=(--cfg harness_crop); has 'pub fn clip_paths' && cfgs+=(--cfg harness_clip_paths)
  has 'fn set_submission_slicing' && cfgs+=(--cfg harness_slices)
  echo "$tag cfgs: $cfgs"
  if cargo rustc --release --example _logos_full --features wgpu -- $cfgs ${=EXTRA_CFGS} > $R/build_$tag.log 2>&1; then
    cp $CARGO_TARGET_DIR/release/examples/_logos_full $B/_logos_full_$tag && echo "built $tag from $(git rev-parse --short HEAD) $(date +%T)"
  else
    echo "BUILD $tag FAILED"; grep -A14 '^error' $R/build_$tag.log | head -60
  fi
  rm -f examples/_logos_full.rs
done
echo BUILDS_DONE
