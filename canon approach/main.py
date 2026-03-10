from archEngine import ArchitectureEngine
from layoutEngine import LayoutEngine
from pptRenderer import PptRenderer
import json


with open('handmade_demo.json', 'r') as file:
    SEMANTIC_JSON = json.load(file)

engine = ArchitectureEngine()
architecture = engine.build(SEMANTIC_JSON)

l_engine = LayoutEngine()
layout = l_engine.build(architecture)

renderer = PptRenderer()
renderer.render(layout, "deltav_architecture.pptx")