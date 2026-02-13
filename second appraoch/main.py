import json
from layout_engine import LayoutEngine
from ppt_renderer import PptRenderer
from link_filter import filter_render_links

arch = json.load(open("arch.json"))

# Build device -> enclosure map
device_to_enclosure = {}
for encl in arch["enclosures"]:
    for d in encl["devices"]:
        device_to_enclosure[d] = encl["id"]

# Layout
engine = LayoutEngine()
engine.layout_rooms(arch["rooms"])
engine.layout_enclosures(arch["rooms"], arch["enclosures"])
# engine.layout_devices(arch["enclosures"], arch["devices"])

# Filter links
render_links = filter_render_links(
    arch["links"],
    device_to_enclosure
)

# Render
renderer = PptRenderer()

for room in arch["rooms"]:
    renderer.draw_room(room)

for encl in arch["enclosures"]:
    renderer.draw_enclosure(encl)

# for dev in arch["devices"]:
#     renderer.draw_device(dev)

# Draw only cross-boundary links
# dev_by_id = {d["id"]: d for d in arch["devices"]}
# for link in render_links:
#     renderer.draw_link(
#         dev_by_id[link["from"]],
#         dev_by_id[link["to"]]
#     )

renderer.save("output.pptx")
