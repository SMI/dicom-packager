#!/bin/bash

set -uo pipefail

if [ $# -ne 1 ]; then
    echo "Error: Usage: $0 file.csv"
    exit 1
fi

set -ex

input="$1"
output="${input/.txt/_uniq.txt}"

echo "$input > $output"

sort -u "$input" > "$output"
