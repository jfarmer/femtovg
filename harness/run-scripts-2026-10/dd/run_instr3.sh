#!/bin/zsh
cd /Users/matt/src/femtovg-wt/runs/dd
W=/Users/matt/src/femtovg-wt
REPEATS=9 python3 tool.py instr.py m8 rvf -- /Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg $W/da/corpus/firefox/puzzle-fox.svg $W/da/harness/clip-bench/cards_none_200.svg $W/da/harness/clip-bench/cards_rounded_200.svg $W/da/harness/clip-bench/cards_circle_200.svg $W/da/mr-settodefault.svg
echo INSTR3_DONE
