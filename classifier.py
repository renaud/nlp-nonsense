import sys, os, re, json
from collections import Counter
import itertools
from numpy import *
import pandas as pd

import nltk

def evaluate_multiclass(y, ypred, int_to_label=None):
    """Pretty-print the confusion matrix
    for a multiclass problem."""
    if isinstance(int_to_label, dict):
        ypred = [int_to_label[s] for s in ypred]
        y = [int_to_label[s] for s in y]

    cm = nltk.metrics.confusionmatrix.ConfusionMatrix(y, ypred)
    acc = nltk.metrics.accuracy(y, ypred)

    print cm.pp()
    print "Accuracy: %.02f%%" % (100*acc)
    return cm

