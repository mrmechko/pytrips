# turn off all the logging
import logging
logging.basicConfig(level=logging.CRITICAL)

from pytrips.ontology import load as load_ontology
from pytrips.helpers import Normalize
from pytrips.tools import nlp

ont = load_ontology()

def tag_word(token):
    pos = Normalize.spacy_pos(token.pos_)
    word = token.text.lower()
    lemma = token.lemma_

    if pos not in "nvar": # if the pos is not in wordnet
        return set()

    # word lookup:
    wlookup = ont[("q::"+word, pos)]
    llookup = ont[("q::"+lemma, pos)]

    res = wlookup["lex"] 
    res += wlookup["wn"]
    res += llookup["lex"]
    res += llookup["wn"]

    return set(res)

def tag_sentence(sentence):
    sentence = nlp(sentence)
    return zip([tag_word(token) for token in sentence], sentence)
