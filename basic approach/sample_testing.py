import json
import networkx as nx
from networkx.drawing.nx_pydot import to_pydot

with open("graph1.json") as f:
    data = json.load(f)

G = nx.DiGraph()

for node in data["nodes"]:
    G.add_node(node["id"], label=node.get("label", node["id"]))

for edge in data["edges"]:
    G.add_edge(edge["from"], edge["to"], label=edge.get("type", ""))

dot = to_pydot(G)
dot.write_png("bom_structure1.png")
