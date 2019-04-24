from ..helpers import get_wn_key, Normalize
from ..structures import TripsType
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset

def load(wn_weight=1.0, trips_weight=1.0):
    from ..ontology import load as ld
    return TripsWN(ld(), wn_weight, trips_weight)


class TripsWN:
    # convenience object
    def __init__(self, ontology, wn_weight=1.0, trips_weight=1.0):
        self.ontology = ontology
        self.wn_weight = wn_weight
        self.trips_weight = trips_weight

    def __getattr__(self, attr):
        # see if this object has attr
        # NOTE do not use hasattr, it goes into
        # infinite recurrsion
        if attr in self.__dict__:
            # this object has it
            return getattr(self, attr)
        # proxy to the wrapped object
        return getattr(self.ontology, attr)

    def trips_candidate(self, trips, key):
        if type(trips) is str:
            trips = self.ontology[Normalize.ont_name(trips)]
        paths = self.get_wordnet(key, path=True, fill=True)
        return [p for p in paths if self.type_in_path(trips, p)]

    def type_in_path(self, trips, path):
        for p in path:
            if type(trips) == type(p):
                if trips == p:
                    return True
        return False

    def candidates_for_word_type(self, trips, word, pos):
        ss = wn.synsets(word, pos)
        res = {s: self.trips_candidate(trips, s) for s in ss}
        return {s: t for s, t in res.items() if t}

    def weighted_candidates_for_word_type(self, trips, word, pos):
        trips = self.ontology[Normalize.ont_name(trips)]
        if not trips:
            return []
        return [(s, min([self.path_weight(x, trips) for x in t])) for s, t in self.candidates_for_word_type(trips, word, pos).items()]

    def get_wordnet(self, key, max_depth=-1, path=False, fill=False):
        if fill:
            fill = lambda x: x.path_to_root()
        else:
            fill = lambda x: [x]

        if max_depth == -1:
            max_depth = self.max_wn_depth
        elif max_depth == 0:
            return []
        if type(key) is str:
            key = get_wn_key(key)
        if not key:
            return []
        if key in self._wordnet_index:
            if not path:
                return self._wordnet_index[key][:]
            return [[key]+fill(t) for t in self._wordnet_index[key][:]]
        else:
            paths = [list(reversed(p[max_depth:])) for p in key.hypernym_paths()]
            results = []
            for p in paths:
                for i in range(len(p)):
                    if p[i] in self._wordnet_index:
                        results.extend(
                                [p[:i+1] + fill(t) for t in self._wordnet_index[p[i]][:]]
                                )
            if not path:
                return [x[-1] for x in results]
            return results

    def path_weight(self, path, stop=None):
        if stop and self.type_in_path(stop, path):
            ind = 0
            for i in path:
                if type(i) == type(stop) and i == stop:
                    break
                ind += 1
            path = path[:ind]
        return sum([self.node_weight(p) for p in path])

    def get_lcs(self, node1, node2):
        if node1 == node2:
            return node1
        if type(node1) is TripsType and type(node2) is TripsType:
            return node1.lcs(node2)
        comb = zip(reversed(path1), reversed(path2))

    def node_weight(self, node):
        if type(node) is Synset:
            return self.wn_weight
        elif type(node) is TripsType:
            return self.trips_weight
        elif type(node) is str:
            # maybe I should have the type detector here?
            return self.wn_weight
        return 0
        
