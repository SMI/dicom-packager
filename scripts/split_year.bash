#!/usr/bin/env bash

set -uo pipefail

if [ $# -ne 1 ]; then
    echo "Error: Usage: $0 file.csv"
    exit 1
fi

set -ex

input="$1"
line=$(head -1 "$input")
year=$(echo "${line%%/*}")
basename="$(basename $input)"
basename=$(echo "${basename%.txt}")
echo $basename

for m in $(seq -f"%02g" 12); do
    echo $input $year $m
    grep "^$year/$m" $input > "directory_lists_by_month/${basename}_${m}.txt" || true
done

