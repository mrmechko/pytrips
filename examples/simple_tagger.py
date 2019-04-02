from pytrips.ontology import load as load_ontology
from pytrips.helpers import Normalize

# turn off all the logging
import logging
logging.basicConfig()
ont = load_ontology()


def tag_word(token):
    pos = Normalize.spacy_pos(token.pos_)
    word = token.text.lower()
    lemma = token.lemma_

    # word lookup:
    wlookup = ont[("q::"+word, pos)]
    llookup = ont[("q::"+lemma, pos)]

    res += wlookup["lex"] 
    res += wlookup["wn"]
    res += llookup["lex"]
    res += llookup["wn"]

    return set(res)

def tag_sentence(sentence):
    return [tag_word(token) for token in nlp(sentence)]
