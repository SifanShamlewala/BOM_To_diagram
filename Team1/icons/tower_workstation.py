import svgwrite
from .base_icon import BaseIcon

class TowerWorkstationIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="tower_workstation")
        x = cx - width / 2
        y = cy - height / 2
        
        # Bounding box: 55 × 140px
        # Body: rect(#3A3A3A fill, #222 border, border-radius=3)
        group.add(dwg.rect(insert=(x, y), size=(width, height), rx=3, ry=3, fill='#3A3A3A', stroke='#222222', stroke_width=1))
        
        # Drive bays: 3 horizontal rects(42×10) stacked at top interior, y from top+8, gap=3
        for i in range(3):
            group.add(dwg.rect(insert=(x + (width - 42)/2, y + 8 + i * 13), size=(42, 10), fill='#222222'))
            
        # Power button: circle(r=7, fill=#222, stroke=#666) at (cx, top+55)
        group.add(dwg.circle(center=(cx, y + 55), r=7, fill='#222222', stroke='#666666', stroke_width=1))
        
        # Power LED: circle(r=2.5, fill=#00CC44) at (cx+12, top+55)
        group.add(dwg.circle(center=(cx + 12, y + 55), r=2.5, fill='#00CC44'))
        
        # Vent slots: 5 lines horizontal, width=38, from y=top+75, spaced 6px, stroke=#444
        for i in range(5):
            ly = y + 75 + i * 6
            group.add(dwg.line(start=(cx - 19, ly), end=(cx + 19, ly), stroke='#444444', stroke_width=1))
            
        # Label: "OWS" at (cx, bottom+12), font-size=9
        if not label:
            label = "OWS"
        group.add(dwg.text(label, insert=(cx, y + height + 12), text_anchor="middle", font_size=9, font_family="sans-serif", fill='#000000'))
        
        return group
