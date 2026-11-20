#!/usr/bin/env bash
# Desktop regression: compare full-page screenshots against a baseline directory.
# usage: tools/regress.sh <baseline_dir> <work_dir> [widths]   (server must be running on :8765)
set -euo pipefail
BASE=$1; WORK=$2; WIDTHS=${3:-1280,1728}
node "$(dirname "$0")/fullshots.js" "$WORK" "$WIDTHS" >/dev/null
fail=0
for f in "$BASE"/*.png; do
  n=$(basename "$f")
  [ -f "$WORK/$n" ] || { echo "MISSING $n"; fail=1; continue; }
  if [ "$(identify -format '%wx%h' "$f")" != "$(identify -format '%wx%h' "$WORK/$n")" ]; then
    echo "SIZE  $n $(identify -format '%wx%h' "$f") -> $(identify -format '%wx%h' "$WORK/$n")"; fail=1; continue
  fi
  # mask the fixed QC typescale switch (bottom-right of the first viewport) in both images
  w=$(identify -format '%w' "$f"); vh=$(( w * 1117 / 1728 ))
  box="rectangle $((w-360)),$((vh-80)) $w,$vh"
  convert "$f" -fill black -draw "$box" "$WORK/.a.png"; convert "$WORK/$n" -fill black -draw "$box" "$WORK/.b.png"
  px=$(compare -metric AE -fuzz 2% "$WORK/.a.png" "$WORK/.b.png" "$WORK/diff-$n" 2>&1 || true)
  total=$(identify -format '%[fx:w*h]' "$f")
  pct=$(python3 -c "print(round(100*float('$px'.split()[0])/$total,4))")
  ok=$(python3 -c "print(1 if $pct<=0.1 else 0)")
  [ "$ok" = 1 ] && rm -f "$WORK/diff-$n" || fail=1
  printf '%s %-34s %8s%%\n' "$([ "$ok" = 1 ] && echo ok || echo DIFF)" "$n" "$pct"
done
exit $fail
