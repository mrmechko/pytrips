import jsontrips
from collections import defaultdict as ddict
import sys

try:
    from nltk.corpus import wordnet as wn
    from nltk.corpus.reader.wordnet import WordNetError
except:
    wn = None


def _is_query_pair(x):
    if type(x) is tuple and len(x) == 2:
        return (type(x[0]) in set([str, TripsType])) and (type(x[1] == str))
    return False

def get_wn_key(k):
    if not wn:
        return None
    if k.startswith("wn::"):
        k = k[4:]
    while len(k.split(":")) < 5:
        k += ":"
    try:
        return wn.lemma_from_key(k).synset()
    except WordNetError:
        print("no synset found for " + k, file=sys.stderr)
        return None


class Trips(object):
    def __init__(self, ontology, lexicon):
        ontology = ontology.values() # used to be a list, now is a dict
        self.__data = {}
        self.__data['root'] = TripsType("root", None, [], [], [], [], self)
        revwords = ddict(set)
        self.__words = ddict(lambda: ddict(set))
        self.__wordnet_index = ddict(list)
        for word, entry in lexicon.items():
            for pos, values in entry.items():
                self.__words[pos.lower()][word.lower()].update([v["sense"].lower() for v in values])
                for val in [v["sense"].lower() for v in values]:
                    revwords[val].add((word+"."+pos).lower())

        for s in ontology:
            arguments = [TripsRestriction(x["role"], x["restriction"], str(x["optionality"]), self) for x in s.get('arguments', [])]
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
        return [self[x] for x in index]

    def get_wordnet(self, key):
        """Get types provided by wordnet mappings"""
        if type(key) is str:
            key = get_wn_key(key)
        if not key:
            return []
        if key in self.__wordnet_index:
            return self.__wordnet_index[key][:]
        else:
            res = set()
            for k in key.hypernyms():
                res.update(self.get_wordnet(k))
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
        else:
            return self.get_trips_type(key)

    def __iter__(self):
        """return an iterator with all the types."""
        # TODO: guarantee order
        return self.__data.values()


class TripsType(object):
    """
    Note: in order for the operations to work, at least one of the
    types must explicitly be a TripsType
    type: t, str: s
    equality: t1 == t2, t1 == s
    subsumption: t1 < t2, s1 < t2, t1 < s2
    lcs: t1 ^ t2, s1 ^ t2, t1 ^ s2
    """

    def __init__(self, name, parent, children, words, wordnet, arguments, ont):
        self.__name = name.lower()
        if parent:
            self.__parent = parent.lower()
        else:
            self.__parent = None
        self.__children = children
        self.__arguments = arguments
        self.__words = [w.lower() for w in words]
        self.__wordnet = [w.lower() for w in wordnet]
        self.__wordnet_keys = [get_wn_key(s) for s in self.__wordnet if get_wn_key(s)]
        self.__ont = ont
        # TODO: set numerical id

    @property
    def depth(self):
        if self == "ont::root":
            return 0
        return self.parent.depth + 1

    @property
    def name(self):
        return self.__name

    @property
    def parent(self):
        return self.__ont[self.__parent]

    @property
    def children(self):
        return [self.__ont[c] for c in self.__children]

    @property
    def arguments(self):
        return self.__arguments[:]

    @property
    def words(self):
        return self.__words[:]

    @property
    def wordnet(self):
        return self.__wordnet[:]

    @property
    def wordnet_keys(self):
        return self.__wordnet_keys[:]

    def __eq__(self, other):
        # XXX: does this cause problems with putting things in sets?
        if type(other) is TripsType:
            return self.name == other.name
        elif type(other) is str:
            return str(self) == other
        else:
            raise NotImplemented

    def __lt__(self, other):
        if type(other) is str:
            other = self.__ont[other]
            if type(other) is not TripsType:
                raise NotImplemented
        return other.subsumes(self)

    def __gt__(self, other):
        if type(other) is str:
            other = self.__ont[other]
            if type(other) is not TripsType:
                raise NotImplemented
        return self.subsumes(other)

    def __str__(self):
        return "ont::" + self.name

    def __hash__(self):
        return hash("<TripsType %s>".format(repr(self)))

    def __repr__(self):
        return str(self)

    def path_to_root(self):
        if self == "ont::root":
            return [self]
        else:
            return [self] + self.parent.path_to_root()

    def lcs(self, other):
        if type(other) is str:
            other = self.__ont[other]
        if type(other) is not TripsType:
            raise NotImplemented
        t = reversed(self.path_to_root())
        s = reversed(other.path_to_root())
        lcs = self.__ont["root"]
        pair = zip(t,s)
        for p, q in pair:
            if p == q:
                lcs = p
        return lcs

    def __xor__(self, other):
        return self.lcs(other)

    def subsumes(self, other):

        if other == "ont::root":
            return False
        elif other in self.children:
            return True
        else:
            return self.subsumes(other.parent)

class TripsRestriction(object):
    def __init__(self, role, restrs, optionality, ont):
        self.__ont = ont
        self.__role = role
        self.__restrs = set()
        for x in restrs:
            if type(x) is list:
                self.__restrs.update(x[2:])
            if type(x) is str:
                self.__restrs.add(x)
        self.__restrs = {x.lower() for x in self.__restrs}
        self.__optionality = optionality

    @property
    def role(self):
        return self.__role.lower()

    @property
    def restrictions(self):
        return [x for x in [self.__ont[r] for r in self.__restrs] if x]

    @property
    def optionality(self):
        return self.__optionality

    def __str__(self):
        return "[:%s %s]".format(self.role, ", ".join(self.restrictions))

    def __repr__(self):
        res = ""
        if self.restrictions:
            res = self.restrictions[0]
        post = ""
        if len(self.restrictions) > 1:
            post = "and {} others".format(len(self.restrictions)-1)
        return "<TripsRestriction :{} {}{}>".format(self.role, res, post)


def load():
    ont = jsontrips.ontology()
    lex = jsontrips.lexicon()
    return Trips(ont, lex)
