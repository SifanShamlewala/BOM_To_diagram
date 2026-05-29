import svgwrite
from .base_icon import BaseIcon

class CharmBaseplateIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="charm_baseplate")
        x = cx - width / 2
        y = cy - height / 2
        
        # Bounding box: TOWER_WIDTH × 18px
        fill_color = '#303030' if label == "alt" else '#2A2A2A'

        # Body: rect(alternating fill: even=#2A2A2A, odd=#303030)
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill=fill_color))
        
        # Left tab: rect(w=5, full height, fill=#4488CC or #44AACC alternating per column)
        group.add(dwg.rect(insert=(x, y), size=(5, height), fill='#4488CC'))
        
        # 8 tiny slot divisions: horizontal lines every 2px from top (subtle, #444)
        for i in range(1, 9):
            group.add(dwg.line(start=(x + 10, y + i * 2), end=(x + width - 5, y + i * 2), stroke='#444444', stroke_width=0.5))
            
        # Right edge: thin highlight line (#3A3A3A)
        group.add(dwg.line(start=(x + width - 1, y), end=(x + width - 1, y + height), stroke='#3A3A3A', stroke_width=1))
        
        return group
