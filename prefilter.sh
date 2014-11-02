#!/bin/bash

INFILE=$1
OUTFILE="$INFILE.filtered"
HERE=`dirname $0`

cat $INFILE | $HERE/prefilter.py > $OUTFILE
echo "Input: `wc -l $INFILE`"
echo "Output: `wc -l $OUTFILE`"
