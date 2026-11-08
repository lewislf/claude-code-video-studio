#!/usr/bin/env bash
cd "$(dirname "$0")"
GR=("$@")
taskline set montar-v5 0 ${#GR[@]} --label "clipes v5" --pid $$
for g in "${GR[@]}"; do python3 montar.py "$g"; taskline add montar-v5; done
taskline done montar-v5
