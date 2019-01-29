import pytest
import pytrips
from pytrips.helpers import Normalize

def test_nmlz_ont():
    assert Normalize.ont_name("test") == "ont::test"
    assert Normalize.ont_name("ont::test") == "ont::test"

trips = pytrips.ontology.load()

class OntTypeData:
    def __init__(self,
        name, # onttype name
        parent, # parent's name
        children=None, # childrens' names
        words=None, # explicitly mapped words
        wordnet_types=None, # Some wordnet keys that should map to this onttype
        ancestors=None, # some ancestors' names
        offspring=None, # some offspring
        ):

        self.name = name
        self.type = trips[name]
        self.parent = Normalize.ont_name(parent)
        if not children:
            self.children = set()
        else:
            self.children = set([Normalize.ont_name(c) for c in self.children])
        if not words:
            self.words = set()
        else:
            self.words = set([l.lower() for l in words])
        if not wordnet_types:
            self.wordnet_types = set()
        else:
            self.wordnet_types = set(wordnet_types)
        if not ancestors:
            self.ancestors = set()
        else:
            self.ancestors = set([Normalize.ont_name(a) for a in ancestors])
        if not offspring:
            self.offspring = set()
        else:
            self.offspring = set([Normalize.ont_name(o) for o in offspring])
