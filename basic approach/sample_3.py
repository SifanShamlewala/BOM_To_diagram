from graphviz import Digraph

dot = Digraph(engine="dot")

for n in G.nodes():
    dot.node(n, n)

for u, v in G.edges():
    dot.edge(u, v)

dot.render("bom_structure", format="png", cleanup=True)