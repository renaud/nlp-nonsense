import sys, os, re, json
from collections import Counter
import itertools
from numpy import *
import pandas as pd

def load_annotated(filename):
    records = []
    with open("data/test.txt.annotated.tagged.json") as fd:
        for line in fd:
            records.append(json.loads(line))

    df = pd.DataFrame.from_records(records, index='__ID__')
    df['text'] = df.word.map(lambda l: " ".join(l))
    return df

def make_basic_features(df):
    """Compute basic features."""

    df['f_nchars'] = df['text'].map(len)
    df['f_nwords'] = df['word'].map(len)

    punct_counter = lambda s: sum(1 for c in s
                                  if (not c.isalnum())
                                      and not c in
                                        [" ", "\t"])
    df['f_npunct'] = df['text'].map(punct_counter)
    df['f_ndigit'] = df['text'].map(lambda s: sum(1 for c in s
                                  if c.isdigit()))

    df['f_nner'] = df['ner'].map(lambda ts: sum(1 for t in ts
                                              if t != 'O'))

    return df


def dataframe_to_xy(df, features=r"f_.+", ):
    """Convert dataframe to standard scikits-learn format."""
    if isinstance(features, str):
        # interpret as regex
        featurenames = [c for c in df.columns
                        if re.match(features, c)]
    else:
        featurenames = [c for c in df.columns
                        if c in features]

    # Design Matrix X
    df_r = df[featurenames]
    col_to_feature = {i:l for l,i in enumerate(df_r.columns)}
    X = df_r.as_matrix().astype('float64')

    # Label Vector y
    labels = df['__LABEL__'].unique()
    label_to_int = {l:i for i,l in enumerate(labels)}
    int_to_label = {i:l for i,l in enumerate(labels)}
    y = array(df['__LABEL__'].map(lambda s: label_to_int[s]))

    return X, y, int_to_label, col_to_feature