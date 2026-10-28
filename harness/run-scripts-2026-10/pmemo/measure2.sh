#!/bin/zsh
# measure2.sh  - a second pass of the paired timings master (pm_base) vs branch (pm), after waiting for a quieter machine.
R=/Users/matt/src/femtovg-wt/runs/pmemo; D=/Users/matt/src/femtovg-wt/da/harness/clip-bench
cd $R
for i in {1..60}; do
  l=$(sysctl -n vm.loadavg | awk '{print $2}')
  if (( l < 4.5 )); then break; fi
  sleep 5
done
echo "start $(date +%T) load $(sysctl -n vm.loadavg)"; ps -Ao pcpu,comm -r | head -5
python3 paired.py 30 300 pm_base pm $D/cards_none_200.svg
python3 paired.py 20 300 pm_base pm $D/cards_rounded_200.svg
python3 paired.py 30 600 pm_base pm $D/overdraw_none.svg
python3 paired.py 30 300 pm_base pm /Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg
echo "end $(date +%T) load $(sysctl -n vm.loadavg)"; ps -Ao pcpu,comm -r | head -5
