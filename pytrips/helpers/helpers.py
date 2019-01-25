import sys

try:
    from nltk.corpus import wordnet as wn
    from nltk.corpus.reader.wordnet import WordNetError
except:
    wn = None


def get_wn_key(k):
    if not wn:
        return None
    if k.startswith("wn::"):
        k = k[4:]
    while len(k.split(":")) < 5:
        k += ":"
    try:
        return wn.lemma_from_key(k).synset()
    except WordNetError:
        print("no synset found for " + k, file=sys.stderr)
        return None
