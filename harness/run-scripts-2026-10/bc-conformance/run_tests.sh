#!/bin/zsh
# Runs the suite in the scratch worktree bct at each variant, one after the other (same path: artifacts overwrite).
set -u
W=~/src/femtovg-wt/bct
L=~/src/femtovg-wt/runs/bc-conformance
export FEMTOVG_REQUIRE_GPU=metal CARGO_TARGET_DIR=~/src/femtovg-wt/target-prs CARGO_PROFILE_RELEASE_DEBUG=0
waitdisk() { for i in {1..45}; do avail=$(df -k / | tail -1 | awk '{print $4}'); [ $avail -gt 1572864 ] && return; echo "disk low, waiting" >> $L/tests_progress.log; sleep 20; done; }
for v in "$@"; do
  name=${v%%:*}; rev=${v#*:}; mode=${rev#*:}; rev=${rev%%:*}
  cd $W
  if [ "$name" = "A" ]; then rm -f tests/curve_flattening_wgpu.rs; fi
  git checkout -q --detach $rev || { echo "checkout $rev failed" >> $L/tests_progress.log; continue; }
  [ -f tests/curve_flattening_wgpu.rs ] || cp ~/src/femtovg-wt/ff/tests/curve_flattening_wgpu.rs tests/
  touch src/lib.rs src/path/cache.rs src/clip/shape.rs
  waitdisk
  echo "$(date +%T) $name $(git log --oneline -1) mode=$mode" >> $L/tests_progress.log
  if [ "$mode" = "full" ]; then
    cargo test --release --features wgpu --no-fail-fast > $L/tests_$name.log 2>&1
  else
    cargo test --release --features wgpu --test curve_flattening_wgpu --test curve_flattening_report_wgpu -- --nocapture > $L/tests_$name.log 2>&1
  fi
  echo "$(date +%T) $name exit $?" >> $L/tests_progress.log
done
