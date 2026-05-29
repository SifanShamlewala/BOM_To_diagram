import svgwrite
from .base_icon import BaseIcon

class EmptyTowerSlotIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="empty_tower_slot")
        x = cx - width / 2
        y = cy - height / 2
        
        # Body: rect(fill=#1A1A1A)
        rect = dwg.rect(insert=(x, y), size=(width, height), fill='#1A1A1A', stroke='#555555', stroke_width=1)
        rect['stroke-dasharray'] = "4,3"
        group.add(rect)
        
        # Optional diagonal hatching: 4 lines from corners, stroke=#2A2A2A, stroke_width=1
        group.add(dwg.line(start=(x, y), end=(x + width, y + height), stroke='#2A2A2A', stroke_width=1))
        group.add(dwg.line(start=(x + width, y), end=(x, y + height), stroke='#2A2A2A', stroke_width=1))
        
        return group
