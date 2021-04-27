#!/bin/bash

set -uo pipefail

if [ $# -ne 1 ]; then
    echo "Error: Usage: $0 file.csv"
    exit 1
fi

set -ex

input="$1"
output="${input/proj_name/proj_name_dirs}"
output="${output/csv/txt}"

echo "$input > $output"
cut -d',' "$input" -f2 | sed -n '1!p' > "$output"
