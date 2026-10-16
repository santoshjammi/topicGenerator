#!/usr/bin/env bash
set -euo pipefail

# Preserve seed keywords and only replace generated suggestions.
rm -f output-keywords.txt
python3 getInputs.py
python3 main.py
