#!/bin/sh
# Renders all four Ki directions at full size into ../  (blender on PATH)
cd "$(dirname "$0")"
for d in watch honeycomb sense kanji; do blender -b -P ki.py -- "$d" "$PWD/../$d-full.png" "${SIZE:-1024}" "${SAMPLES:-192}" 2>&1 | grep -E "rendered|Error|Traceback"; done
