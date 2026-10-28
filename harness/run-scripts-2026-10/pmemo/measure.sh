#!/bin/zsh
# measure.sh  - waits for a quieter machine (1-minute load under 5, at most 5 minutes), then: a 12 s sample of master on
# the cards page, the paired timings master (pm_base) vs branch (pm), and instructions retired per frame.
R=/Users/matt/src/femtovg-wt/runs/pmemo; D=/Users/matt/src/femtovg-wt/da/harness/clip-bench; B=/Users/matt/src/femtovg-wt/bin
cd $R
for i in {1..60}; do
  l=$(sysctl -n vm.loadavg | awk '{print $2}')
  if (( l < 5.0 )); then break; fi
  sleep 5
done
echo "start $(date +%T) load $(sysctl -n vm.loadavg)"; ps -Ao pcpu,comm -r | head -5
(env FRAME_W=1920 FRAME_H=1080 BOX=1080 BOX_X=420 BOX_Y=0 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 LAYER_STATS=1 MEM_PEAKS=1 TRANSIENT_BUDGET_MB=1024 FRAMES=8000 $B/_logos_full_pm_base 1 $R/prof.ppm $D/cards_none_200.svg > $R/prof_base2.stderr 2>&1 &)
sleep 3
/usr/bin/sample $(pgrep -f "_logos_full_pm_base" | head -1) 12 1 -file $R/sample_base2.txt > /dev/null 2>&1
while pgrep -f "_logos_full_pm_base" > /dev/null; do sleep 1; done
echo "profile run: $(grep -o 'frame_ms.*' $R/prof_base2.stderr)"; python3 $R/sample_share.py $R/sample_base2.txt
echo "--- paired timings $(date +%T) load $(sysctl -n vm.loadavg)"
python3 paired.py 30 300 pm_base pm $D/cards_none_200.svg
python3 paired.py 20 300 pm_base pm $D/cards_rounded_200.svg
python3 paired.py 30 600 pm_base pm $D/overdraw_none.svg
python3 paired.py 30 300 pm_base pm /Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg
echo "--- instructions $(date +%T) load $(sysctl -n vm.loadavg)"
LO=100 HI=600 REPEATS=5 python3 instr.py pm_base pm -- $D/cards_none_200.svg $D/cards_rounded_200.svg $D/overdraw_none.svg /Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg
echo "end $(date +%T) load $(sysctl -n vm.loadavg)"; ps -Ao pcpu,comm -r | head -5
rm -f $R/prof.ppm $R/instr.ppm
