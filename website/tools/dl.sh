#!/usr/bin/env bash
# usage: dl.sh name=url ...   -> downloads into assets/_raw/<name>.<ext-from-url>
set -e
cd "$(dirname "$0")/.."
mkdir -p assets/_raw
for pair in "$@"; do
  name="${pair%%=*}"; url="${pair#*=}"; ext="${url##*.}"
  out="assets/_raw/$name.$ext"
  [ -s "$out" ] && continue
  curl -sSfL --retry 3 -o "$out" "$url" && echo "ok $out $(stat -c%s "$out")"
done
