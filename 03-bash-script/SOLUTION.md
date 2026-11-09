# Solution — Task 3

Reference implementations are in `solution_check_errors.sh` and
`solution_check_errors.py` (prefixed `solution_` so they don't collide
with the `check_errors.sh`/`.py` you write). Both verified against
`sample.log`: default threshold → `4 error(s)`, exit `1`; threshold `100`
→ exit `0`.

## The trap in this exercise

`sample.log` has 8 `ERROR`/`CRITICAL` lines total, but only **4** fall
inside the last 5 minutes relative to the log's own last timestamp — the
other 4 are older. A naive `grep -c ERROR sample.log` gives 8 and is
wrong. The point of the exercise is the time-windowing, not the grep —
if your first instinct was to just count matching lines file-wide,
that's the exact gap a monitoring-script task is testing for.

## Key design points (either language)

- **Anchor to the log's last timestamp, not wall-clock `now`.** In
  production you'd use real `now`, but a static sample file only makes
  sense anchored to its own last entry — and the same code works either
  way if you just make "now" a variable.
- **Treat `CRITICAL` as error-level too** — the spec says "ERROR or
  above"; hardcoding only `ERROR` misses it.
- **Exit codes carry the signal.** `0` = OK, non-zero = alert — this is
  the calling convention for cron, Nagios/Icinga2 plugins, and CI checks
  alike. Printing a message but always exiting 0 makes the script
  useless for automation, even if a human reading the output would
  understand it.
- **Alert detail goes to stderr**, the summary line to stdout — lets a
  monitoring system show just the one-liner by default while `2>&1`
  still gets you the full context when debugging.

## Bash (`solution_check_errors.sh`)

```bash
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
```

Note: this shells out to `date -d` once per line, which is fine for a
small log but wouldn't scale to a huge file — if asked to optimize,
mention doing the whole thing in a single `awk` pass with `mktime()`
instead of forking `date` repeatedly.

## Python (`solution_check_errors.py`)

```python
#!/usr/bin/env python3
import sys
from datetime import datetime, timedelta

def main():
    if len(sys.argv) < 2:
        sys.exit(f"usage: {sys.argv[0]} <logfile> [threshold]")

    logfile = sys.argv[1]
    threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    window = timedelta(minutes=5)

    with open(logfile) as f:
        lines = [line.rstrip("\n") for line in f if line.strip()]

    parsed = []
    for line in lines:
        ts_str, level, *rest = line.split(maxsplit=2)
        parsed.append((datetime.fromisoformat(ts_str), level, " ".join(rest)))

    last_ts = parsed[-1][0]
    window_start = last_ts - window

    matches = [
        (ts, level, msg) for ts, level, msg in parsed
        if level in ("ERROR", "CRITICAL") and ts > window_start
    ]

    print(f"{len(matches)} error(s) in the last 5 minutes")

    if len(matches) >= threshold:
        print(f"ALERT: {len(matches)} error(s) in the last 5 minutes (threshold: {threshold})", file=sys.stderr)
        print("--- matching lines ---", file=sys.stderr)
        for ts, level, msg in matches:
            print(f"{ts.isoformat()} {level} {msg}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
```
