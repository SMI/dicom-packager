#!/bin/bash

set -uo pipefail

if [ $# -ne 1 ]; then
    echo "Error: Usage: $0 file.csv"
    exit 1
fi

set -ex

input="$1"
output="${input/.txt/_filtered.txt}"
year="$(echo "$input" | cut -d'_' -f3 | cut -d'.' -f1)"

echo "$input > $output"

head -1 "$input" > "$output"
grep "^$year" "$input" > "$output"
