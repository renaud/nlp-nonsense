#!/bin/bash

HERE=`dirname $0`
INFILE=${1:-"data/test.txt.annotated"}

java -cp "$HERE/corenlp/*:$HERE/lib/*:$HERE/build/production/code" \
	edu.stanford.iftenney.JSONAnnotator \
	$INFILE

