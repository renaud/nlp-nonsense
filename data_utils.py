import sys, os, re, json
from collections import Counter, OrderedDict
import itertools
from numpy import *
import pandas as pd

def parse_labels(ls):
    # Handle badly-serialized labels from java code
    try: return tuple(json.loads(ls))
    except ValueError as e: return (ls,)

def binarize_label(l):
    if l == None: return l
    if "SENTENCE" in l: return "-SENTENCE-"
    else: return "-OTHER-"

from sklearn import preprocessing
class SplitDataset(object):
    master = None   # master Dataset object
    Xy_idx = None   # index into df_*
    X = None        # data vectors
    y = None        # labels
    transformer = None  # preprocessing transformer

    def __init__(self, master, X, y, Xy_idx):
        self.master = master
        self.X = X
        self.y = y
        self.Xy_idx = Xy_idx

    def preprocess(self, transformer=None):
        if transformer != None:
            self.transformer = transformer
            self.X = self.transformer.transform(self.X)
        else: # standard preprocessing
            self.transformer = preprocessing.StandardScaler()
            self.X = self.transformer.fit_transform(self.X)


class Dataset(object):
    """Dataset object to encapsulate training or test set."""

    df_master = None    # Master featureset
    df_pos = None       # POS distributional
    df_pos_norm = None  # POS distributional, normed
    df_ppos = None      # POS positional

    train = None    # SplitDataset
    test = None     # SplitDataset

    int_to_label = None     # map y -> label
    col_to_feature = None   # map j -> f_name

    def __init__(self, filename):
        records = []
        with open(filename) as fd:
            for line in fd:
                records.append(json.loads(line))

        df = pd.DataFrame.from_records(records, index='__ID__')
        # df['text'] = df.word.map(lambda l: " ".join(l))
        # Handle nested JSON
        df['__LABEL__'] = df['__LABEL__'].map(parse_labels)

        # Disambiguate and binarize labels
        df["__LABELS__"] = df["__LABEL__"]
        df["__LABEL__"] = df["__LABEL__"].map(lambda l: l[0] if len(set(l)) == 1 else None)
        df["__LABEL_BIN__"] = df["__LABEL__"].map(binarize_label)

        # Count sentences and unambiguous labels
        nunamb = len(df[df.__LABEL__.notnull()])
        print "%d unambiguous labels" % nunamb
        nsentence = len(df[df.__LABEL_BIN__ == "-SENTENCE-"])
        print "%d sentences (%.02f%%)" % (nsentence, 100*nsentence/(1.0*nunamb))

        # Make basic features
        df = make_basic_features(df)

        self.df_master = df

        print df.shape
        # for c in df.columns:
        #     print c

    def make_pos_features(self):
        # Distributional
        pdf = get_pos_counts(self.df_master)

        # L1-normalized distributional
        pdf_norm = pdf.divide(pdf.sum(axis=0))

        # Positional (begin,end token indicators)
        ppdf = get_pos_positionals(self.df_master)

        self.df_pos = pdf
        self.df_pos_norm = pdf_norm
        self.df_ppos = ppdf

    def to_sklearn(self, level=3, splitat=9000, label_col="__LABEL_BIN__"):
        data = self.df_master
        if level >= 2: # merge in normed POS distributional
            data = data.merge(self.df_pos_norm, how='outer',
                              left_index=True, right_index=True)
        if level >= 3:
            data = data.merge(self.df_ppos, how='outer',
                              left_index=True, right_index=True)

        # Skip nulls
        # label_col = "__LABEL_BIN__"
        data = data[data[label_col].notnull()]
        Xy_idx = data.index

        X, y, int_to_label, col_to_feature = dataframe_to_xy(data,
                                                            r"f_.*",
                                                            label_col=label_col)
        print "X: " + str(X.shape)
        print "y: " + str(int_to_label)
        print "Features: " + ", ".join(col_to_feature.values())

        self.train = SplitDataset(self, X[:splitat], y[:splitat], Xy_idx[:splitat])
        self.test = SplitDataset(self, X[splitat:], y[splitat:], Xy_idx[splitat:])

        self.int_to_label = int_to_label
        self.col_to_feature = col_to_feature


