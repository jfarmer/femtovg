#!/bin/zsh
# build_fb.sh TAG:CHECKOUT ... - the lib test binary with fill_bench_test.rs appended to src/path/cache.rs (restored
# after), as $HARNESS_BIN/_fb_TAG
export CARGO_PROFILE_RELEASE_DEBUG=0
H=${0:A:h}
BIN=${HARNESS_BIN:-$H/../../../bin}
for spec in "$@"; do
  tag=${spec%%:*}; wt=${spec##*:}
  cd $wt || exit 1
  cp src/path/cache.rs $H/cache_$tag.rs.orig
  cat $H/fill_bench_test.rs >> src/path/cache.rs; find src -name '*.rs' -exec touch {} +
  out=$(cargo test --release --lib --no-run --message-format=json 2>$H/build_fb_$tag.log | python3 -c "
import sys, json
for l in sys.stdin:
    try: m = json.loads(l)
    except Exception: continue
    if m.get('reason') == 'compiler-artifact' and m.get('executable') and m['target']['name'] == 'femtovg': print(m['executable'])")
  cp $H/cache_$tag.rs.orig src/path/cache.rs; rm $H/cache_$tag.rs.orig
  if [ -n "$out" ]; then cp $out $BIN/_fb_$tag && echo "built _fb_$tag"; else echo "BUILD $tag FAILED"; tail -20 $H/build_fb_$tag.log; fi
done
