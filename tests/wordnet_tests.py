from .wordnet.data import synset_mapping, key_mapping, overkill
from . import trips
from nltk.corpus import wordnet as wn

def test_synset_mapping(synset_mapping):
    assert synset_mapping[1] in trips[synset_mapping[0]]

def test_key_mapping(key_mapping):
    assert key_mapping[1] in trips["wn::"+key_mapping[0]]

def test_overkill_closure(overkill):
    ok = set([s for s in wn.all_synsets() if overkill in trips[s]])
    assert ok == overkill.wordnet_closure()
