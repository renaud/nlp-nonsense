#!/bin/bash

HERE=$(dirname $0)
INFILE=${1:-"$HERE/../data/commoncrawl-1M.txt"}
NLINES=${2:-"10000"}
SPLIT=${3:-"1000"}
OUTDIR=${4:-"$HERE/../data/commoncrawl-$NLINES-s$SPLIT/"}

mkdir -p $OUTDIR

head -n $NLINES $INFILE | split -l $SPLIT -a 2 -d - "$OUTDIR/split-"

