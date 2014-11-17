import sys, os, re, json
from collections import Counter
import itertools
from numpy import *
import pandas as pd

import nltk
import sklearn.metrics
from sklearn import cross_validation

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


def evaluate_retrieval(y, ypred, posclass='-SENTENCE-'):
    ref = [(l == posclass) for l in y]
    pred = [(l == posclass) for l in ypred]

    print "Precision: %.02f%%" % (100*sklearn.metrics.precision_score(ref, pred))
    print "Recall:    %.02f%%" % (100*sklearn.metrics.recall_score(ref, pred))
    print "F1:        %.02f%%" % (100*sklearn.metrics.f1_score(ref, pred))
