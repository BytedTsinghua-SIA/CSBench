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
git cat-file -e e8f457e3de90b75c1340ad4d36b8fe4424753c32:test.sh >/dev/null 2>&1 || finish 0
rm -rf test.sh tests
git checkout e8f457e3de90b75c1340ad4d36b8fe4424753c32 -- test.sh >/dev/null 2>&1 || finish 0
if git cat-file -e e8f457e3de90b75c1340ad4d36b8fe4424753c32:tests >/dev/null 2>&1; then
  git checkout e8f457e3de90b75c1340ad4d36b8fe4424753c32 -- tests >/dev/null 2>&1 || finish 0
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
