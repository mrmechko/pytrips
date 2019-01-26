import pytrips

trips = pytrips.ontology.load()

def test_bread():
    assert str(trips["bread"]) == "ont::bread"
