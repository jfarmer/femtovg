#!/bin/zsh
cd /Users/matt/src/femtovg-wt/runs/dd10
for f in keys/id_*.json; do fr=${${f:t:r}#id_}; python3 tool.py refs_ideal.py keys=$f framings=$fr; done
for f in keys/chr_*.json; do fr=${${f:t:r}#chr_}; python3 tool.py refs.py chromium keys=$f framings=$fr; done
for f in keys/ff_*.json; do fr=${${f:t:r}#ff_}; python3 tool.py refs.py firefox keys=$f framings=$fr; done
echo REFS_DONE
