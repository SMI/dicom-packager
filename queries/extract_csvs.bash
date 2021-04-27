#!/bin/bash

mkdir -p results

# NOTE(rkm 2020-10-26) These are used as regexs for MongoDB
for date in \
        2010 \
        2011 \
        2012 \
        2013 \
        # 2014 \
        # 2015 \
        # 2016 \
        # 2017 \
        # '20180[1-8]' \
do
    echo $date
    file_date=$(sed 's/\[//; s/\-/-0/; s/\]//' <<< $date)
    mongo \
        --quiet \
        --eval "const date=$date" \
        extractAllSeriesRange.js \
        > results/all_${file_date}.csv
done

