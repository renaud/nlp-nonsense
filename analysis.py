
import sys, os, re, json
from collections import Counter
import itertools
from numpy import *
import pandas as pd

import matplotlib.pyplot as plt
# DEFAULT_COLORCYCLE = ["Blue",
#                       "Red",
#                       "Green",
#                       "Magenta",
#                       "Cyan"]
DEFAULT_COLORCYCLE = ["DeepSkyBlue",
                      "Crimson",
                      "Coral",
                      "MediumOrchid",
                      "LightSkyBlue",
                      "LimeGreen"]

def stacked_histogram(datasets, bin_edges, normed=True):
    """Plot a stacked histogram that shows p(y|x in bucket),
    given a list of datasets corresponding to samples
    from p(x|y)."""

    # Put data into buckets
    histos = [histogram(list(d), bins=bin_edges, normed=False)[0]
              for d in datasets]

    # Compute cumulative bar heights
    hcum = cumsum(array(histos, dtype=float), axis=0)
    totals = hcum[-1]
    if normed:
        hcum = hcum / totals # normalize by total
    return histos, hcum, totals


def plot_stacked_histogram(hcum, bin_edges, ax=None,
                           colors=DEFAULT_COLORCYCLE,
                           labels=itertools.cycle([None])):
    # Plot in reverse order, so smallest is drawn last
    if ax == None: ax = plt.gca()
    for w,c,l in reversed(zip(hcum,
                              itertools.cycle(colors),
                              labels)):
        ax.bar(bin_edges[:-1], w,
               width=(bin_edges[1:]-bin_edges[:-1]),
               color=c, label=l)


def visualize_conditionals(datasets, bin_edges,
                           figsize=None,
                           colors=DEFAULT_COLORCYCLE,
                           labels=itertools.cycle([None])):
    """
    Given samples from distributions p(x|y),
    plot a) distribution p(x in bucket)
    and b) distributions p(y|x in bucket)
    """
    # Compute conditional bars
    histos, hcum, totals = stacked_histogram(datasets, bin_edges)

    # Check for dropped points
    total_y = map(len, datasets)
    print "Class totals: \n" + "\n".join(map(lambda (t,l): "    %d (%s)" % (t,l),
                                             zip(total_y, labels)))
    print "%d points total" % sum(total_y)
    print "(%d points clipped by histogram)" % (sum(total_y) - sum(totals))

    fig, axs = plt.subplots(2,1, squeeze=True,
                            figsize=figsize)

    # Make plot of total counts (p(bucket))
    ax = axs[0]
    ax.bar(bin_edges[:-1], totals, width=(bin_edges[1:]-bin_edges[:-1]),
           label="Totals", color='k', alpha=0.6)
    ax.set_title("count(bucket) : %d points total" % sum(totals))
    ax.set_ylabel("count(bucket)")
    ax.set_xlabel("bucket")
    ax.set_xlim(min(bin_edges),max(bin_edges))
    ax.grid()

    # Make plot of conditionals
    ax = axs[1]
    plot_stacked_histogram(hcum, bin_edges,
                           ax=ax, colors=colors, labels=labels)
    ax.set_title("p(y|bucket)")
    ax.set_ylabel("p(y|bucket)")
    ax.set_xlabel("bucket")
    ax.set_xlim(min(bin_edges),max(bin_edges))
    ax.grid(axis='y')

    return axs