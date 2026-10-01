#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# Build the German AOSP/HeliBoard main dictionaries into build/.
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

LOCALES=(de de_DE)
OUT=build

for cmd in python3 hunspell java; do
    command -v "$cmd" >/dev/null || { echo "error: $cmd not found" >&2; exit 1; }
done

mkdir -p "$OUT"

echo "==> Generating wordlists, validated with hunspell"
python3 build_de_dict.py --out "$OUT" --locale "${LOCALES[@]}"

for locale in "${LOCALES[@]}"; do
    echo "==> Compiling $OUT/main_$locale.dict"
    ./dicttool_aosp makedict -s "$OUT/main_$locale.combined" -d "$OUT/main_$locale.dict" -2 >/dev/null
done

echo "==> Done:"
ls -l "$OUT"/*.dict
