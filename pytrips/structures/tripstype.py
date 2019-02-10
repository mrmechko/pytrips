from ..helpers import get_wn_key


class TripsType(object):
    """
    Note: in order for the operations to work, at least one of the
    types must explicitly be a TripsType
    type: t, str: s
    equality: t1 == t2, t1 == s
    subsumption: t1 < t2, s1 < t2, t1 < s2
    lcs: t1 ^ t2, s1 ^ t2, t1 ^ s2

    # WARNING: arguments are currently not loaded.  There is a raw dict there
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

    def wordnet_closure(self, max_depth=-1, pos=None):
        if max_depth == -1:
            max_depth = self.__ont.max_wn_depth
        clsr = set([k for k in self.wordnet_keys if pos and k.pos() == pos])
        for key in self.wordnet_keys:
            ext = list(key.closure(lambda s: [t for t in s.hyponyms() if self in self.__ont[t]], depth=max_depth))
            clsr.update(ext)
        return clsr

    def word_closure(self, max_depth=3, pos=None):
        clsr = self.wordnet_closure(max_depth=max_depth, pos=pos)
        words = set()
        for key in clsr:
            words.update([w.name() for w in key.lemmas()])
        return words

    def is_a_closure(self, max_depth=3):
        clsr = self.word_closure(max_depth)
        for c in self.children:
            clsr.update(c.is_a_closure(max_depth))
        return clsr

    @property
    def wordnet(self):
        return self.__wordnet[:]

    @property
    def wordnet_keys(self):
        return self.__wordnet_keys[:]

    def __eq__(self, other):
        # XXX: does this cause problems with putting things in sets?
        if not other:
            return False
        elif type(other) is TripsType:
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
        if not other:
            return False # Is this a good idea?
        if other == "ont::root":
            return False
        elif other in self.children:
            return True
        else:
            return self.subsumes(other.parent)
