
import sys, os, re, json
import xmltodict

import pdb

class Sentence(object):
    """Simple class for representing
    annotated sentences, stored as parallel token lists."""

    data = {}

    def __init__(self, tokenlist,
                 keys=['word','lemma','POS','NER']):
        if not 'word' in keys: keys.append('word')
        for k in keys:
            self.data[k] = []
        for t in tokenlist:
            for k in keys:
                self.data[k].append(t[k])

    def __repr__(self):
        return self.data.__repr__()

    def to_pretty_string(self):
        s = ""
        prefix_len = 2+max([len(k) for k in self.data.keys()])
        s += (" " * prefix_len) + " ".join(self.data['word']) + "\n"
        for k in self.data.keys():
            if not k == 'word':
                pairs = zip(self.data[k], self.data['word'])
                s += ("%s:" % k).ljust(prefix_len)
                s += " ".join([t.ljust(len(w)) for (t,w) in pairs])
                s += "\n"
        return s

    def get_text(self):
        return " ".join(self.data['word'])


def load_coreNLP_annotations(filename,
                             token_keys=['word','lemma','POS','NER']):
    sentences = []
    def tokens_callback(path, tokens):
        try:
            tokenlist = tokens['tokens']['token']
            if "@id" in tokenlist: # avoid singleton bug
                tokenlist = [tokenlist]
            s = Sentence(tokenlist,
                         keys=token_keys)
            sentences.append(s)
            return True
        except Exception as e:
            print >> sys.stderr, "Error parsing sentence %d" % len(sentences)
            print >> sys.stderr, repr(e)
            pdb.set_trace()
            return False

    with open(filename) as fd:
        # streaming parse of each
        # root/document/sentences/sentence
        xmltodict.parse(fd, item_depth=4,
                        item_callback=tokens_callback)

    return sentences