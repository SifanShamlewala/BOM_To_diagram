import json
import networkx as nx
import matplotlib.pyplot as plt

with open("graph.json") as f:
    data = json.load(f)

G = nx.DiGraph()

for node in data["nodes"]:
    G.add_node(node["id"], label=node.get("label", node["id"]))

for edge in data["edges"]:
    G.add_edge(edge["from"], edge["to"], label=edge.get("type", ""))

nx.draw(G, with_labels=True)
plt.show()
