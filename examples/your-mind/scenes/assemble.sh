#!/usr/bin/env bash
cd "$(dirname "$0")"
GROUP_LIST=("$@")
taskline set assemble-v5 0 ${#GROUP_LIST[@]} --label "v5 clips" --pid $$
for g in "${GROUP_LIST[@]}"; do python3 assemble.py "$g"; taskline add assemble-v5; done
taskline done assemble-v5
