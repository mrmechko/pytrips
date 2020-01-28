from ..helpers import get_wn_key, all_hyponyms
from anytree import NodeMixin, RenderTree
import json


class AbstractTripsType(object):
    pass

class TripsType(AbstractTripsType, NodeMixin):
    """
    Note: in order for the operations to work, at least one of the
    types must explicitly be a TripsType
    type: t, str: s
    equality: t1 == t2, t1 == s
    subsumption: t1 < t2, s1 < t2, t1 < s2
    lcs: t1 ^ t2, s1 ^ t2, t1 ^ s2

    # WARNING: arguments are currently not loaded.  There is a raw dict there
    """

    def __init__(self, name, parent, children, words, wordnet, arguments, sem, definitions, ont):
        self.__name = name.lower()
        if parent:
            self.__parent = parent.lower()
        else:
            self.__parent = None
        self.__children = children
        self.__arguments = arguments
        self.__sem = sem
        self.__words = [w.lower() for w in words]
        self.__wordnet = [w.lower() for w in wordnet]
        self.__wordnet_keys = None
        self.__definitions = json.loads(json.dumps(definitions))
        self.__ont = ont
        # TODO: set numerical id

    def subtree_string(self, max_depth=1000):
        return "\n".join(["%s%s" % (a, c.name) for a, b, c in RenderTree(self, maxlevel=max_depth)])

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
    def sem(self):
        return self.__sem

    @property
    def definitions(self):
        return self.__definitions[:]

    @property
    def words(self):
        return self.__words[:]

    def wordnet_closure(self, max_depth=-1, pos=None):
        if max_depth == -1:
            max_depth = self.__ont.max_wn_depth
        clsr = set([k for k in self.wordnet_keys if k.pos() == pos or not pos])
        for key in self.wordnet_keys:
            ext = list(key.closure(lambda s: [t for t in all_hyponyms(s) if self in self.__ont[t]], depth=max_depth))
            clsr.update(ext)
        return clsr

    def word_closure(self, max_depth=3, pos=None):
        clsr = self.wordnet_closure(max_depth=max_depth, pos=pos)
        words = set()
        for key in clsr:
            words.update([w.name() for w in key.lemmas()])
        return words

    def is_a_closure(self, max_depth=3, pos=None):
        clsr = self.word_closure(max_depth, pos=pos)
        for c in self.children:
            clsr.update(c.is_a_closure(max_depth))
        return clsr

    @property
    def wordnet(self):
        return self.__wordnet[:]

    @property
    def wordnet_keys(self):
        if self.__wordnet_keys is None:
            self.__wordnet_keys = [get_wn_key(s) for s in self.__wordnet if get_wn_key(s)]
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
            return False

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

    def path_len(self, other):
        return self.depth + other.depth - 2*(self ^ other).depth

    def wup(self, other):
        lcsd = (self ^ other).depth
        return 2 * lcsd/(self.depth + other.depth)

    def cosine(self, other):
        import math
        if not other:
            return 0
        lcsd = (self ^ other).depth
        return lcsd / math.sqrt(self.depth * other.depth)

    def __xor__(self, other):
        return self.lcs(other)

    def subsumes(self, other, max_depth=-1, significant=False):
        """messing with a method this fundamental is dangerous.  
           Guarantee - node never changes, we only abstract out other"""
        node = self
        if significant:
            node = self.significant()
            other = other.significant()
            if node == other:
                return False # they are in the same class, so no subsumption
        if not other:
            return False # Is this a good idea?
        if other == "ont::root":
            return False
        elif significant and other in node.significant_children():
            return True
        elif not significant and other in node.children:
            return True
        elif max_depth == 0:
            return False
        elif significant:
            return node.subsumes(other.significant_parent(), max_depth=max_depth-1)
        else:
            return node.subsumes(other.parent, max_depth=max_depth-1)

    def differs_semantically_from(self, other):
        if self.sem.differs_from(other.sem):
            return True
        argset = set([str(x) for x in self.arguments])
        argset2 = set([str(x) for x in other.arguments])
        return argset != argset2

    def significant_parent(self):
        """returns next significant ancestor"""
        if self == "ont::root":
            return self
        return self.parent.significant()

    def significant(self):
        """returns next significant node on path to root, including self"""
        if self == "ont::root":
            return self
        if self.differs_semantically_from(self.parent):
            return self
        return self.parent.significant()

    def significant_ancestors(self):
        """returns all significant ancestors"""
        if self == "ont::root":
            return []
        if self.differs_semantically_from(self.parent):
            return [self] + self.parent.significant_ancestors()
        return self.parent.significant_ancestors()

    def significant_children(self):
        """return significant immediate children"""
        return [c for c in self.children if c and self.differs_semantically_from(c)]

    def significant_descendants(self):
        """return all significant descendants"""
        if not self.children:
            return []
        return sum([c.significant_descendants() for c in self.children], self.significant_children())

