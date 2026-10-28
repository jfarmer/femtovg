#!/usr/bin/env bash
# Builds the corpus harness for the browser against femtovg checkouts.
#
#   harness/wasm/build_wasm.sh TAG:SRC ...
#
# For each TAG, crate/ (the harness _logos_full.rs as a wasm32 cdylib, with the page entry in crate/src/web.rs)
# built against the femtovg checkout SRC with every harness cfg that checkout's API supports (as harness/build.sh
# works them out), then wasm-bindgen'd into $WASM_OUT/TAG/ (logos_wasm.js, logos_wasm_bg.wasm), which
# page/index.html loads as ?build=TAG.
#
# Environment (each optional):
#   WASM_BUILD     where the per-TAG crates are made (default: wasm-build/ beside this checkout)
#   WASM_OUT       where the packages go (default: wasm-pkg/ beside this checkout)
#   WASM_BINDGEN   the wasm-bindgen CLI, the version of the checkout's wasm-bindgen crate (0.2.129 at 06243b80)
#   CARGO_TARGET_DIR  cargo's
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
HARN=$(dirname "$HERE")
DA=$(dirname "$HARN")
WASM_BUILD=${WASM_BUILD:-$(dirname "$DA")/wasm-build}
WASM_OUT=${WASM_OUT:-$(dirname "$DA")/wasm-pkg}
WASM_BINDGEN=${WASM_BINDGEN:-wasm-bindgen}
mkdir -p "$WASM_BUILD" "$WASM_OUT"

# As harness/build.sh: the harness cfgs the checkout's API supports, found by what each one calls.
cfgs_for() {
  local src=$1/src flags=()
  has() { grep -rqF -- "$1" "$src"; }
  has 'pub fn clip_path(' && flags+=(--cfg harness_clip)
  has 'TurbulenceKind' && flags+=(--cfg harness_turbulence)
  has 'Blend {' && flags+=(--cfg harness_blend)
  has 'fn with_blend(' && flags+=(--cfg harness_mix_blend)
  has 'sigma_x' && flags+=(--cfg harness_blur_xy)
  has 'Morphology {' && flags+=(--cfg harness_morph)
  has 'Crop {' && flags+=(--cfg harness_crop)
  has 'pub fn clip_paths' && flags+=(--cfg harness_clip_paths)
  has 'fn set_submission_slicing' && flags+=(--cfg harness_slices)
  has 'fn debug_image_count' && flags+=(--cfg harness_image_count)
  has 'pub fn set_thin_fill_masks' && flags+=(--cfg harness_thin_fill_masks)
  echo "${flags[@]}"
}

for spec in "$@"; do
  tag=${spec%%:*}
  src=${spec#*:}
  if [ "$spec" = "$tag" ] || ! grep -qs '^name = "femtovg"' "$src/Cargo.toml"; then
    echo "$tag: pass TAG:SRC with SRC a femtovg checkout" >&2
    exit 1
  fi
  src=$(cd "$src" && pwd)
  rev=$(git -C "$src" rev-parse --short HEAD 2>/dev/null || echo '?')
  dir=$WASM_BUILD/$tag
  mkdir -p "$dir/src"
  sed "s|@FEMTOVG_SRC@|$src|" "$HERE/crate/Cargo.toml.in" > "$dir/Cargo.toml"
  cp "$HERE/crate/build.rs" "$dir/build.rs"
  cp "$HERE/crate/src/"*.rs "$dir/src/"
  # The checkout's lock, so the dependencies are the versions its own builds use.
  [ -f "$dir/Cargo.lock" ] || cp "$src/Cargo.lock" "$dir/Cargo.lock"
  cfgs=$(cfgs_for "$src")
  log=$dir/build.log
  # shellcheck disable=SC2086
  if (cd "$dir" && LOGOS_SRC=$HARN/_logos_full.rs cargo rustc --release --lib --target wasm32-unknown-unknown -- $cfgs) > "$log" 2>&1; then
    wasm=${CARGO_TARGET_DIR:-$dir/target}/wasm32-unknown-unknown/release/logos_wasm.wasm
    rm -rf "${WASM_OUT:?}/$tag"
    "$WASM_BINDGEN" --target web --no-typescript --out-dir "$WASM_OUT/$tag" "$wasm"
    printf '{"tag": "%s", "src": "%s", "rev": "%s", "cfgs": "%s"}\n' "$tag" "$src" "$rev" "$cfgs" > "$WASM_OUT/$tag/build.json"
    echo "built $WASM_OUT/$tag from $src ($rev): $(du -h "$WASM_OUT/$tag/logos_wasm_bg.wasm" | cut -f1) wasm; cfgs: $cfgs"
  else
    echo "$tag FAILED (log: $log)" >&2
    grep -B2 -A12 '^error' "$log" | head -60 >&2
  fi
done
