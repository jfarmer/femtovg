#!/bin/zsh
# timing_chain.sh BUILD STEP...  - the paired timings for the clip and filter branches, one step after the other on
# a quiet machine. BUILD is the #380 build (harness and gl_fill_bench of that tag); steps: A A2 B C D D2 E E2 F.
# Each step writes its own log under runs/pr/time_*; a pass_time step whose rows file exists resumes.
R=/Users/matt/src/femtovg-wt/runs/pr; C=/Users/matt/src/femtovg-wt/da/harness/corpus_run; B=/Users/matt/src/femtovg-wt/da/harness/clip-bench
cd $R && export CORPUS_RUN_OUT=$R
P=$B/overdraw
build=$1; shift
echo "start $* $(date +%T) load: $(uptime | sed 's/.*averages: //')" >> time_chain.log
for step in "$@"; do
case $step in
A)  # #380 on the bench pages, wgpu: frame time, then encoding time
  python3 tmp/bench.py master_h $build 30 60 ${P}_none.svg ${P}_paths_none.svg ${P}_rect.svg ${P}_rounded.svg ${P}_ellipse.svg ${P}_rect_small.svg ${P}_rounded_small.svg ${P}_paths_rounded_small.svg > time_bench_380.log 2>&1
  python3 tmp/bench.py master_h $build 14 60 $B/cards_none_200.svg $B/cards_rounded_200.svg $B/cards_circle_200.svg >> time_bench_380.log 2>&1
  BENCH_FIELD=encode_ms python3 tmp/bench.py master_h $build 30 60 $B/cards_none_200.svg ${P}_none.svg ${P}_paths_none.svg > time_bench_380_encode.log 2>&1
  BENCH_UNSET=VIEWPORT_CLIP BENCH_FIELD=encode_ms python3 tmp/bench.py master_h $build 30 60 $B/cards_none_200.svg >> time_bench_380_encode.log 2>&1 ;;
A2) # the same scenes on OpenGL
  python3 $B/glpaired.py m $build 12 200 none paths_none rect rounded ellipse rounded_small rect_small paths_rounded_small paths_rounded paths_ellipse cards cards_rounded > time_gl_380.log 2>&1 ;;
B)  # #380 over the corpus: every file at the fit and at 1080p
  python3 $C/pass_time.py master_h $build frames=20 repeats=1 match=. framings=z1,hd out=time_380 > time_380.log 2>&1 ;;
C)  # the crop over the filter files
  python3 $C/pass_time.py cp_h sr frames=20 repeats=1 out=time_crop > time_crop.log 2>&1 ;;
D)  # masks: the files whose frames they change, still and with the scene moving every frame; the bench pages
  python3 $C/pass_time.py cm_stencil cm keys=$R/tmp/cm_changed_keys.json frames=30 repeats=3 out=time_mask_still > time_mask_still.log 2>&1
  python3 $C/pass_time.py cm_stencil cm keys=$R/tmp/cm_changed_keys.json frames=30 repeats=3 env=FRAME_DRIFT=0.37 out=time_mask_drift > time_mask_drift.log 2>&1
  python3 tmp/bench.py cm_stencil cm 14 60 ${P}_star.svg ${P}_paths_star.svg > time_bench_mask.log 2>&1
  python3 $B/glpaired.py m cm 12 200 star star_small paths_star paths_star_small >> time_bench_mask.log 2>&1 ;;
D2) # masks over every file with a clip-path, against their base
  python3 $C/pass_time.py $build cm frames=20 repeats=2 match=clip-path out=time_mask_clipfiles > time_mask_clipfiles.log 2>&1 ;;
E)  # the flattening tolerance, a quarter of the default
  python3 $C/pass_time.py tt_0.25 tt_0.0625 frames=20 repeats=1 match=. framings=z1,hd out=time_tess4 > time_tess4.log 2>&1 ;;
E2) # and a sixteenth
  python3 $C/pass_time.py tt_0.25 tt_0.015625 frames=20 repeats=1 match=. framings=z1,hd out=time_tess16 > time_tess16.log 2>&1 ;;
F)  # clipped groups through a layer
  python3 $C/pass_time.py cgl_off cgl frames=20 repeats=2 match='clip-path' framings=z1,hd out=time_cgl > time_cgl.log 2>&1 ;;
esac
echo "$step done $(date +%T) load: $(uptime | sed 's/.*averages: //')" >> time_chain.log
done
echo "CHAIN_DONE $*" >> time_chain.log
