#!/usr/bin/env bash
set -u

reward_file=/logs/verifier/reward.txt
mkdir -p /logs/verifier
finish() {
  printf '%s\n' "$1" > "$reward_file"
  exit 0
}

cd /testbed || finish 0
git config --global --add safe.directory /testbed || finish 0
rm -f .harbor-environment-placeholder

# The original evaluator applies the agent patch to a fresh image while
# excluding test.sh and tests/. Restore that protected surface before grading.
git cat-file -e 628f4d0588b98922709ab27a16adf71c9913f532:test.sh >/dev/null 2>&1 || finish 0
rm -rf test.sh tests
git checkout 628f4d0588b98922709ab27a16adf71c9913f532 -- test.sh >/dev/null 2>&1 || finish 0
if git cat-file -e 628f4d0588b98922709ab27a16adf71c9913f532:tests >/dev/null 2>&1; then
  git checkout 628f4d0588b98922709ab27a16adf71c9913f532 -- tests >/dev/null 2>&1 || finish 0
fi

if [ -d /tests/test_override ]; then
  cp -a /tests/test_override/. /testbed/ || finish 0
fi

bash test.sh
status=$?
if [ "$status" -eq 0 ]; then
  finish 1
else
  finish 0
fi
