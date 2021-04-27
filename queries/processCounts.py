#!/usr/bin/env python3
# Processes an output csv from the extractAllSeriesRange.js script.
# Expects a csv with columns PatientID,DirectoryPath,Modality,ImagesInSeries

import csv
import glob
from collections import Counter
from pathlib import Path


def print_counts(counts: Counter) -> None:
    print("Modality\t\tImage Count")
    for mod, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"{mod}\t\t\t{count}")
    

def process_csv(csv_path: Path) -> Counter:
    with open(csv_path) as f:
        reader = csv.reader(f)
        next(reader, None) # Skip header
        counts = Counter()
        for row in reader:
            modality, series_count = row[2], row[3]
            counts[modality] += int(series_count)

    print(f"\nCounts for {csv_path.name}")
    print_counts(counts)

    return counts


def main() -> int:

    totals = Counter()
    for f in sorted(glob.glob("results/proj_name_*.csv")):
        totals += Counter(process_csv(Path(f)))
    
    print("\nTotals:")
    print_counts(totals)

    return 0

if __name__ == "__main__":
    exit(main())

