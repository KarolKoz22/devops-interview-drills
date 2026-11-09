#!/usr/bin/env bash
set -euo pipefail

LOGFILE="${1:?usage: $0 <logfile> [threshold]}"
THRESHOLD="${2:-3}"
WINDOW_SECONDS=300

last_ts=$(tail -n 1 "$LOGFILE" | awk '{print $1}')
last_epoch=$(date -d "$last_ts" +%s)
window_start=$(( last_epoch - WINDOW_SECONDS ))

count=0
matches=""

while read -r ts level rest; do
    [[ "$level" == "ERROR" || "$level" == "CRITICAL" ]] || continue
    line_epoch=$(date -d "$ts" +%s)
    if (( line_epoch > window_start )); then
        count=$((count + 1))
        matches+="${ts} ${level} ${rest}"$'\n'
    fi
done < "$LOGFILE"

echo "${count} error(s) in the last 5 minutes"

if (( count >= THRESHOLD )); then
    {
        echo "ALERT: ${count} error(s) in the last 5 minutes (threshold: ${THRESHOLD})"
        echo "--- matching lines ---"
        printf '%s' "$matches"
    } >&2
    exit 1
fi

exit 0
