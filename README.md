# PyTrips [![PyPI version](https://badge.fury.io/py/pytrips.svg)](https://badge.fury.io/py/pytrips)

[![Build Status](https://travis-ci.com/mrmechko/pytrips.svg?branch=master)](https://travis-ci.com/mrmechko/pytrips)

PyTrips provides a python interface to interacting with the TRIPS ontology and parser.


# Installation

```
pip install pytrips
pip install pytrips[tools] # optional
python -c "import nltk; nltk.download('wordnet')"
```

# Basic Usage

Load the ontology and retrieve a type by name:

```
from pytrips.ontology import load
ont = load()

catch = ont["catch"] # lookup an ontology type
```

And then inspect said type:

```
print(catch)
print(catch.parent)
print(catch.children)
print(catch.arguments)
```

which should result in:

```
# ont::catch
# ont::co-motion
# []
# [<TripsRestriction :neutral >, <TripsRestriction :source >, <TripsRestriction :result >, <TripsRestriction :extent >, <TripsRestriction :affected >, <TripsRestriction :agent >]
```

Check if types subsume each other:
```
catch < ont["event-of-action"]

# Make sure at least one type is explicitly a TripsType.  The other can be a string.
"food" > ont["bread"]
```

Or get the lowest common subsumer of two types:
```
ont["bread"] ^ ont["geo-object"]
```

For simplicity, lookup words and ontology types in the same way:
```
ont["person"] # default is to look up an ontology type
ont["ont::person"] # explicitly get the ontology type named "ont::person"
ont["w::person"] # or lookup the list of ontology types that the word "person" can map to
```

WordNet lookups are similar:
```
ont["wn::cat%1:06:00::"]
>> [ont::device]

ont["q::cat"] # returns all lexical and wordnet mappings for the word cat in a dictionary
>> {'lex': [ont::nonhuman-animal, ont::medical-diagnostic],
 'wn': [ont::pharmacologic-substance,
  ont::female-person,
  ont::communication-party,
  ont::male-person,
  ont::medication,
  ont::mammal,
  ont::device,
  ont::land-vehicle,
  ont::vomit]}
```

Or we can specify a part of speech to limit the search:
```
ont[("q::move", 'v')]
>> {'lex': [ont::cause-move, ont::move, ont::provoke, ont::activity-ongoing],
 'wn': [ont::cause-effect,
  ont::change,
  ont::believe,
  ont::activity-event,
  ont::commerce-sell,
  ont::move,
  ont::progress,
  ont::live,
  ont::suggest]}
```
