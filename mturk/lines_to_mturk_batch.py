#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Based on http://stackoverflow.com/questions/25362251/python-process-a-csv-file-to-remove-unicode-characters-greater-than-3-bytes

import csv
import re

import unidecode

import argparse
parser = argparse.ArgumentParser(description="Unicode Lines to MTurk CSV Converter")

parser.add_argument("infile",
                    default='data/test.txt',
                    help="input file")
parser.add_argument('-n', dest='ncols', default=10, type=int,
                    help="Number of lines per HIT")
parser.add_argument('--nofilter', dest='prefilter', action='store_false',
                    help="Pre-filter lines to remove obvious porn and very small fragments")

args = parser.parse_args()
if args.prefilter:
    args.outfile = args.infile + ".mturk.filtered.csv"
else:
    args.outfile = args.infile + ".mturk.csv"

quote_replace = re.compile(r'"', re.UNICODE)

def prefilter(line):
    line = line.strip()

    # Remove really short things (likely fragments)
    if len(line) <= 10: return False

    # Remove single words
    if len(line.split()) < 2: return False

    # Remove obvious porn
    ll = line.lower()
    if re.search("(porn)|(xxx)", ll): return False

    return True

def prefilter_iter(lines):
    for line in lines:
        if prefilter(line): yield line


def chunk(seq, n):
    """Chunk a sequence or iterator into equal-sized slices."""
    chunk = []
    for e in seq:
        chunk.append(e)
        if len(chunk) >= n:
            yield chunk
            chunk = []
    yield chunk

with open(args.infile, 'rU') as infile, open(args.outfile, 'w') as outfile:
    if args.prefilter:
        infile = prefilter_iter(infile)

    header = ", ".join("text_%d" % (i+1) for i in range(args.ncols)) + "\n"
    outfile.write(header)
    for row in chunk(infile, args.ncols):
        newline = ", ".join(('"' + quote_replace.sub(r'‟', line.strip("\n")) + '"')
                            for line in row) + "\n"
        outfile.write(newline)
