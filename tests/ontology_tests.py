from . import trips
from .ontology.data import TestType
from pytrips.helpers import Normalize

def test_name(TestType):
    assert str(TestType.type) == Normalize.ont_name(TestType.name)

def test_parent(TestType):
    assert str(TestType.type.parent) == Normalize.ont_name(TestType.parent)

def test_children(TestType):
    children = set([str(c) for c in TestType.type.children])
    assert len(TestType.children) == len(children)
    assert TestType.children == children

"""def test_words(TestType):
    words = set(TestType.type.words)
    assert len(TestType.words) == len(words)
    assert TestType.words == words"""

def test_wn_types(TestType):
    this = TestType.type
    for t in TestType.wordnet_types:
        assert this in trips["wn::"+t]

def test_ancestors(TestType):
    ptr = TestType.type.path_to_root()
    for a in TestType.ancestors:
        assert str(trips[a]) == a
        assert trips[a] in ptr

def test_offspring(TestType):
    this = TestType.type
    if not TestType.offspring:
        assert len(this.children) == 0
    for f in TestType.offspring:
        fs = trips[f]
        assert str(fs) == f
        assert this in fs.path_to_root()
