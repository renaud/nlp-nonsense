#!/usr/bin/env python

import sys, os, re, json
import collections
from numpy import *
import pandas as pd
import nltk

input_re = re.compile(r"Input\.text_(\d+)")
def find_answer_field(colname):
    m = input_re.match(colname)
    if m == None: return None
    return (colname, "Answer.Q%sAnswer" % m.group(1))


def main(args):
    infile = args.infile

    # Read CSV and map input columns -> answer columns
    df_input = pd.read_csv(infile)
    iomap = dict(filter(lambda s: s, map(find_answer_field, df_input.columns)))

    dfs = []
    for i,o in iomap.items():
        idata = df_input[i]
        odata = df_input[o]
        id = df_input['HITId'] + "-\"" + df_input[i] + "\""
        df_new = pd.DataFrame({"input": idata, "output": odata,
                               "id":id, 'worker_id':df_input['WorkerId']})
        dfs.append(df_new.set_index("id"))

    df = pd.concat(dfs, ignore_index=False)
    print df.shape

    # Print feedback
    print "Feedback:"
    s = df_input['Answer.Feedback']
    for line in s.loc[s.notnull()]:
        print ">> " + line

    # Collect all labels for a given input
    datamap = collections.defaultdict(lambda: [])
    for i,o in zip(df.input, df.output):
        datamap[i].append(o)

    # Compute confusion matrix
    from nltk.metrics import ConfusionMatrix
    x,ys = zip(*datamap.items())
    y0, y1 = zip(*ys) # get first, second element of each
    c = ConfusionMatrix(y0,y1)
    print c
    acc = nltk.metrics.accuracy(y0, y1)
    print "Full cross-annotator accuracy: %.02f%%" % (100*acc)
    print ""

    # Try binarizing: sentence/not
    ys_b = map(lambda ls: [(l if l == '-SENTENCE-' else '-NOT-') for l in ls], ys)
    y0, y1 = zip(*ys_b)
    c_b = ConfusionMatrix(y0,y1)
    print c_b
    acc = nltk.metrics.accuracy(y0, y1)
    print "Binarized cross-annotator accuracy: %.02f%%" % (100*acc)
    print ""

    # Save data to file
    d = df.to_dict('records')
    print "Saving %d records to %s" % (len(d), args.outfile)
    with open(args.outfile, 'w') as fd:
        for r in d:
            print >> fd, json.dumps(r)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="MTurk Output Processor")

    parser.add_argument("infile")
    parser.add_argument('--outfile', dest='outfile', default='test.output.json')

    args = parser.parse_args()

    main(args)