import sys
import logging

log = logging.getLogger("pytrips.helpers")

try:
    from nltk.corpus import wordnet as wn
    from nltk.corpus.reader.wordnet import WordNetError
    from nltk.corpus.reader.wordnet import Synset
except:
    wn = None

def make_spacy_pos_table():
    spacy_pos_labels = {
        "v": ['VBZ', 'TO', 'VBN', 'VBG', 'VBD', 'VB', 'VBP'],
        "n": ['NN', 'NNP', 'NNPS'],
        "a": ['JJS', 'JJ', 'JJR'],
        "r": ['RBS', 'RBR', 'RB']
        }
    res = {}
    for x, y in spacy_pos_labels.items():
        for yy in y:
            res[yy] = x
    return res

spacy_pos_labels = make_spacy_pos_table()


def get_wn_key(k):
    if not wn:
        return None
    if type(k) is Synset:
        return k
    if k.startswith("wn::"):
        k = k[4:]
    while len(k.split(":")) < 5:
        k += ":"
    try:
        return wn.lemma_from_key(k).synset()
    except WordNetError:
        log.info("no synset found for " + k)
        return None
    
class Normalize:
    @staticmethod
    def ont_name(name):
        name = name.lower()
        if name.startswith("ont::"):
            return name
        return "ont::{}".format(name)

    @staticmethod
    def wn_key(name):
        return name

    @staticmethod
    def lemma(name):
        return name.lower()

    @staticmethod
    def spacy_pos(pos):
        return spacy_pos_labels.get(pos, pos.lower()[0])
