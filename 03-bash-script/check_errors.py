#!/usr/bin/env python3 

import sys
import re
from datetime import datetime, timedelta


if len(sys.argv)!=2:
    print("You need to pass file_path", file=sys.stderr)
    sys.exit(1)

logfile=sys.argv[1]

try:
    with open(logfile, 'r') as f:
        lines=f.readlines()
except FileNotFoundError:
    print(f"Error: file {logfile} not found", file=sys.stderr)
    sys.exit(1)

timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})')
timestamps = []

for line in lines:
    match=timestamp_pattern.match(line)
    if match:
        try:
            print("chuj")
            ts=datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S")
            print(ts)
            timestamps.append(ts)
        except ValueError:
            continue
if not timestamps:
    print("No timestamps", file=sys.stderr)
    sys.exit(0)

newest=max(timestamps)
cutoff=newest-timedelta(minutes=5)

error_critical_pattern=re.compile(r'\b(error|critical)', re.IGNORECASE)
count=0

for line in lines:
    match=timestamp_pattern.match(line)
    if match:
        try:      
            ts=datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    if ts>=cutoff and error_critical_pattern.search(line):
        count+=1

print(count)
            
