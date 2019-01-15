import pytrips

trips = pytrips.ontology.load()

assert str(trips["bread"]) == "ont::bread"
