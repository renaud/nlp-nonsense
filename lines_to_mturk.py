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

args = parser.parse_args()
args.outfile = args.infile + ".mturk.csv"

re_pattern = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)
quote_replace = re.compile(r'"', re.UNICODE)

def limit_to_BMP(value, patt=re_pattern):
    return patt.sub(u'\uFFFD', unicode(value, 'utf8')).encode('utf8')


with open(args.infile, 'rU') as infile, open(args.outfile, 'w') as outfile:
    outfile.write("Text\n")
    for row in infile:
        # newline = unicode(row.strip("\n"), 'utf8')
        # newline = limit_to_BMP(row).strip("\n")
        # import pdb; pdb.set_trace()
        # newline = unidecode.unidecode(newline)
        # newline = quote_replace.sub(r'\"', unicode(newline, 'utf8')).encode('utf8')
        # newline = quote_replace.sub(r'&quot;', row.strip("\n"))
        newline = quote_replace.sub(r'‟', row.strip("\n")) # try to get around sucky unicode support?
        outfile.write('"' + newline + '"\n')