def make_basic_features(df):
    """Compute basic features."""

    df['f_nchars'] = df['__TEXT__'].map(len)
    df['f_nwords'] = df['word'].map(len)

    punct_counter = lambda s: sum(1 for c in s
                                  if (not c.isalnum())
                                      and not c in
                                        [" ", "\t"])
    df['f_npunct'] = df['__TEXT__'].map(punct_counter)
    df['f_rpunct'] = df['f_npunct'] / df['f_nchars']

    df['f_ndigit'] = df['__TEXT__'].map(lambda s: sum(1 for c in s
                                  if c.isdigit()))
    df['f_rdigit'] = df['f_ndigit'] / df['f_nchars']

    upper_counter = lambda s: sum(1 for c in s if c.isupper())
    df['f_nupper'] = df['__TEXT__'].map(upper_counter)
    df['f_rupper'] = df['f_nupper'] / df['f_nchars']

    df['f_nner'] = df['ner'].map(lambda ts: sum(1 for t in ts
                                              if t != 'O'))
    df['f_rner'] = df['f_nner'] / df['f_nwords']

    # Check standard sentence pattern:
    # if starts with capital, ends with .?!
    def check_sentence_pattern(s):
        ss = s.strip(r"""`"'""").strip()
        return s[0].isupper() and (s[-1] in '.?!')
    df['f_sentence_pattern'] = df['__TEXT__'].map(check_sentence_pattern)

    return df

# Get all POS tags
def get_pos_counts(df, firstchar_only=False):
    # Count tags for each sentence
    if firstchar_only == True:
        source = df['pos'].map(lambda s: [t[0] for t in s])
    else:
        source = df['pos']
    counters = source.map(Counter)
    tagnames = sorted(reduce(lambda a,b: a.union(b), source.map(set), set()))
    # Construct DataFrame mapping counters -> rows
    pos_df = pd.DataFrame.from_records(counters,
                                       index=df.index,
                                       columns=tagnames,
                                       coerce_float=True)
    pos_df.fillna(value=0, method=None, inplace=True)
    pos_df.rename(columns={c:"f_pos_"+c for c in pos_df.columns},
                  inplace=True)
    return pos_df

def get_pos_positionals(df):
    """Make indicator features for part-of-speech tokens
    at beginning and end of text."""
    source = df['pos']
    tagnames = sorted(reduce(lambda a,b: a.union(b), source.map(set), set()))
    colnames = (["f_pos_begin_"+c for c in tagnames]
                + ["f_pos_end_"+c for c in tagnames])
    counters = source.map(lambda l: {"f_pos_begin_"+l[0]:1.0,
                                     "f_pos_end"+l[-1]:1.0})
    pos_pos_df = pd.DataFrame.from_records(counters,
                                           index=df.index,
                                           columns=colnames,
                                           coerce_float=True)
    pos_pos_df.fillna(value=0, method=None, inplace=True)
    return pos_pos_df


def dataframe_to_xy(df, features=r"f_.+",
                    label_col="__LABEL__",
                    skipnull=True):
    """Convert dataframe to standard scikits-learn format."""
    if isinstance(features, str):
        # interpret as regex
        featurenames = [c for c in df.columns
                        if re.match(features, c)]
    else:
        featurenames = [c for c in df.columns
                        if c in features]

    if skipnull: # skip missing labels
        df = df[df[label_col].notnull()]

    # Design Matrix X
    df_r = df[featurenames]
    col_to_feature = OrderedDict((i,l) for i,l in enumerate(df_r.columns))
    X = df_r.as_matrix().astype('float64')

    # Label Vector y
    labels = df[label_col].unique()
    if len(labels) == 2 and "-SENTENCE-" in labels:
        # Guarantee sentence is "1" for binary labels
        labels = sorted(labels,
                        key=lambda l: 0 if "SENTENCE" in l else l,
                        reverse=True)
    label_to_int = {l:i for i,l in enumerate(labels)}
    int_to_label = {i:l for i,l in enumerate(labels)}
    y = array(df[label_col].map(lambda s: label_to_int[s]))

    return X, y, int_to_label, col_to_feature