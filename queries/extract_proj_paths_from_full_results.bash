#!/bin/bash

set -uo pipefail

if [ $# -ne 1 ]; then
    echo "Error: Usage: $0 file.csv"
    exit 1
fi

# TODO(rkm 2021-04-27) Parameterise this
id_list="list.txt"

if [ ! -f "$id_list" ]; then
    echo "Erorr: ID list not found"
    exit 1
fi

set -ex

input="$1"
output="${input/all/proj_name}"

echo $input ">" $output

head -n1 $input > $output

grep \
    --file "$id_list" \
    --fixed-strings \
    $input >> $output

