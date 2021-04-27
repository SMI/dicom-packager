#!/usr/bin/env bash

set -uo pipefail

if [ $# -lt 1 ]; then
    echo "Error: Usage $0 file [file...]"
    exit 1
fi

set -ex

mkdir -p md5s

# shellcheck disable=SC2016
echo "$@" | xargs -n1 -P$# sh -c 'md5sum $1 > md5s/$(basename $1).md5' --
