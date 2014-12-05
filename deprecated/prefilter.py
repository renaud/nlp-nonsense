#!/usr/bin/env python

import sys, os, re

def custom_filter(line):
    # Remove really short things (likely fragments)
    if len(line) <= 10: return False

    # Remove single words
    if len(line.split()) < 2: return False

    # Remove obvious porn
    ll = line.lower()
    if re.search("(porn)|(xxx)", ll): return False

    return True

##
# Really simple line filtering
for line in sys.stdin:
    line = line.strip()
    if custom_filter(line):
        print line