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
