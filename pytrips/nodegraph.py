from .structures import TripsRestriction, TripsType, TripsSem
from .helpers import wn, get_wn_key
from nltk.corpus.reader.wordnet import Synset
#import re
from graphviz import Digraph



class NodeGraph:
    def __init__(self, default_node_attr=None, default_edge_attr=None):
        self.nodes = {}
        self.node_attrs = {}
        self.edge_attrs = {}
        self.edges = set()
        self.default_node_attr = {}
        if default_node_attr:
            self.default_node_attr = default_node_attr
        self.default_edge_attr = {}
        if default_edge_attr:
            self.default_edge_attr = default_edge_attr

    def get_nth_label(self, n):
        if n < 26:
            return _string.ascii_uppercase[n]
        return self.get_nth_label(n // 26) + self.get_nth_label(n % 26)

    def get_label(self, name):
        #res = get_wn_key(name.split("::")[-1])
        #if res:
        #    return res.name()
        return name.lower()

    def escape_label(self, s):
        if not s:
            return ""
        if type(s) is str:
            return "w::"+s
        if type(s) is Synset:
            return "wn::"+s.lemmas()[0].key().lower()#.replace("%", ".")
        if type(s) is TripsType:
            return "ont::"+s.name
        return "any::"+str(s)

    def escape_dot(self, x):
        return x.replace(":", "_").replace("%", ".")

    def node(self, name, attrs=None):
        name = self.escape_label(name)
        if name in self.nodes:
            return
        label = self.get_label(name)
        self.nodes[name] = label
        if attrs:
            self.node_attrs[name] = attrs

    def edge(self, source, target, label="", attrs=None):
        e = (self.escape_label(source), 
                    self.escape_label(target), 
                        self.escape_label(label))
        self.edges.add(e)
        if attrs:
            self.edge_attrs[e] = attrs

    def graph(self, format='svg'):
        graph = Digraph(format=format)
        for l, t in self.nodes.items():
            over = self.node_attrs.get(t, self.default_node_attr)
            attrs = {"shape": "rectangle"}
            if t.startswith("w::"):
                t = t[3:]
                attrs["shape"] = "diamond"
                attrs["style"] = "filled"
                attrs["fillcolor"] = "lightgray"
            elif t.startswith("wn::"):
                t = t[4:]
                attrs["shape"] = "oval"
                attrs["tooltip"] = get_wn_key(t).definition()
            elif t.startswith("ont::"):
                attrs["style"] = "filled"
                attrs["fillcolor"] = "lightblue"
            for a, v in over.items():
                attrs[a] = v
            graph.node(self.escape_dot(l), t, **attrs)
        for s, t, l in self.edges:
            a = self.edge_attrs.get((s,t,l), self.default_edge_attr)
            s, t = self.nodes[s], self.nodes[t]
            if l:
                graph.edge(self.escape_dot(s), self.escape_dot(t), l, **a)
            else:
                graph.edge(self.escape_dot(s), self.escape_dot(t), **a)
        return graph

    def source(self):
        return self.graph().source

    def json(self):
        elements = []
        for label, name in self.nodes.items():
            elements.append({"data": {"id": name, "label": label}})
        for source, target, label in self.edges:
            source = self.nodes[source]
            target = self.nodes[target]
            edge = {"data": {"source": source, "target": target}}
            if label:
                edge["data"]["label"] = label
            elements.append(edge)
        return elements
