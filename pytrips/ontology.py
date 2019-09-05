import logging
logger = logging.getLogger("pytrips")

import jsontrips
from collections import defaultdict as ddict
import json
import sys

from .structures import TripsRestriction, TripsType
from .helpers import wn, get_wn_key, all_hypernyms
from nltk.corpus.reader.wordnet import Synset
import string as _string
from graphviz import Digraph

class NodeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = set()

    def get_nth_label(self, n):
        if n < 26:
            return _string.ascii_uppercase[n]
        return self.get_nth_label(n // 26) + self.get_nth_label(n % 26)

    def escape_label(self, s):
        if type(s) is str:
            return s
        if type(s) is Synset:
            return s.lemmas()[0].key().replace("%", ".")
        if type(s) is TripsType:
            return s.name
        return str(s)

    def node(self, name):
        name = self.escape_label(name)
        if name in self.nodes:
            return
        label = self.get_nth_label(len(self.nodes))
        self.nodes[name] = label

    def edge(self, source, target, label=""):
        self.edges.add((self.escape_label(source), 
                    self.escape_label(target), 
                    self.escape_label(label)))

    def source(self):
        graph = Digraph()
        for l, t in self.nodes.items():
            graph.node(l, t)
        for s, t, l in self.edges:
            s, t = self.nodes[s], self.nodes[t]
            if l:
                graph.edge(s, t, l)
            else:
                graph.edge(s, t)
        return graph.source

def _is_query_pair(x):
    if type(x) is tuple and len(x) == 2:
        return (type(x[0]) in set([str, TripsType])) and (type(x[1] == str))
    return False


class Trips(object):
    def __init__(self, ontology, lexicon):
        ontology = ontology.values() # used to be a list, now is a dict
        self.max_wn_depth = 5 # override this for more generous or controlled lookups
        self._data = {}
        self._data['root'] = TripsType("root", None, [], [], [], [], [], self)
        revwords = ddict(set)
        self._words = ddict(lambda: ddict(set))
        self._wordnet_index = ddict(list)
        self.__definitions = ddict(list)
        for word, entry_list in lexicon["words"].items():
            for entry in entry_list:
                name = entry["name"].lower()
                #cat = entry["cat"].lower()
                entries = lexicon["entries"][entry["entry"]]
                pos = entries['pos'].lower()
                # TODO: incorporate the lexicon
                if len(entries['senses']) > 1:
                    logger.info(entries["name"] + " has " + str(len(entries["senses"])) + " senses")
                for values in entries["senses"]:
                    if "lf_parent" not in values.keys():
                        c = "no_parent"
                    else:
                        c = values["lf_parent"].lower()
                    self._words[pos][word.lower()].add(c)
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
                    s.get('definitions', []),
                    self
                )
            self._data[t.name] = t
            for k in s.get('wordnet_sense_keys', []):
                k = get_wn_key(k)
                if k:
                    self._wordnet_index[k].append(t)

            if t.definitions:
                self.__definitions[json.dumps(t.definitions)].append(t.name)

    def get_trips_type(self, name):
        """Get the trips type associated with the name"""
        name = name.split("ont::")[-1].lower()
        return self._data.get(name, None)

    def get_word(self, word, pos=None):
        """Lookup all possible types for a word."""
        word = word.split("w::")[-1].lower()
        if pos:
            index = self._words[pos][word]
        else:
            index = set()
            for pos, words in self._words.items():
                index.update(words[word])
        return [self[x] for x in index if self[x]]

    def get_part_of_speech(self, pos, lex):
        """Lookup all possible types or lexical items for the given part of speech"""
        pos = pos.split("p::")[-1]
        words = self._words[pos].keys()
        if lex:
            return words
        res = []
        for x in words:
            res += self.get_word(x, pos=pos)
        return list(set(res))

    def get_word_graph(self, word, pos=None):
        graph = NodeGraph()
        senses = wn.synsets(word, pos=pos)
        if pos:
            word = word + "." + pos
        graph.node(word)
        for s in senses:
            n, graph = self.get_wordnet(s, graph=graph, parent=word)
        return graph

    def get_wordnet(self, key, max_depth=-1, graph=None, parent=None):
        """Get types provided by wordnet mappings"""
        def _return(val):
            if graph:
                return (val, graph)
            return val

        if graph == True:
            graph = NodeGraph()

        if max_depth == -1:
            max_depth = self.max_wn_depth
        elif max_depth == 0:
            return _return([])

        if type(key) is str:
            key = get_wn_key(key)
        if not key:
            return _return([])

        if graph:
            graph.node(key)
            if parent:
                graph.edge(parent, key)
        res = []
        if key in self._wordnet_index:
            res = self._wordnet_index[key][:]
            if graph:
                for r in res:
                    graph.node(r)
                    graph.edge(key, r)
        else:
            res = set()
            for k in all_hypernyms(key):
                n = self.get_wordnet(k, max_depth=max_depth-1, graph=graph, parent=key)
                if graph:
                    n, graph = n
                res.update(n)
        return _return(res)

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

    def get_definition(self, name):
        """Get types that contain the given name in their definitions
        """
        name = name.split("d::")[-1].split("ont::")[-1].upper() #definitions are in uppercase, names are in lower case.
        return list(set(["ont::"+df for lst in self.__definitions.keys() for df in self.__definitions[lst] if ""+name+"" in lst]))

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
        elif key.startswith("d::") and self.get_trips_type(key.split("d::")[-1]):
            return self.get_definition(key)
        else:
            return self.get_trips_type(key)

    def __iter__(self):
        """return an iterator with all the types."""
        # TODO: guarantee order
        return self._data.values()


def load(log=False):
    if not log:
        logging.disable(logging.CRITICAL)
    logger.info("Loading ontology")

    ont = jsontrips.ontology()

    logger.info("Loaded ontology")
    logger.info("Loading lexicon")
    
    lex = jsontrips.lexicon()

    logger.info("Loaded lexicon")
    return Trips(ont, lex)

__ontology__ = None

def get_ontology(log=False):
    global __ontology__
    if not __ontology__:
        __ontology__ = load(log=log)
    return __ontology__
