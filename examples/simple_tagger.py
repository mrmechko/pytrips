# turn off all the logging
import logging
logging.basicConfig(level=logging.CRITICAL)

from pytrips.ontology import load as load_ontology
from pytrips.helpers import Normalize
from pytrips.tools import nlp

ont = load_ontology()

word_cache = {}

def lookup_word(query):
    word, lemma, pos = query
    # word lookup:
    wlookup = ont[("q::"+word, pos)]
    llookup = ont[("q::"+lemma, pos)]

    res = wlookup["lex"]
    res += wlookup["wn"]
    res += llookup["lex"]
    res += llookup["wn"]

    return set(res)

def tag_word(token):
    pos = Normalize.spacy_pos(token.pos_)
    word = token.text.lower()
    lemma = token.lemma_

    if pos not in "nvar": # if the pos is not in wordnet
        return set()

    query = (word, lemma, pos)
    return word_cache[(word, lemma, pos)]


def tag_sentence(sentence):
    sentence = nlp(sentence)
    return zip([tag_word(token) for token in sentence], sentence)
