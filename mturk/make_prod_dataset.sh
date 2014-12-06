#!/bin/bash

HERE=$(dirname $0)
MTURK_DIR=$HERE/../../data/mturk-prod/
OUTFILE=${2:-"$MTURK_DIR/../mturk-prod.json"}

rm $OUTFILE-temp
touch $OUTFILE-temp
for fname in $(ls $MTURK_DIR/*batch_results*)
do
	echo "Processing $fname"
	tempfile=$(basename $fname-temp.json)
	./mturk-proc.py $MTURK_DIR/$fname --outfile $tempfile
	cat $tempfile >> $OUTFILE-temp
	rm $tempfile
done
cat $OUTFILE-temp | jq --slurp 'add' > $OUTFILE
rm $OUTFILE-temp
