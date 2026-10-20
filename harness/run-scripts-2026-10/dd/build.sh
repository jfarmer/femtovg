#!/bin/zsh
# build.sh TAG:WORKTREE ... - the demo-assets harness against each worktree with every cfg master supports,
# into bin/_logos_full_TAG; own target dir, sources touched first so a stale library is never linked.
B=/Users/matt/src/femtovg-wt/bin; H=/Users/matt/src/femtovg-wt/da/harness/_logos_full.rs; R=/Users/matt/src/femtovg-wt/runs/dd
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-/Users/matt/src/femtovg-wt/target-dd} CARGO_PROFILE_RELEASE_DEBUG=0
for spec in "$@"; do
  tag=${spec%%:*}; wt=/Users/matt/src/femtovg-wt/${spec##*:}
  cd $wt || exit 1
  cp $H examples/_logos_full.rs; find src -name '*.rs' -exec touch {} +
  if cargo rustc --release --example _logos_full --features wgpu -- --cfg harness_clip --cfg harness_turbulence --cfg harness_blend --cfg harness_mix_blend --cfg harness_blur_xy --cfg harness_morph --cfg harness_clip_paths --cfg harness_crop ${=EXTRA_CFGS} > $R/build_$tag.log 2>&1; then
    cp $CARGO_TARGET_DIR/release/examples/_logos_full $B/_logos_full_$tag && echo "built $tag from $(git rev-parse --short HEAD) $(date +%T)"
  else
    echo "BUILD $tag FAILED"; grep -A12 '^error' $R/build_$tag.log | head -30
  fi
  rm -f examples/_logos_full.rs
done
