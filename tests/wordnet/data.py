import pytest
from pytrips.helpers import Normalize
from nltk.corpus import wordnet as wn

from .. import trips

synsets = [
    (wn.synset("cat.n.01"), trips["ont::mammal"])
]

keys = [
    ("cat%1:05:00::", trips["ont::mammal"])
]

overkills = [
    "move", "mammal", "person"
]

@pytest.fixture(params=synsets)
def synset_mapping(request):
    return request.param

@pytest.fixture(params=keys)
def key_mapping(request):
    return request.param

@pytest.fixture(params=[trips[t] for t in overkills])
def overkill(request):
    return request.param
