import logging
logger = logging.getLogger("pytrips")

import jsontrips
from collections import defaultdict as ddict
import sys

from .structures import TripsRestriction, TripsType
from .helpers import wn, get_wn_key
from nltk.corpus.reader.wordnet import Synset


def _is_query_pair(x):
    if type(x) is tuple and len(x) == 2:
        return (type(x[0]) in set([str, TripsType])) and (type(x[1] == str))
    return False


class Trips(object):
    def __init__(self, ontology, lexicon):
        ontology = ontology.values() # used to be a list, now is a dict
        self.max_wn_depth = 5 # override this for more generous or controlled lookups
        self.__data = {}
        self.__data['root'] = TripsType("root", None, [], [], [], [], self)
        revwords = ddict(set)
        self.__words = ddict(lambda: ddict(set))
        self.__wordnet_index = ddict(list)
        for word, entry_list in lexicon["words"].items():
            for entry in entry_list:
                name = entry["name"].lower()
                #cat = entry["cat"].lower()
                entries = lexicon["entries"][entry["entry"]]
                pos = entries['pos'].lower()
                # TODO: incorporate the lexicon
                for values in entries["senses"]:
                    if "lf_parent" not in values.keys():
                        c = "no_parent"
                    else:
                        c = values["lf_parent"].lower()
                    self.__words[pos][word.lower()].add(c)
                    revwords[c].add((word+"."+pos).lower())

        for s in ontology:
            arguments = [TripsRestriction(x["role"],
                                          x["restriction"],
                                          str(x["optionality"]), self)
                         for x in s.get('arguments', [])]
            t = TripsType(
                    s['name'],
                    s.get('parent', "ROOT"),
                    s.get('children', []),
                    list(revwords[s['name'].lower()]),
                    s.get('wordnet_sense_keys', []),
                    arguments,
                    self
                )
            self.__data[t.name] = t
            for k in s.get('wordnet_sense_keys', []):
                k = get_wn_key(k)
                if k:
                    self.__wordnet_index[k].append(t)

    def get_trips_type(self, name):
        """Get the trips type associated with the name"""
        name = name.split("ont::")[-1].lower()
        return self.__data.get(name, None)

    def get_word(self, word, pos=None):
        """Lookup all possible types for a word."""
        word = word.split("w::")[-1].lower()
        if pos:
            index = self.__words[pos][word]
        else:
            index = set()
            for pos, words in self.__words.items():
                index.update(words[word])
        return [self[x] for x in index if self[x]]

    def get_part_of_speech(self, pos, lex):
        """Lookup all possible types or lexical items for the given part of speech"""
        pos = pos.split("p::")[-1]
        words = self.__words[pos].keys()
        if lex:
            return words
        res = []
        for x in words:
            res += self.get_word(x, pos=pos)
        return list(set(res))

    def get_wordnet(self, key, max_depth=-1):
        """Get types provided by wordnet mappings"""
        if max_depth == -1:
            max_depth = self.max_wn_depth
        elif max_depth == 0:
            return []
        if type(key) is str:
            key = get_wn_key(key)
        if not key:
            return []
        if key in self.__wordnet_index:
            return self.__wordnet_index[key][:]
        else:
            res = set()
            for k in key.hypernyms():
                res.update(self.get_wordnet(k, max_depth=max_depth-1))
            return list(res)

    def lookup(self, word, pos): #TODO what kind of information does this need in general?
        word = word.split("q::")[-1]
        #1 get word lookup
        w_look = self.get_word(word, pos=pos)
        #2 get wordnet
        wnlook = set()
        if wn:
            keys = wn.synsets(word, pos=pos)
            for k in keys:
                wnlook.update(self.get_wordnet(k))
        return {"lex" : w_look, "wn": list(wnlook)}


    def __getitem__(self, key):
        """if the input is "w::x" lookup x as a word
        if the input is "ont::x" lookup x as a type
        if the input is "wn::x" lookup x as a wordnet sense
        else lookup as an ont type.
        """
        pos = None
        if _is_query_pair(key):
            key, pos = key
        if type(key) is TripsType:
            return key
        if type(key) is Synset:
            return self.get_wordnet(key)
        elif type(key) is not str:
            return None
        if key is None:
            return None
        key = key.lower()
        if key.startswith("w::"):
            return self.get_word(key, pos=pos)
        elif key.startswith("wn::"):
            return self.get_wordnet(key)
        elif key.startswith("q::"):
            return self.lookup(key, pos=pos)
        elif key.startswith("p::"):
            return self.get_part_of_speech(key, lex=pos)
        else:
            return self.get_trips_type(key)

    def __iter__(self):
        """return an iterator with all the types."""
        # TODO: guarantee order
        return self.__data.values()


def load():
    logger.info("Loading ontology")

    ont = jsontrips.ontology()

    logger.info("Loaded ontology")
    logger.info("Loading lexicon")
    
    lex = jsontrips.lexicon()

    logger.info("Loaded lexicon")
    return Trips(ont, lex)
