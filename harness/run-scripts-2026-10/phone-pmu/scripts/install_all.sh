#!/bin/zsh
# usage: install_all.sh a12|a14  -- installs the six variant apps
source ${0:A:h}/common.sh
D=$1
for v in m a b c pp pc; do
  xcrun devicectl device install app --device ${UDID[$D]} $APPS/${TGT[$v]}.app 2>&1 | grep -E "installed|ERROR|error" | head -2
done
