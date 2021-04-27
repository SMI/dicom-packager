#!/usr/bin/env python3
import datetime
from pathlib import Path


for log in Path("logs").glob("*.log"):
    start = end = None
    with open(log) as f:
        for line in f.read().splitlines():
            if "Removed" in line:
                d = line.split()[0]
                t = line.split()[1]
                start = datetime.datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M:%S")
            elif "Completed" in line:
                d = line.split()[0]
                t = line.split()[1]
                end = datetime.datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M:%S")
    if not start or not end:
        print(log, "Incomplete log")
        continue
    print(log, end - start)
