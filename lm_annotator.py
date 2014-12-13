#!/usr/bin/env python

import sys, os, re, json

import kenlm


import argparse
parser = argparse.ArgumentParser(description="Language Model Pass-Through Annotator")

parser.add_argument("lmfile",
                    help="Path to language model file, e.g. nyt.arpa")

args = parser.parse_args()

# Load language model
f_name = "f_lmscore_"+os.path.splitext(os.path.basename(args.lmfile))[0]
model = kenlm.LanguageModel(args.lmfile)

for line in sys.stdin:
    data = json.loads(line)
    score = model.score(data['__TEXT__'])
    data[f_name] = score
    print json.dumps(data)