import sys, os, re, json
from collections import Counter, OrderedDict
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


from multiprocessing import Pool
from sklearn.cross_validation import StratifiedKFold
from sklearn import metrics
def _cv_wrapper(argdict):
    # print >> sys.stderr, "cv: fold %d BEGIN" % argdict['__idx__']
    ret = _cv_helper(**argdict)
    # print >> sys.stderr, "cv: fold %d END" % argdict['__idx__']
    # sys.stderr.flush()
    return (argdict['__idx__'],ret)

def _cv_helper(estimator, X, y, train, test, scoring=metrics.f1_score, **kwargs):
    estimator.fit(X[train],y[train])
    ypred = estimator.predict(X[test])
    ytrue = y[test]
    return scoring(ytrue, ypred)

def cross_val_score(estimator, X, y, scoring=metrics.f1_score, cv=5, n_jobs=5):
    """
    Version of sklearn.cross_validation.cross_val_score that allows for more complex
    scoring functions returning arbitrary (serializable) objects.
    Useful for computing multiple evaluation metrics in one run.
    """
    if isinstance(cv, int):
        cv = StratifiedKFold(y, n_folds=cv)
    pool = Pool(n_jobs)
    arglist = [dict(estimator=estimator, X=X, y=y,
                    train=train, test=test,
                    scoring=scoring, __idx__=i)
               for i, (train, test) in enumerate(cv)]
    return pool.map(_cv_wrapper, arglist)

def standard_scorefunc(y, ypred):
    return {'acc': metrics.accuracy_score(y, ypred),
            'pre': metrics.precision_score(y, ypred),
            'rec': metrics.recall_score(y, ypred),
            'f1' : metrics.f1_score(y, ypred)
            }

def standard_crossval(estimator, X, y, **kwargs):
    results = cross_val_score(estimator, X, y, scoring=standard_scorefunc,
                              **kwargs)
    idx, records = zip(*results)
    return pd.DataFrame.from_records(records, index=idx,
                                     columns=['acc','pre','rec','f1'])

def print_cv_results(res):
    mu = res.mean()
    sigma = res.std()
    print "%d-fold cv:" % len(res)
    for c in res.columns:
        print "%4s: %.02f +\- %.02f%%" % (c, 100*mu[c], 100*2*sigma[c]/(len(res)-1.0))

    return pd.DataFrame([mu, sigma], index=['mu','sigma'])


from sklearn import grid_search
class ClassifierExperiment(object):
    """Classifier experiment
    Encapsulates X,y and a classifier,
    and provides for grid search and
    cv evaluation."""

    def __init__(self, clf, X, y):
        self.clf = clf
        self.clfopt = None

        self.X = X
        self.y = y

    def grid_search(self, param_grid, scoring='f1'):
        clfopt = grid_search.GridSearchCV(self.clf, param_grid,
                                          scoring='f1',
                                          cv=5, n_jobs=6)
        clfopt.fit(self.X, self.y)
        self.clfopt = clfopt
        print "Best params: " + str(clfopt.best_params_)
        print "Best score: %.02f%%" % (100*clfopt.best_score_)
        self.clf.set_params(**clfopt.best_params_)

    def eval_cv(self, cv=5, n_jobs=5):
        res = standard_crossval(self.clf, self.X, self.y,
                                cv=5, n_jobs=5)
        stats = print_cv_results(res)
        return res, stats