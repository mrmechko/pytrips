from .structures import TripsRestriction, TripsType, TripsSem
from .helpers import wn, get_wn_key
from nltk.corpus.reader.wordnet import Synset
#import re
from graphviz import Digraph



class NodeGraph:
    def __init__(self, default_node_attr=None, default_edge_attr=None, no_escape=False, subgraphs=None, name="graph", attrs=None, label=None):
        self.name = name
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
        self.no_escape = no_escape
        self.subgraphs = []
        if subgraphs:
            self.subgraphs = subgraphs
        self.attrs = {}
        if attrs:
            self.attrs = attrs
        if label:
            self.attrs["label"] = label

    def get_nth_label(self, n):
        if n < 26:
            return _string.ascii_uppercase[n]
        return self.get_nth_label(n // 26) + self.get_nth_label(n % 26)

    def get_label(self, name):
        #res = get_wn_key(name.split("::")[-1])
        #if res:
        #    return res.name()
        return name.lower()

    def add_subgraph(self, sg):
        self.subgraphs.append(sg)

    def escape_label(self, s):
        if self.no_escape:
            return s
        if not s:
            return ""
        if type(s) is str and (s.startswith("w::") or s.startswith("wn::") or s.startswith("ont::")):
            # already namespaced
            return s
        if type(s) is str:
            return "w::"+s
        if type(s) is Synset:
            return "wn::"+s.lemmas()[0].key().lower()#.replace("%", ".")
        if type(s) is TripsType:
            return "ont::"+s.name
        return "any::"+str(s)

    def escape_dot(self, x):
        if self.no_escape:
            return x
        return x.replace(":", "_").replace("%", ".")

    def node(self, name, attrs=None, label=None):
        name = self.escape_label(name)
        if name in self.nodes:
            return
        if not label: 
            label = name
        self.nodes[name] = label
        if attrs:
            self.node_attrs[name] = attrs

    def edge(self, source, target, label="", attrs=None, port=None, noloop=False):
        #print(self.edges, self.nodes.keys())
        #print(source, target, label)
        source = self.escape_label(source)
        target = self.escape_label(target)
        if noloop and source == target:
            return
        e = (source, target, self.escape_label(label))
        self.edges.add(e)
        if attrs:
            self.edge_attrs[e] = attrs

    def graph(self, format='svg', attrs={}):
        attrs = dict(self.attrs, **attrs)
        attrs["compound"] = "true"
        if 'rankdir' not in attrs:
            attrs["rankdir"] = "LR"
        graph = Digraph(format=format, name=self.name) 
        graph.attr(**attrs)
        for l, t in self.nodes.items():
            attrs = dict(self.default_node_attr)
            over = self.node_attrs.get(l, {})
            if t.startswith("w::"):
                t = t[3:]
                attrs["shape"] = "diamond"
                attrs["style"] = "filled"
                attrs["fillcolor"] = "lightgray"
            elif t.startswith("wn::"):
                t = t[4:]
                if not "shape" in attrs:
                    attrs["shape"] = "oval"
                attrs["tooltip"] = get_wn_key(t).definition()
            elif t.startswith("ont::"):
                attrs["style"] = "filled"
                attrs["fillcolor"] = "lightblue"
                attrs["href"] = "https://www.cs.rochester.edu/research/trips/lexicon/data/%s.xml" % t.replace("ont::", "ONT%3A%3A")
                attrs["target"] = "_none"
            attrs = dict(attrs, **over)
            #print(l, t, attrs, over)
            graph.node(self.escape_dot(l), t, **attrs)
        # Add subgraphs before edges
        for sg in self.subgraphs:
            sg = sg.graph()
            #print("sg name:", sg.name)
            graph.subgraph(graph=sg)
        for s, t, l in self.edges:
            #print(s, t, l)
            a = self.edge_attrs.get((s,t,l), self.default_edge_attr)
            #s, t = self.nodes[s], self.nodes[t]
            #print(self.escape_dot(s), "->", self.escape_dot(t))
            if l:
                graph.edge(self.escape_dot(s), self.escape_dot(t), l, **a)
            else:
                graph.edge(self.escape_dot(s), self.escape_dot(t), **a)
        #print(graph.source)
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


def type_to_dot(onttype):
    G = NodeGraph(no_escape=True, name="ont_"+onttype.name, attrs=dict(rankdir="TB", layout="fdp"), default_node_attr=dict(shape="plain"))
    root = "ont_" + onttype.name
    G.node(root, label=onttype.name)

    # parent
    G.node("parent", label=onttype.parent.name)
    G.edge("parent", root, label="parent")

    words = NodeGraph(no_escape=True, name="cluster_words", attrs=dict(mindist="0.2"), default_node_attr=dict(shape="plain", mindist="0.2"), default_edge_attr=dict(style="invis"))
    words.node("word_root", label=" ")

    wordnet = NodeGraph(no_escape=True, name="cluster_wordnet", default_node_attr=dict(shape="plain"), default_edge_attr=dict(style="invis"))
    wordnet.node("wordnet_root", label=" ", attrs=dict(shape="plain"))

    for i, w in enumerate(onttype.words):
        words.node("word_%d" % i, label=w)
        words.edge("word_root", "word_%d" % i, label="", attrs=dict())


    for i, w in enumerate(onttype.wordnet):
        wordnet.node("wn_%d" % i, label=w)

    G.add_subgraph(words)
    G.edge(root, "word_root", attrs=dict(ltail=root, lhead="cluster_words"))
    G.add_subgraph(wordnet)
    G.edge(root, "wordnet_root", attrs=dict(ltail=root, lhead="cluster_wordnet"))

    feats = list(onttype.sem.sem.keys())
    feat_str = "{ %s } | { %s }" % (" | ".join(feats), " | ".join([onttype.sem.sem[f] for f in feats]))
    G.node("features", label=feat_str, attrs=dict(shape="record"))
    G.edge(root, "features", label="features")
    
    return G.graph()
